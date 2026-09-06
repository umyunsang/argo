#!/usr/bin/env python3
from __future__ import annotations
import hashlib,sys,tempfile,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from episode import SAMPLES,measure
class Font:
 def __init__(self,size):self.value=size
 def size(self,text):return (len(text)*self.value,self.value)
 def metrics(self,text):return [[1,2,3,4,5] for _ in text]
 def render(self,*args):return b"pixels"
class FontModule:
 @staticmethod
 def SysFont(name,size,bold=False,italic=False):return Font(size)
class Image:
 @staticmethod
 def tostring(surface,mode):return surface
class Sysfont:
 def __init__(self,path):self.Sysfonts={"arial":{(False,False):str(path)}};self.Sysalias={"monospace":{(False,False):str(path),(True,False):str(path)}}
class Tests(unittest.TestCase):
 def test_fixed_samples(self):self.assertEqual(SAMPLES,["ARGO 0123","한글 ARGO"])
 def test_measure_schema_and_hash(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   path=Path(td)/"font";path.write_bytes(b"font");module=types.SimpleNamespace(font=FontModule(),image=Image(),sysfont=Sysfont(path));row=measure(module,{"source":"x","line":1,"name":"Arial","size":8,"bold":False,"italic":False});self.assertEqual(row["font_sha256"],hashlib.sha256(b"font").hexdigest());self.assertEqual(len(row["samples"]),2);self.assertEqual(row["samples"][0]["render_rgba_sha256"],hashlib.sha256(b"pixels").hexdigest())
if __name__=="__main__":unittest.main(verbosity=2)
