import { promises as fs } from "node:fs"
import path from "node:path"
import os from "node:os"

const HOME = os.homedir()
const MEMORY_ROOT = process.env.OPENCODE_MEMORY_DIR || path.join(HOME, ".config", "opencode", "memory")
const MAX_CONTEXT_CHARS = 24000
const MAX_STRING_CHARS = 12000

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
  if (out.length > MAX_STRING_CHARS) out = out.slice(0, MAX_STRING_CHARS) + "\n[TRUNCATED]"
  return out
}

function sanitize(value, depth = 0) {
  if (depth > 10) return "[MAX_DEPTH]"
  if (typeof value === "string") return redactString(value)
  if (Array.isArray(value)) return value.slice(0, 400).map((v) => sanitize(v, depth + 1))
  if (!value || typeof value !== "object") return value

  const result = {}
  for (const [key, item] of Object.entries(value)) {
    if (/^(token|password|secret|authorization|cookie|api[_-]?key|private[_-]?key)$/i.test(key)) {
      result[key] = "[REDACTED]"
      continue
    }
    if (/^(stdout|stderr|responseBody)$/i.test(key)) {
      result[key] = "[OMITTED_FROM_MEMORY]"
      continue
    }
    result[key] = sanitize(item, depth + 1)
  }
  return result
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

async function buildMemoryContext(directory) {
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

  let pending = 0
  try {
    const files = await fs.readdir(path.join(MEMORY_ROOT, "inbox"))
    pending = files.filter((name) => name.includes("__" + slug + "__") || name.includes("__" + slug + ".")).length
  } catch {}

  let context = [
    "# Shared model-independent memory",
    "Treat live repository/runtime/provider state as more authoritative than this memory.",
    "Never copy secret values into memory.",
    pending > 0
      ? `There are ${pending} pending candidate memory file(s) for this project. Reconcile relevant candidates with memory-orchestrator before consequential work, without asking the user unless a conflict cannot be resolved safely.`
      : "No pending candidate memory is currently detected for this project.",
    ...chunks,
  ].join("\n\n")

  if (context.length > MAX_CONTEXT_CHARS) {
    context = context.slice(0, MAX_CONTEXT_CHARS) + "\n\n[MEMORY CONTEXT TRUNCATED]"
  }
  return context
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

export const SavageAutoMemoryPlugin = async ({ client, directory }) => {
  return {
    "experimental.chat.system.transform": async (_input, output) => {
      const context = await buildMemoryContext(directory)
      if (!context) return
      if (output.system.length === 0) output.system.push(context)
      else output.system[0] = output.system[0] + "\n\n" + context
    },

    "experimental.session.compacting": async (_input, output) => {
      const context = await buildMemoryContext(directory)
      if (context) output.context.push(context)
    },

    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && isProtectedPath(output?.args?.filePath)) {
        throw new Error("Protected secret file: use the secret-vault runtime injection workflow instead of reading secret values into the model.")
      }
    },

    event: async ({ event }) => {
      const idleEvent =
        event.type === "session.idle" ||
        (event.type === "session.status" && event?.properties?.status?.type === "idle")
      if (!idleEvent) return

      const sessionID = event?.properties?.sessionID
      if (!sessionID) return

      const slug = projectSlug(directory)
      const inbox = path.join(MEMORY_ROOT, "inbox")
      await fs.mkdir(inbox, { recursive: true })

      try {
        const response = await client.session.messages({ path: { id: sessionID } })
        const messages = response?.data ?? response
        const payload = sanitize({
          source: "opencode-auto",
          project: slug,
          captured_at: new Date().toISOString(),
          session_id: sessionID,
          directory,
          status: "candidate",
          note: "Automatically captured on session idle. Candidate evidence only; not canonical truth.",
          messages,
        })

        const finalPath = path.join(inbox, `AUTO__opencode__${slug}__${sessionID}.json`)
        const tempPath = finalPath + ".tmp"
        await fs.writeFile(tempPath, JSON.stringify(payload, null, 2) + "\n", { mode: 0o600 })
        await fs.rename(tempPath, finalPath)
      } catch (error) {
        try {
          await client.app.log({
            body: {
              service: "savage-auto-memory",
              level: "warn",
              message: "Automatic memory capture failed",
              extra: { error: String(error), sessionID },
            },
          })
        } catch {}
      }
    },
  }
}
