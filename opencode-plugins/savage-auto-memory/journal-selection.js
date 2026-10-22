/** Read and validate all journal candidates before selecting a small recent subset. */
import path from "node:path"
import { promises as fs } from "node:fs"
import { safeSessionId, validateJournal } from "./memory-boundaries.js"

export async function selectRecentJournals(scope, currentSessionId, roots, {
  limit = 4, maxAgeDays = 90, now = Date.now(),
} = {}) {
  safeSessionId(currentSessionId)
  if (!scope?.authorized) return []
  const valid = new Map()
  for (const root of roots) {
    const directory = path.join(root, scope.id)
    let names = []
    try {
      const st = await fs.lstat(directory)
      if (!st.isDirectory() || st.isSymbolicLink()) continue
      names = await fs.readdir(directory)
    } catch { continue }
    for (const name of names) {
      if (!name.endsWith(".json")) continue
      const id = name.slice(0, -5)
      try {
        safeSessionId(id)
        const full = path.join(directory, name)
        const stat = await fs.lstat(full)
        if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 1_000_000) continue
        const data = JSON.parse(await fs.readFile(full, "utf8"))
        if (!validateJournal(data, scope, id)) continue
        if (data.schema_version === 2 && data.status === "legacy-unverified-reference") {
          if (!/^[a-f0-9]{64}$/i.test(data.legacy_migration?.original_sha256 || "")) continue
          if (data.legacy_migration?.verification !== "OpenCode read-only session_v2 and project.worktree") continue
        }
        if (!Array.isArray(data.snippets)) continue
        // Historical journals can include role=unknown tool/transport fragments.
        // Preserve the immutable source but exclude those fragments from injection.
        const validSnippets = data.snippets.filter(x => x && typeof x === "object" &&
          ["user", "assistant"].includes(x.role) && typeof x.text === "string")
        if (!validSnippets.length) continue
        const timestamp = Date.parse(data.captured_at)
        if (!Number.isFinite(timestamp) || timestamp > now + 5 * 60_000 ||
            timestamp < now - maxAgeDays * 86_400_000) continue
        const candidate = { data: { ...data, snippets: validSnippets }, full, id,
          current: id === currentSessionId, time: timestamp }
        const old = valid.get(id)
        if (!old || candidate.time > old.time ||
            (candidate.time === old.time && !candidate.data.legacy_migration && old.data.legacy_migration)) {
          valid.set(id, candidate)
        }
      } catch { /* malformed, expired, wrong-project journals are ignored */ }
    }
  }
  // Important: filter invalid candidates BEFORE taking the four newest.
  return [...valid.values()]
    .sort((a, b) => Number(b.current) - Number(a.current) || b.time - a.time)
    .slice(0, limit)
}
