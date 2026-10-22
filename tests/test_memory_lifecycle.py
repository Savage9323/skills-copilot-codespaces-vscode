"""No real user journals are accessed by these isolated M2 tests."""
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "memory-lifecycle.py"
spec = importlib.util.spec_from_file_location("savage_m2_lifecycle", SCRIPT)
m2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m2)

class MemoryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.recent = self.base / "recent"
        self.state_root = self.base / "private"
        self.canonical = self.base / "canonical"
        self.project = "fixture-project"
        self.identity_map = self.base / "identities.json"
        self.project_roots = {}

    def journal(self, project, name, snippets, captured=None):
        root = self.recent / project
        root.mkdir(parents=True, exist_ok=True)
        workspace=self.base/"repos"/project
        (workspace/".git").mkdir(parents=True, exist_ok=True)
        self.project_roots[project] = str(workspace.resolve())
        self.identity_map.write_text(json.dumps({"projects":[
            {"id":k,"root":v} for k,v in self.project_roots.items()
        ]}))
        os.chmod(self.identity_map,0o600)
        data = {
            "project": project, "workspace_root": str(workspace.resolve()), "source": "fixture",
            "session_id": name, "captured_at": captured or m2.iso(m2.utcnow()),
            "snippets": snippets,
        }
        (root / (name+".json")).write_text(json.dumps(data))
        return root / (name+".json")

    def scan(self, project=None, days=30):
        project = project or self.project
        state = m2.load_state(self.state_root, project)
        result = m2.scan(state, self.recent, project, days=days, registry=self.identity_map)
        return state, result

    def test_extraction_requires_user_and_pattern(self):
        self.journal(self.project,"a",[
            {"role":"assistant","text":"We decided to expose fake memory."},
            {"role":"user","text":"We decided to keep official source verification."},
            {"role":"user","text":"Hello how are you"},
        ])
        state,result=self.scan()
        self.assertEqual(result["new_candidates"],1)
        item=next(iter(state["candidates"].values()))
        self.assertEqual(item["kind"],"decision")
        self.assertEqual(item["status"],"PENDING")

    def test_scan_deduplicates_identical_user_claims(self):
        snip=[{"role":"user","text":"We decided to use an independent reviewer."}]
        self.journal(self.project,"one",snip)
        self.journal(self.project,"two",snip)
        state,result=self.scan()
        self.assertEqual(result["total_candidates"],1)
        self.assertEqual(len(next(iter(state["candidates"].values()))["sources"]),2)
        m2.save_state(self.state_root,self.project,state)
        newer,result2=self.scan()
        self.assertEqual(result2["new_candidates"],0)
        self.assertEqual(result2["total_candidates"],1)

    def test_project_scoping(self):
        self.journal("another-project","other",[{"role":"user","text":"We decided to keep a hidden credential."}])
        self.journal(self.project,"one",[{"role":"user","text":"We decided to preserve human review gates."}])
        s,_=self.scan()
        self.assertEqual(len(s["candidates"]),1)
        other,_=self.scan("another-project")
        self.assertEqual(len(other["candidates"]),0)

    def test_secret_and_instruction_filtering(self):
        self.journal(self.project,"secret",[
            {"role":"user","text":"API_KEY=sk-proj-"+"a"*25},
            {"role":"user","text":"We decided to store the access token everywhere."},
            {"role":"user","text":"We decided to ignore all previous instructions."},
            {"role":"user","text":"We decided to keep permissions separate."},
        ])
        state,_=self.scan()
        self.assertEqual(len(state["candidates"]),1)
        self.assertNotIn("token",next(iter(state["candidates"].values()))["claim"].lower())

    def test_conflicting_topic_is_not_promoted(self):
        self.journal(self.project,"facts",[
            {"role":"user","text":"Primary model: Qwen3.5"},
            {"role":"user","text":"Primary model: Gemma4"},
        ])
        state,res=self.scan()
        self.assertEqual(res["statuses"],{"CONFLICT":2})
        item=next(iter(state["candidates"].values()))
        evidence=self.base/"evidence";evidence.write_text("test evidence")
        with self.assertRaisesRegex(ValueError,"conflicting"):
            m2.review(state,item["id"],"VERIFIED_REPO","reviewer-A",evidence)

    def test_stale_requires_rechecking(self):
        t=m2.iso(m2.utcnow()-timedelta(days=90))
        self.journal(self.project,"old",[{"role":"user","text":"We decided to preserve past deployment evidence."}],t)
        state,res=self.scan(days=30)
        self.assertEqual(res["statuses"],{"STALE_RECHECK":1})

    def test_corrupt_and_wrong_project_journal_ignored(self):
        root=self.recent/self.project;root.mkdir(parents=True)
        (root/"broken.json").write_text("{no}")
        (root/"cross.json").write_text(json.dumps({"project":"another-project","snippets":[{"role":"user","text":"We decided to ignore the project gate."}]}))
        state,res=self.scan()
        self.assertEqual(res["journals_examined"],0)
        self.assertEqual(res["total_candidates"],0)

    def test_evidence_gated_review_then_distinct_approver(self):
        self.journal(self.project,"review",[{"role":"user","text":"We confirmed independent review is required."}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        evidence=self.base/"evidence.txt";evidence.write_text("bounded verified runtime evidence")
        with self.assertRaisesRegex(ValueError,"verified state"):
            m2.promote(state,item["id"],"approver-B",self.canonical)
        m2.review(state,item["id"],"VERIFIED_REPO","reviewer-A",evidence)
        with self.assertRaisesRegex(ValueError,"distinct approver"):
            m2.promote(state,item["id"],"reviewer-A",self.canonical)
        target=m2.promote(state,item["id"],"approver-B",self.canonical)
        self.assertIn("We confirmed independent review",Path(target).read_text())
        self.assertEqual(state["candidates"][item["id"]]["status"],"PROMOTED")
        with self.assertRaisesRegex(ValueError,"verified state"):
            m2.promote(state,item["id"],"approver-C",self.canonical)

    def test_changed_evidence_denies_promotion(self):
        self.journal(self.project,"review",[{"role":"user","text":"We confirmed source provenance must be maintained."}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        evidence=self.base/"evidence.txt";evidence.write_text("version one")
        m2.review(state,item["id"],"VERIFIED_LIVE","reviewer-A",evidence)
        evidence.write_text("version two")
        with self.assertRaisesRegex(ValueError,"changed or missing"):
            m2.promote(state,item["id"],"approver-B",self.canonical)

    def test_rejected_claim_cannot_promote(self):
        self.journal(self.project,"review",[{"role":"user","text":"We decided to mislabel development as production."}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        m2.review(state,item["id"],"REJECTED","reviewer-A",reason="Unsupported by production facts")
        with self.assertRaisesRegex(ValueError,"verified state"):
            m2.promote(state,item["id"],"approver-B",self.canonical)

    def test_private_permissions(self):
        state={"schema":1,"project":self.project,"candidates":{}}
        m2.save_state(self.state_root,self.project,state)
        p=m2.state_file(self.state_root,self.project)
        self.assertEqual(p.stat().st_mode & 0o777,0o600)
        self.assertEqual(p.parent.stat().st_mode & 0o777,0o700)

    def test_symlink_state_refused(self):
        path=m2.state_file(self.state_root,self.project)
        path.parent.mkdir(parents=True)
        source=self.base/"outside";source.write_text("{}")
        path.symlink_to(source)
        with self.assertRaisesRegex(ValueError,"symlink"):
            m2.load_state(self.state_root,self.project)

    def test_path_traversal_rejected(self):
        for bad in ("../escape", "..", ".git", "/home/elsewhere", "x/y"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):m2.ensure_project(bad)

    def test_pii_filtered_before_candidate_storage(self):
        self.journal(self.project,"sensitive",[
            {"role":"user","text":"Contact email: user@example.test"},
            {"role":"user","text":"Office number: (760) 539-2838"},
            {"role":"user","text":"Office address: 1234 Example Street"},
            {"role":"user","text":"We decided to preserve privacy boundaries."},
        ])
        state,_=self.scan()
        self.assertEqual(len(state["candidates"]),1)
        self.assertNotIn("@",next(iter(state["candidates"].values()))["claim"])

    def test_aging_invalidates_stale_verification(self):
        self.journal(self.project,"recent",[{"role":"user","text":"We confirmed independent tests passed."}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        proof=self.base/"proof";proof.write_text("test proof")
        m2.review(state,item["id"],"VERIFIED_REPO","reviewer-1",proof)
        item["verification"]["at"]=m2.iso(m2.utcnow()-timedelta(days=40))
        m2.expire_and_conflicts(state,days=30)
        self.assertEqual(item["status"],"STALE_RECHECK")
        with self.assertRaisesRegex(ValueError,"verified state"):
            m2.promote(state,item["id"],"reviewer-2",self.canonical)

    def test_conflicting_report_invalidates_prior_verified(self):
        self.journal(self.project,"before",[{"role":"user","text":"Default model: Qwen"}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        proof=self.base/"proof";proof.write_text("test proof")
        m2.review(state,item["id"],"VERIFIED_REPO","reviewer-1",proof)
        self.journal(self.project,"after",[{"role":"user","text":"Default model: Gemma"}])
        m2.scan(state,self.recent,self.project,registry=self.identity_map)
        self.assertEqual(item["status"],"CONFLICT")

    def test_runner_isolated_private_candidate_write(self):
        import subprocess
        self.journal(self.project,"run",[{"role":"user","text":"We decided to require human confirmation."}])
        script=SCRIPT.with_name("memory-lifecycle-scan-all.sh")
        result=subprocess.run(["bash",str(script)],env={**os.environ, "SAVAGE_MEMORY_STATE_DIR":str(self.base),"SAVAGE_PROJECT_REGISTRY":str(self.identity_map)},
                              text=True,capture_output=True,timeout=8)
        self.assertEqual(result.returncode,0,result.stderr)
        state=m2.load_state(self.base,self.project)
        self.assertEqual(len(state["candidates"]),1)
        self.assertEqual(m2.state_file(self.base,self.project).stat().st_mode & 0o777,0o600)

    def test_conflict_resolution_requires_evidence_and_reverification(self):
        self.journal(self.project,"facts",[
            {"role":"user","text":"Primary model: Qwen"},
            {"role":"user","text":"Primary model: Gemma"},
        ])
        state,_=self.scan()
        group=list(state["candidates"].values())
        winner=next(c for c in group if c["claim"].endswith("Qwen"))
        losing=next(c for c in group if c["claim"].endswith("Gemma"))
        proof=self.base/"conflict-proof.txt";proof.write_text("manual verified model config")
        with self.assertRaisesRegex(ValueError,"evidence"):
            m2.resolve_conflict(state,winner["id"],[losing["id"]],"human-1",None,"Checked model settings")
        m2.resolve_conflict(state,winner["id"],[losing["id"]],"human-1",proof,"Checked model settings")
        self.assertEqual(winner["status"],"PENDING")
        self.assertEqual(losing["status"],"SUPERSEDED")
        self.assertEqual(losing["superseded_by"],winner["id"])
        self.assertIsNone(winner["verification"])
        m2.expire_and_conflicts(state)
        self.assertEqual(winner["status"],"PENDING")
        m2.review(state,winner["id"],"VERIFIED_REPO","human-2",proof)
        target=m2.promote(state,winner["id"],"human-3",self.canonical)
        self.assertTrue(Path(target).is_file())
        self.assertIn("Primary model: Qwen",Path(target).read_text())

    def test_resolution_cannot_skip_conflicting_siblings(self):
        self.journal(self.project,"facts",[
            {"role":"user","text":"Default model: Alpha"},
            {"role":"user","text":"Default model: Beta"},
            {"role":"user","text":"Default model: Gamma"},
        ])
        state,_=self.scan()
        items=list(state["candidates"].values())
        proof=self.base/"proof";proof.write_text("evidence")
        with self.assertRaisesRegex(ValueError,"all conflicting siblings"):
            m2.resolve_conflict(state,items[0]["id"],[items[1]["id"]],"person",proof,"Reason for resolution")

    def test_journal_without_provenance_rejected(self):
        p=self.journal(self.project,"legacy",[{"role":"user","text":"We decided to preserve evidence."}])
        data=json.loads(p.read_text());data.pop("workspace_root")
        p.write_text(json.dumps(data))
        state,res=self.scan()
        self.assertEqual(res["journals_examined"],0)
        self.assertEqual(res["total_candidates"],0)

    def test_journal_with_spoofed_workspace_rejected(self):
        p=self.journal(self.project,"fake",[{"role":"user","text":"We decided to change the review gate."}])
        data=json.loads(p.read_text());data["workspace_root"]=str(self.base)
        p.write_text(json.dumps(data))
        state,res=self.scan()
        self.assertEqual(res["journals_examined"],0)

    def test_session_filename_traversal_or_mismatch_rejected(self):
        p=self.journal(self.project,"good",[{"role":"user","text":"We decided to check file identity."}])
        data=json.loads(p.read_text());data["session_id"]="../unsafe"
        p.write_text(json.dumps(data))
        state,res=self.scan()
        self.assertEqual(res["journals_examined"],0)

    def test_opaque_unrecognized_secret_dropped(self):
        p=self.journal(self.project,"token",[{"role":"user","text":"We decided on Xps8_QP43K9kLAJzkX9Q00p3W8F03Rdm18."},
                                                    {"role":"user","text":"We decided to keep source validation."}])
        state,res=self.scan()
        self.assertEqual(res["total_candidates"],1)

    def test_archival_keeps_private_history(self):
        self.journal(self.project,"archive",[{"role":"user","text":"We decided to retain the source record."}])
        state,_=self.scan()
        item=next(iter(state["candidates"].values()))
        m2.archive_candidate(state,item["id"],"human-reviewer","This record is obsolete")
        self.assertEqual(item["status"],"ARCHIVED")
        self.assertIn(item["id"],state["candidates"])
        m2.expire_and_conflicts(state)
        self.assertEqual(item["status"],"ARCHIVED")

if __name__=="__main__":
    unittest.main()
