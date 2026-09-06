#!/usr/bin/env python3
from __future__ import annotations
import json,os,shutil,subprocess,sys,tarfile,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from environment_manifest import copy_and_verify
from run import SANDBOX_EXEC,SOURCE_COMMIT,SOURCE_REPO,managed_run,sandbox_profile
class Tests(unittest.TestCase):
 def test_relocated_capsule_imports_only_sealed_python_packages_and_source(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();manifest=json.loads((HERE/"environment-content-manifest.json").read_text());copied=copy_and_verify(manifest,root/"runtime");source=root/"source";source.mkdir();archive=root/"source.tar"
   with archive.open("wb") as stream:done=subprocess.run(["git","-C",SOURCE_REPO,"archive","--format=tar",SOURCE_COMMIT],stdout=stream,check=False)
   self.assertEqual(done.returncode,0)
   with tarfile.open(archive) as tar:tar.extractall(source,filter="data")
   bundle=root/"bundle";bundle.mkdir();shutil.copy2(HERE/"bootstrap.py",bundle/"bootstrap.py");dummy='import json,os,subprocess,sys\nfrom pathlib import Path\nimport discoveryworld,numpy,pygame\nfork_denied=False;original_denied=False\ntry:subprocess.run(["/usr/bin/true"],check=True)\nexcept (OSError,subprocess.SubprocessError):fork_denied=True\ntry:Path("/Users/um-yunsang/.cache/argo-research/DiscoveryWorld/discoveryworld/DiscoveryWorldAPI.py").read_bytes()\nexcept OSError:original_denied=True\nprint(json.dumps({"executable":sys.executable,"prefix":sys.prefix,"discoveryworld":discoveryworld.__file__,"numpy":numpy.__file__,"pygame":pygame.__file__,"fork_denied":fork_denied,"original_denied":original_denied},sort_keys=True))\n';(bundle/"episode.py").write_text(dummy);work=root/"work";work.mkdir();profile=work/"worker.sb";profile.write_text(sandbox_profile(work,bundle,source));python=copied["base_python"]/"bin/python3.11";site=copied["site_packages"];argv=[SANDBOX_EXEC,"-f",str(profile),str(python),"-I","-S","-B",str(bundle/"bootstrap.py"),"worker",str(bundle),str(source),str(site)];env={"HOME":str(work),"TMPDIR":str(work),"PATH":"/usr/bin:/bin","PYTHONDONTWRITEBYTECODE":"1","PYGAME_HIDE_SUPPORT_PROMPT":"1","SDL_VIDEODRIVER":"dummy","SDL_AUDIODRIVER":"dummy"};run=managed_run(argv,work,env,work/"stdout",work/"stderr",work/"events",30,35);self.assertEqual(run["exit_code"],0,(work/"stderr").read_text());value=json.loads((work/"stdout").read_text());self.assertTrue(value["fork_denied"]);self.assertTrue(value["original_denied"]);self.assertTrue(value["executable"].startswith(str(root)));self.assertTrue(value["prefix"].startswith(str(root)));self.assertTrue(value["discoveryworld"].startswith(str(source)));self.assertTrue(value["numpy"].startswith(str(site)));self.assertTrue(value["pygame"].startswith(str(site)))
if __name__=="__main__":unittest.main(verbosity=2)
