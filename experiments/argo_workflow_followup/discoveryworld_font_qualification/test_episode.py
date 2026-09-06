#!/usr/bin/env python3
from __future__ import annotations
import errno,hashlib,sys,tempfile,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from episode import SAMPLES,assert_cold,measure,probe_no_fork
class Font:
 def __init__(self,size):self.value=size
 def size(self,text):return (len(text)*self.value,self.value)
 def metrics(self,text):return [[1,2,3,4,5] for _ in text]
 def render(self,*args):return b"pixels"
class FontModule:
 def __init__(self,sysfont):self.sysfont=sysfont
 def SysFont(self,name,size,bold=False,italic=False):
  path=(self.sysfont.Sysfonts.get("arial") if name.lower()=="arial" else self.sysfont.Sysalias.get("monospace"))[(bold,italic)];return self.sysfont.font_constructor(path,size,bold,italic)
class Image:
 @staticmethod
 def tostring(surface,mode):return surface
class Sysfont:
 def __init__(self,path):self.font_constructor=lambda fontpath,size,bold,italic:Font(size);self.Sysfonts={"arial":{(False,False):str(path)}};self.Sysalias={"monospace":{(False,False):str(path),(True,False):str(path)}}
class Tests(unittest.TestCase):
 def test_fixed_samples(self):self.assertEqual(SAMPLES,["ARGO 0123","한글 ARGO"])
 def test_warm_and_alias_cache_rejected(self):
  shared=lambda *args,**kwargs:None;module=types.SimpleNamespace(sysfont=types.SimpleNamespace(is_init=True,Sysfonts={},Sysalias={},SysFont=shared),font=types.SimpleNamespace(SysFont=shared))
  with self.assertRaises(RuntimeError):assert_cold(module)
  module.sysfont.is_init=False;module.font.SysFont=lambda:None
  with self.assertRaises(RuntimeError):assert_cold(module)
 def test_fork_probe_requires_permission_errno(self):
  def denied(*args,**kwargs):raise PermissionError(errno.EPERM,"denied")
  self.assertTrue(probe_no_fork(denied));self.assertFalse(probe_no_fork(lambda *args,**kwargs:None))
  with self.assertRaises(FileNotFoundError):probe_no_fork(lambda *args,**kwargs:(_ for _ in ()).throw(FileNotFoundError(errno.ENOENT,"missing")))
 def test_measure_schema_and_hash(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   path=Path(td)/"font";path.write_bytes(b"font");sysfont=Sysfont(path);module=types.SimpleNamespace(font=FontModule(sysfont),image=Image(),sysfont=sysfont);row=measure(module,{"source":"x","line":1,"name":"Arial","size":8,"bold":False,"italic":False});self.assertEqual(row["font_sha256"],hashlib.sha256(b"font").hexdigest());self.assertEqual(len(row["samples"]),2);self.assertEqual(row["samples"][0]["render_rgba_sha256"],hashlib.sha256(b"pixels").hexdigest())
if __name__=="__main__":unittest.main(verbosity=2)
