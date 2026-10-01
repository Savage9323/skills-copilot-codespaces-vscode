import { Plugin } from "@opencode/plugin"
import { promises as fs } from "node:fs"
import path from "node:path"
import os from "node:os"

const HOME = os.homedir()
const MEMORY_ROOT = process.env.OPENCODE_MEMORY_DIR || path.join(HOME, ".config", "opencode", "memory")
const MAX_CANONICAL_CHARS = 22000
const MAX_RECENT_CHARS = 8000
const MAX_ITEM_CHARS = 4000

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
  return out.length > MAX_ITEM_CHARS ? out.slice(0, MAX_ITEM_CHARS) + "\n[TRUNCATED]" : out
}

function projectSlug(directory) {
  return path.basename(directory || "unknown-project")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "") || "unknown-project"
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
  if (/(tool|reasoning|analysis|attachment|file|metadata|step)/.test(type)) return out

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
    if (node[key] && typeof node[key] !== "string") collectText(node[key], out, depth + 1)
  }

  return out
}

async function saveRecentSession(directory, sessionID, ctx) {
  const slug = projectSlug(directory)
  const dir = path.join(MEMORY_ROOT, "recent", slug)
  await fs.mkdir(dir, { recursive: true })

  const context = await ctx.session.context({ sessionID })
  const snippets = collectText(context)
    .filter((item, index, arr) => index === 0 || item.text !== arr[index - 1].text)
    .slice(-30)

  const payload = {
    source: "opencode-v2-auto-memory",
    project: slug,
    session_id: sessionID,
    captured_at: new Date().toISOString(),
    status: "recent-conversation-recollection",
    warning: "Recent conversation memory is context, not canonical truth. Verify consequential facts live.",
    snippets,
  }

  const target = path.join(dir, sessionID + ".json")
  const temp = target + ".tmp"
  await fs.writeFile(temp, JSON.stringify(payload, null, 2) + "\n", { mode: 0o600 })
  await fs.rename(temp, target)
}

async function loadRecentSessions(directory, currentSessionID) {
  const slug = projectSlug(directory)
  const dir = path.join(MEMORY_ROOT, "recent", slug)

  let files = []
  try {
    files = await fs.readdir(dir)
  } catch {
    return ""
  }

  const entries = []
  for (const name of files.filter((n) => n.endsWith(".json") && n !== currentSessionID + ".json")) {
    try {
      const full = path.join(dir, name)
      const stat = await fs.stat(full)
      entries.push({ full, mtime: stat.mtimeMs })
    } catch {}
  }

  entries.sort((a, b) => b.mtime - a.mtime)

  const chunks = []
  for (const entry of entries.slice(0, 3)) {
    try {
      const data = JSON.parse(await fs.readFile(entry.full, "utf8"))
      const lines = (data.snippets || [])
        .slice(-12)
        .map((item) => `${item.role || "unknown"}: ${redactString(item.text || "")}`)
        .filter(Boolean)

      if (lines.length) {
        chunks.push(
          `Recent OpenCode session ${data.session_id || path.basename(entry.full, ".json")} (${data.captured_at || "unknown time"}):\n` +
          lines.join("\n")
        )
      }
    } catch {}
  }

  let text = chunks.join("\n\n")
  if (text.length > MAX_RECENT_CHARS) text = text.slice(0, MAX_RECENT_CHARS) + "\n[RECENT MEMORY TRUNCATED]"
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
    canonical = canonical.slice(0, MAX_CANONICAL_CHARS) + "\n[CANONICAL MEMORY TRUNCATED]"
  }

  const recent = await loadRecentSessions(directory, sessionID)

  return [
    "# Shared model-independent memory",
    "Live repository/runtime/provider state outranks all memory.",
    "Canonical memory below contains durable project context.",
    "Recent-conversation memory is only recollection from earlier OpenCode sessions and may be stale or wrong.",
    "Never copy secret values into memory or prompts.",
    canonical,
    recent ? "## Recent OpenCode conversation memory\n" + recent : "## Recent OpenCode conversation memory\nNo prior captured OpenCode session memory found for this project.",
  ].join("\n\n")
}

function isProtectedPath(filePath) {
  const normalized = String(filePath || "").replace(/\\/g, "/")
  const base = path.basename(normalized)
  if (base === ".env" || (base.startsWith(".env.") && ![".env.example", ".env.sample", ".env.template"].includes(base))) return true
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

    await ctx.session.hook("context", async (event) => {
      const memory = await buildMemoryContext(directory, event.sessionID)
      event.system.push({ type: "text", text: memory })
    })

    await ctx.session.hook("compaction", async (event) => {
      const memory = await buildMemoryContext(directory, event.sessionID)
      event.system.push({ type: "text", text: memory })
    })

    await ctx.tool.hook("execute.before", async (event) => {
      if (event.tool !== "read") return
      const filePath = event.input?.filePath || event.input?.path
      if (isProtectedPath(filePath)) {
        throw new Error("Protected secret file: use the secret-vault runtime injection workflow instead of reading secret values into the model.")
      }
    })

    void (async () => {
      for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
        if (event.type !== "session.idle") continue
        const sessionID = event?.properties?.sessionID
        if (!sessionID) continue

        try {
          await saveRecentSession(directory, sessionID, ctx)
        } catch {}
      }
    })()

    return () => controller.abort()
  },
})
