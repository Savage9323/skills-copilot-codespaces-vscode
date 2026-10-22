import importlib.util,hashlib,os,pathlib,tempfile,unittest,json
p=pathlib.Path(__file__).parents[1]/"scripts/vault-broker.py"
spec=importlib.util.spec_from_file_location("vaultbroker",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class BrokerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  self.binary=self.root/"trusted-tool"
  self.binary.write_text("#!/bin/sh\nexit 0\n");self.binary.chmod(0o700)
  self.bws=self.root/"bws"
  self.bws.write_text("#!/bin/sh\nexit 0\n");self.bws.chmod(0o700)
  self.uuid="11111111-2222-3333-4444-555555555555"
  self.mapping={"provider":"bitwarden","projects":{"sbi":{"project_id":self.uuid}}}
  self.policy={"actions":{"sbi":{"health":{"executable":str(self.binary),"args":[],"sha256":m.sha256_file(self.binary)}}}}
 def test_permitted_trusted_action(self):
  argv=m.build_command("sbi","health",self.mapping,self.policy,self.bws)
  self.assertEqual(argv[1:4],["run","--project-id",self.uuid])
 def test_cross_project_denied(self):
  with self.assertRaisesRegex(ValueError,"project not enrolled"):
   m.build_command("bountyhunter","health",self.mapping,self.policy,self.bws)
 def test_unlisted_action_denied(self):
  with self.assertRaisesRegex(ValueError,"not on trusted"):
   m.build_command("sbi","arbitrary",self.mapping,self.policy,self.bws)
 def test_tampered_executable_denied(self):
  self.binary.write_text("#!/bin/sh\necho modified\n")
  with self.assertRaisesRegex(ValueError,"checksum changed"):
   m.build_command("sbi","health",self.mapping,self.policy,self.bws)
 def test_symlink_denied(self):
  link=self.root/"link";link.symlink_to(self.binary)
  self.policy["actions"]["sbi"]["health"]["executable"]=str(link)
  with self.assertRaisesRegex(ValueError,"symlinked"):
   m.build_command("sbi","health",self.mapping,self.policy,self.bws)
 def test_group_writable_denied(self):
  self.binary.chmod(0o770)
  with self.assertRaisesRegex(ValueError,"writable"):
   m.build_command("sbi","health",self.mapping,self.policy,self.bws)
 def test_bad_project_id_denied(self):
  self.mapping["projects"]["sbi"]["project_id"]="BITWARDEN_PROJECT_UUID"
  with self.assertRaisesRegex(ValueError,"verified UUID"):
   m.build_command("sbi","health",self.mapping,self.policy,self.bws)
 def test_command_injection_is_not_allowed(self):
  with self.assertRaisesRegex(ValueError,"invalid project or action"):
   m.build_command("sbi","health;rm",self.mapping,self.policy,self.bws)
 def test_private_config_rejected_if_exposed(self):
  path=self.root/"public.json";path.write_text(json.dumps(self.mapping));path.chmod(0o644)
  with self.assertRaisesRegex(ValueError,"insecure"):
   m.private_json(path)
if __name__=="__main__":unittest.main()
