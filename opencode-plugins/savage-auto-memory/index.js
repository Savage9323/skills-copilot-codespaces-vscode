import { Plugin } from "@opencode/plugin"
import { promises as fs } from "node:fs"
import path from "node:path"
import os from "node:os"

const HOME = os.homedir()
const MEMORY_ROOT =
  process.env.OPENCODE_MEMORY_DIR ||
  path.join(HOME, ".config", "opencode", "memory")
const PRIVATE_STATE_ROOT =
  process.env.SAVAGE_MEMORY_STATE_DIR ||
  path.join(HOME, ".local", "share", "savage-agent-memory")

const MAX_CANONICAL_CHARS = 22000
const MAX_RECENT_CHARS = 10000
const MAX_ITEM_CHARS = 4000
const MAX_JOURNAL_SNIPPETS = 60

const secretPatterns = [
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/gi,
  /\bgh[pousr]_[A-Za-z0-9_]{20,}\b/g,
  /\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b/g,
  /\bAKIA[0-9A-Z]{16}\b/g,
  /\b(?:BWS_ACCESS_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|SUPABASE_SERVICE_ROLE_KEY|AZURE_CLIENT_SECRET|CLOUDFLARE_API_TOKEN)\s*[=:]\s*[^\s"'\\]+/gi,
]

function redactString(value) {
  let out = String(value)
  for (const pattern of secretPatterns) out = out.replace(pattern, "[REDACTED]")
  if (out.length > MAX_ITEM_CHARS) {
    out = out.slice(0, MAX_ITEM_CHARS) + "\n[TRUNCATED]"
  }
  return out
}

function projectSlug(directory) {
  return (
    path
      .basename(directory || "unknown-project")
      .toLowerCase()
      .replace(/[^a-z0-9._-]+/g, "-")
      .replace(/^-+|-+$/g, "") || "unknown-project"
  )
}

async function readText(file) {
  try {
    return await fs.readFile(file, "utf8")
  } catch {
    return ""
  }
}

function collectText(node, out = [], depth = 0) {
  if (depth > 12 || node == null) return out

  if (Array.isArray(node)) {
    for (const item of node) collectText(item, out, depth + 1)
    return out
  }

  if (typeof node !== "object") return out

  const type = String(node.type || "").toLowerCase()
  if (/(tool|reasoning|analysis|attachment|file|metadata|step)/.test(type)) {
    return out
  }

  const role = typeof node.role === "string" ? node.role.toLowerCase() : ""

  if (["user", "assistant"].includes(role)) {
    if (typeof node.text === "string" && node.text.trim()) {
      out.push({ role, text: redactString(node.text.trim()) })
    }
    if (typeof node.content === "string" && node.content.trim()) {
      out.push({ role, text: redactString(node.content.trim()) })
    }
  }

  if (typeof node.text === "string" && node.text.trim() && !role) {
    out.push({ role: "unknown", text: redactString(node.text.trim()) })
  }

  for (const key of ["messages", "parts", "content", "message"]) {
    if (node[key] && typeof node[key] !== "string") {
      collectText(node[key], out, depth + 1)
    }
  }

  return out
}

function dedupeSnippets(items) {
  const result = []
  for (const item of items) {
    if (!item?.text) continue
    const prev = result[result.length - 1]
    if (prev && prev.role === item.role && prev.text === item.text) continue
    result.push({
      role: item.role || "unknown",
      text: redactString(item.text),
    })
  }
  return result.slice(-MAX_JOURNAL_SNIPPETS)
}

function recentDir(directory) {
  return path.join(PRIVATE_STATE_ROOT, "recent", projectSlug(directory))
}

function recentFile(directory, sessionID) {
  return path.join(recentDir(directory), sessionID + ".json")
}

function healthFile() {
  return path.join(PRIVATE_STATE_ROOT, "plugin-health.json")
}

async function updateHealth(patch) {
  await fs.mkdir(PRIVATE_STATE_ROOT, { recursive: true, mode: 0o700 })

  let current = {}
  try {
    current = JSON.parse(await fs.readFile(healthFile(), "utf8"))
  } catch {}

  const next = {
    ...current,
    ...patch,
    updated_at: new Date().toISOString(),
  }

  const temp = healthFile() + ".tmp"
  await fs.writeFile(temp, JSON.stringify(next, null, 2) + "\n", { mode: 0o600 })
  await fs.rename(temp, healthFile())
}

async function readJournal(directory, sessionID) {
  try {
    return JSON.parse(await fs.readFile(recentFile(directory, sessionID), "utf8"))
  } catch {
    return null
  }
}

async function writeJournal(directory, sessionID, incoming, source) {
  if (!sessionID) return

  const snippets = collectText(incoming)
  if (!snippets.length) return

  const dir = recentDir(directory)
  await fs.mkdir(dir, { recursive: true, mode: 0o700 })

  const existing = await readJournal(directory, sessionID)
  const merged = dedupeSnippets([...(existing?.snippets || []), ...snippets])

  const payload = {
    source,
    project: projectSlug(directory),
    session_id: sessionID,
    captured_at: new Date().toISOString(),
    status: "recent-conversation-recollection",
    warning:
      "Private recent-conversation continuity only. Not canonical truth. Verify consequential facts live.",
    snippets: merged,
  }

  const target = recentFile(directory, sessionID)
  const temp = target + ".tmp"
  await fs.writeFile(temp, JSON.stringify(payload, null, 2) + "\n", { mode: 0o600 })
  await fs.rename(temp, target)
}

async function loadRecentConversationMemory(directory, currentSessionID) {
  const dir = recentDir(directory)
  let names = []

  try {
    names = await fs.readdir(dir)
  } catch {
    return ""
  }

  const entries = []
  for (const name of names.filter((name) => name.endsWith(".json"))) {
    try {
      const full = path.join(dir, name)
      const stat = await fs.stat(full)
      entries.push({
        full,
        mtime: stat.mtimeMs,
        current: name === currentSessionID + ".json",
      })
    } catch {}
  }

  entries.sort((a, b) => {
    if (a.current !== b.current) return a.current ? -1 : 1
    return b.mtime - a.mtime
  })

  const chunks = []
  for (const entry of entries.slice(0, 4)) {
    try {
      const data = JSON.parse(await fs.readFile(entry.full, "utf8"))
      let snippets = data.snippets || []

      // The prompt hook captures the current user prompt before context assembly.
      // Do not inject that newest prompt back into the system message for the
      // same dispatch; keep only earlier same-session turns.
      if (
        entry.current &&
        snippets.length > 0 &&
        snippets[snippets.length - 1]?.role === "user"
      ) {
        snippets = snippets.slice(0, -1)
      }

      const lines = snippets
        .slice(entry.current ? -24 : -10)
        .map(
          (item) =>
            `${item.role || "unknown"}: ${redactString(item.text || "")}`,
        )
        .filter(Boolean)

      if (!lines.length) continue

      chunks.push(
        `${entry.current ? "Current-session fallback journal" : "Recent OpenCode session"} ${data.session_id || path.basename(entry.full, ".json")} (${data.captured_at || "unknown time"}):\n` +
          lines.join("\n"),
      )
    } catch {}
  }

  let text = chunks.join("\n\n")
  if (text.length > MAX_RECENT_CHARS) {
    text =
      text.slice(0, MAX_RECENT_CHARS) +
      "\n[RECENT CONVERSATION MEMORY TRUNCATED]"
  }
  return text
}

async function buildMemoryContext(directory, sessionID) {
  const slug = projectSlug(directory)
  const chunks = []

  for (const rel of [
    "PORTFOLIO.md",
    "TOOLCHAIN.md",
    "RESOURCES.md",
    path.join("projects", slug + ".md"),
  ]) {
    const value = await readText(path.join(MEMORY_ROOT, rel))
    if (value) chunks.push("## " + rel + "\n" + value)
  }

  let canonical = chunks.join("\n\n")
  if (canonical.length > MAX_CANONICAL_CHARS) {
    canonical =
      canonical.slice(0, MAX_CANONICAL_CHARS) +
      "\n[CANONICAL MEMORY TRUNCATED]"
  }

  const recent = await loadRecentConversationMemory(directory, sessionID)

  return [
    "# Shared model-independent memory",
    "Live repository/runtime/provider state outranks all memory.",
    "Canonical memory contains durable project context.",
    "The private recent-conversation journal is a continuity fallback because OpenCode session persistence may be incomplete.",
    "Recent conversation recollections may be stale or incomplete and are not canonical truth.",
    "Never copy secret values into memory or prompts.",
    canonical,
    recent
      ? "## Private recent conversation memory\n" + recent
      : "## Private recent conversation memory\nNo captured conversation journal exists yet for this project.",
  ].join("\n\n")
}

function isProtectedPath(filePath) {
  const normalized = String(filePath || "").replace(/\\/g, "/")
  const base = path.basename(normalized)

  if (
    base === ".env" ||
    (base.startsWith(".env.") &&
      ![".env.example", ".env.sample", ".env.template"].includes(base))
  ) {
    return true
  }

  if (/\.(?:pem|p12|pfx|key)$/i.test(base)) return true
  if (/^(?:id_rsa|id_ed25519|id_ecdsa)$/i.test(base)) return true
  if (/credentials(?:\.json)?$/i.test(base)) return true
  return false
}

export default Plugin.define({
  id: "savage-auto-memory",

  async setup(ctx) {
    const directory = ctx.location.directory
    const controller = new AbortController()

    await updateHealth({
      status: "loaded",
      plugin: "savage-auto-memory",
      app_version: ctx.app?.version || "unknown",
      directory,
      loaded_at: new Date().toISOString(),
    })

    // Capture the exact user prompt at admission time. OpenCode documents this
    // hook as running once before durable prompt admission and before model
    // context assembly, making it the most reliable place for continuity.
    await ctx.session.hook("prompt", async (event) => {
      try {
        await writeJournal(
          directory,
          event.sessionID,
          [{ role: "user", text: event.prompt?.text || "" }],
          "opencode-v2-prompt-hook",
        )

        await updateHealth({
          status: "active",
          last_prompt_capture_at: new Date().toISOString(),
          last_prompt_session_id: event.sessionID,
          last_prompt_project: projectSlug(directory),
        })
      } catch (error) {
        await updateHealth({
          status: "prompt-capture-error",
          last_error: String(error),
        })
      }
    })

    await ctx.session.hook("context", async (event) => {
      // Inject the journal that existed before this model dispatch.
      const memory = await buildMemoryContext(directory, event.sessionID)
      event.system.push({ type: "text", text: memory })

      await updateHealth({
        status: "active",
        last_context_hook_at: new Date().toISOString(),
        last_context_session_id: event.sessionID,
        last_context_project: projectSlug(directory),
      })

      // Then persist the current dispatch context. This path runs before the
      // model call and therefore does not depend on OpenCode export or its
      // session database successfully persisting the turn.
      try {
        await writeJournal(
          directory,
          event.sessionID,
          event.messages,
          "opencode-v2-context-hook",
        )
      } catch {}
    })

    await ctx.session.hook("compaction", async (event) => {
      const memory = await buildMemoryContext(directory, event.sessionID)
      event.system.push({ type: "text", text: memory })
    })

    await ctx.tool.hook("execute.before", async (event) => {
      if (event.tool !== "read") return
      const filePath = event.input?.filePath || event.input?.path

      if (isProtectedPath(filePath)) {
        throw new Error(
          "Protected secret file: use the secret-vault runtime injection workflow instead of reading secret values into the model.",
        )
      }
    })

    // Supplemental capture only. The context hook above is the primary
    // persistence path.
    void (async () => {
      for await (const event of ctx.event.subscribe({
        signal: controller.signal,
      })) {
        if (event.type !== "session.idle") continue

        const sessionID = event?.properties?.sessionID
        if (!sessionID) continue

        try {
          const context = await ctx.session.context({ sessionID })
          await writeJournal(
            directory,
            sessionID,
            context,
            "opencode-v2-idle-supplement",
          )
        } catch {}
      }
    })()

    return () => controller.abort()
  },
})
