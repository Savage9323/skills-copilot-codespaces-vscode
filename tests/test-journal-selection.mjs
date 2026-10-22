import { test } from "node:test"
import assert from "node:assert/strict"
import { mkdtemp, mkdir, writeFile, rm, utimes } from "node:fs/promises"
import os from "node:os"
import path from "node:path"
import { selectRecentJournals } from "../opencode-plugins/savage-auto-memory/journal-selection.js"

async function fixture(fn) {
 const base=await mkdtemp(path.join(os.tmpdir(),"savage-journal-selection-"))
 const scope={authorized:true,id:"fixture-sbi",root:"/repos/sbi"}
 const roots=[path.join(base,"recent"),path.join(base,"recent-v2")]
 for(const r of roots)await mkdir(path.join(r,scope.id),{recursive:true})
 try{return await fn({base,scope,roots})}finally{await rm(base,{recursive:true,force:true})}
}
async function write(root,scope,id,options={}) {
 const data={source:"test",project:scope.id,workspace_root:scope.root,session_id:id,
   captured_at:options.time || "2026-10-22T06:00:00Z",
   snippets:[{role:"user",text:"We decided to keep verified history."}]}
 if(options.project)data.project=options.project
 if(options.root)data.workspace_root=options.root
 if(options.migration){data.schema_version=2;data.status="legacy-unverified-reference";data.legacy_migration={
  original_sha256:"a".repeat(64),verification:"OpenCode read-only session_v2 and project.worktree"}}
 const file=path.join(root,scope.id,id+".json")
 await writeFile(file,JSON.stringify(data),{mode:0o600})
 return file
}
const now=Date.parse("2026-10-22T07:00:00Z")
test("invalid newer journals cannot hide older valid entry",async()=>fixture(async({scope,roots})=>{
 await write(roots[0],scope,"older_valid",{time:"2026-10-21T23:00:00Z"})
 for(let i=1;i<=4;i++)await write(roots[0],scope,"newer_invalid"+i,{project:"another-project",time:`2026-10-22T06:0${i}:00Z`})
 const selected=await selectRecentJournals(scope,"no_session",roots,{now})
 assert.deepEqual(selected.map(x=>x.id),["older_valid"])
}))
test("malformed and expired journals excluded before limit",async()=>fixture(async({scope,roots})=>{
 await write(roots[0],scope,"good")
 await write(roots[0],scope,"expired",{time:"2025-01-01T00:00:00Z"})
 await writeFile(path.join(roots[0],scope.id,"broken.json"),"{invalid")
 const items=await selectRecentJournals(scope,"none",roots,{now})
 assert.deepEqual(items.map(x=>x.id),["good"])
}))
test("project and workspace provenance both enforced",async()=>fixture(async({scope,roots})=>{
 await write(roots[0],scope,"good")
 await write(roots[0],scope,"wrong_root",{root:"/repos/another"})
 await write(roots[0],scope,"wrong_project",{project:"not-sbi"})
 assert.deepEqual((await selectRecentJournals(scope,"none",roots,{now})).map(x=>x.id),["good"])
}))
test("migrated history can be selected without overwriting originals",async()=>fixture(async({scope,roots})=>{
 await write(roots[1],scope,"old_session",{migration:true})
 const selected=await selectRecentJournals(scope,"none",roots,{now})
 assert.equal(selected.length,1)
 assert.equal(selected[0].data.status,"legacy-unverified-reference")
}))
test("a valid current journal ranks before older ones",async()=>fixture(async({scope,roots})=>{
 await write(roots[0],scope,"current",{time:"2026-10-21T20:00:00Z"})
 for(let i=0;i<6;i++)await write(roots[0],scope,"other"+i,{time:"2026-10-22T06:00:00Z"})
 const selected=await selectRecentJournals(scope,"current",roots,{now})
 assert.equal(selected.length,4)
 assert.equal(selected[0].id,"current")
}))
test("legacy unknown-role snippets are excluded without rejecting verified user history",async()=>fixture(async({scope,roots})=>{
 const file=await write(roots[1],scope,"mixed",{migration:true})
 const data=JSON.parse(await (await import("node:fs/promises")).readFile(file,"utf8"))
 data.snippets.push({role:"unknown",text:"Untrusted transport trace"})
 await writeFile(file,JSON.stringify(data))
 const items=await selectRecentJournals(scope,"none",roots,{now})
 assert.equal(items.length,1)
 assert.deepEqual(items[0].data.snippets.map(x=>x.role),["user"])
}))
test("all unknown role snippets are excluded entirely",async()=>fixture(async({scope,roots})=>{
 const file=await write(roots[1],scope,"only_unknown",{migration:true})
 const data=JSON.parse(await (await import("node:fs/promises")).readFile(file,"utf8"))
 data.snippets=[{role:"unknown",text:"Should not be injected"}]
 await writeFile(file,JSON.stringify(data))
 const items=await selectRecentJournals(scope,"none",roots,{now})
 assert.equal(items.length,0)
}))
test("unregistered projects get no private history",async()=>fixture(async({scope,roots})=>{
 await write(roots[0],scope,"good")
 assert.deepEqual(await selectRecentJournals({...scope,authorized:false},"none",roots,{now}),[])
}))
