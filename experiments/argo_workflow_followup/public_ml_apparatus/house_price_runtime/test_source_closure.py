"""Closed byte-tree integrity controls. No external code imports or execution."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import os
import tempfile
import unittest
from source_closure import ClosureError, ClosureLimits, capture_tree, verify_tree

class ClosureTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-closure-")
        self.root=Path(self.temp.name).resolve()/"root";self.root.mkdir()
        (self.root/"module.js").write_bytes(b"export const value = 1;\n")
        (self.root/".hidden").write_bytes(b"metadata")
        (self.root/"pkg").mkdir();(self.root/"pkg"/"module.json").write_bytes(b"{}")
        self.limits=ClosureLimits(32,1024,256,8,512)
    def tearDown(self):self.temp.cleanup()
    def test_complete_tree_and_rederived_bytes_not_self_attestation(self):
        result=capture_tree(self.root,self.limits)
        self.assertEqual((result.file_count,result.directory_count,result.symlink_count),(3,1,0))
        self.assertEqual(result.total_file_bytes,34)
        self.assertEqual(verify_tree(self.root,result,self.limits),result)
        with self.assertRaises(ClosureError):verify_tree(self.root,replace(result,tree_sha256="0"*64),self.limits)
    def test_mutation_hidden_add_remove_and_preserved_mtime_rejected(self):
        result=capture_tree(self.root,self.limits)
        path=self.root/"module.js";saved=path.stat();path.write_bytes(b"export const value = 2;\n")
        os.utime(path,ns=(saved.st_atime_ns,saved.st_mtime_ns))
        with self.assertRaises(ClosureError):verify_tree(self.root,result,self.limits)
        result=capture_tree(self.root,self.limits);(self.root/".new").write_bytes(b"new")
        with self.assertRaises(ClosureError):verify_tree(self.root,result,self.limits)
        result=capture_tree(self.root,self.limits);(self.root/".new").unlink()
        with self.assertRaises(ClosureError):verify_tree(self.root,result,self.limits)
    def test_internal_symlink_bound_external_and_fifo_rejected(self):
        link=self.root/"link";link.symlink_to("module.js")
        result=capture_tree(self.root,self.limits);self.assertEqual(result.symlink_count,1)
        link.unlink();link.symlink_to("pkg/module.json")
        with self.assertRaises(ClosureError):verify_tree(self.root,result,self.limits)
        link.unlink();link.symlink_to(self.root.parent)
        with self.assertRaises(ClosureError):capture_tree(self.root,self.limits)
        link.unlink();os.mkfifo(self.root/"fifo")
        with self.assertRaises(ClosureError):capture_tree(self.root,self.limits)
    def test_caps_before_read_and_root_identity_changes(self):
        with self.assertRaises(ClosureError):capture_tree(self.root,replace(self.limits,max_file_bytes=2))
        with self.assertRaises(ClosureError):capture_tree(self.root,replace(self.limits,max_total_bytes=5))
        with self.assertRaises(ClosureError):capture_tree(self.root,replace(self.limits,max_entries=2))
        result=capture_tree(self.root,self.limits);old=self.root.with_name("old");self.root.rename(old);self.root.mkdir()
        with self.assertRaises(ClosureError):verify_tree(self.root,result,self.limits)

    def test_boolean_expected_fields_are_not_integer_census_values(self):
        with tempfile.TemporaryDirectory(prefix="hp-one-file-tree-") as tmp:
            root=Path(tmp).resolve();(root/"a").write_bytes(b"x")
            expected=capture_tree(root,self.limits)
            for field in ["root_device","root_inode","file_count","directory_count","symlink_count","total_file_bytes","maximum_mtime_ns"]:
                with self.subTest(field=field),self.assertRaises(ClosureError):
                    verify_tree(root,replace(expected,**{field:bool(getattr(expected,field))}),self.limits)
            for field,value in [("tree_sha256","A"*64),("root",str(root)+"/../"+root.name),
                                ("file_count",-1),("maximum_mtime_ns",2**100)]:
                with self.subTest(field=field),self.assertRaises(ClosureError):
                    verify_tree(root,replace(expected,**{field:value}),self.limits)

if __name__=="__main__":unittest.main(verbosity=2)
