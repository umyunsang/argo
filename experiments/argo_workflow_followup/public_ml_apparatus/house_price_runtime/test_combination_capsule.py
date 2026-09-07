"""Synthetic capsule exact membership and closed-file checks, never code execution."""
from __future__ import annotations
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.deployment_assets as deployment_assets_module
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_capsule import CapsuleProtectedRoots, SyntheticCapsuleError, materialize_synthetic_capsule
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.deployment_assets import NamespaceMember, DeploymentError, materialize_namespace
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding, read_bound
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import ClosureLimits, capture_tree, verify_tree

ROOT=Path(__file__).resolve().parents[4]
CONTRACT=ROOT/"paper/research/public-ml-programme-qualification/house-price-p0/option-a2-synthetic-capsule-contract-v1.json"

def binding(path):
    data=path.read_bytes();return FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),path.stat().st_mtime_ns)

class SyntheticCapsuleTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="hp-capsule-mock-")
        self.root=Path(self.temp.name).resolve();self.root.chmod(0o700)
        self.destination=self.root/"synthetic-namespace"
        identities=[]
        for name in ("raw","auth","profile","controller","public"):
            path=self.root/name;path.mkdir(mode=0o700)
            info=path.stat();identities.append(DirectoryIdentity(path,info.st_dev,info.st_ino))
        self.protected=CapsuleProtectedRoots(*identities)
        self.expected=json.loads(CONTRACT.read_bytes())["exact_members"]
        self.members=[]
        for index,relative in enumerate(self.expected):
            source=self.root/("source-"+str(index)+".py")
            source.write_bytes(("VALUE = "+repr(relative)+"\n").encode())
            self.members.append(NamespaceMember(relative,binding(source)))
        self.members=tuple(self.members)
    def tearDown(self):self.temp.cleanup()

    def test_exact_capsule_has_twenty_five_sources_and_four_empty_initializers(self):
        tree=materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        self.assertEqual(tree.file_count,29);self.assertEqual(tree.directory_count,4);self.assertEqual(tree.symlink_count,0)
        for member in self.members:
            self.assertEqual((self.destination/member.relative_path).read_bytes(),member.source.path.read_bytes())
        for path in self.destination.rglob("__init__.py"):self.assertEqual(path.read_bytes(),b"")
        self.assertEqual(verify_tree(self.destination,tree,ClosureLimits(160,8388608,1048576,8,4096)),tree)
        with self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)

    def test_missing_extra_duplicate_and_hash_tampered_sources_fail_before_destination(self):
        invalids=[self.members[:-1],self.members+(self.members[0],),
            (replace(self.members[0],relative_path="experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_other.py"),)+self.members[1:],
            (replace(self.members[0],source=replace(self.members[0].source,sha256="0"*64)),)+self.members[1:]]
        for index,members in enumerate(invalids):
            output=self.root/("denied-"+str(index))
            with self.subTest(index=index),self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(output,members,protected_roots=self.protected)
            self.assertFalse(output.exists())

    def test_production_allowlist_is_not_broadened_by_synthetic_copy(self):
        materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        member=next(item for item in self.members if item.relative_path.endswith("/test_bridge.py"))
        with self.assertRaises(DeploymentError):materialize_namespace(self.root/"production",(member,))
        self.assertFalse((self.root/"production").exists())

    def test_symlink_source_is_rejected_and_partial_copy_cannot_be_reused(self):
        member=self.members[0];link=self.root/"source-link.py";link.symlink_to(member.source.path)
        linked=(replace(member,source=replace(member.source,path=link)),)+self.members[1:]
        with self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(self.destination,linked,protected_roots=self.protected)
        self.assertFalse(self.destination.exists())
        native_write=os.write;calls=0
        def interrupted(fd,data):
            nonlocal calls
            calls+=1
            if calls>1:raise OSError("synthetic copy failure")
            return native_write(fd,data[:7])
        with patch("os.write",side_effect=interrupted),self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        self.assertTrue(self.destination.exists())
        with self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)

    def test_destination_is_private_outside_git_and_copied_bytes_are_reopened(self):
        gitparent=self.root/"worktree";gitparent.mkdir(mode=0o700);(gitparent/".git").mkdir()
        with self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(gitparent/"denied",self.members,protected_roots=self.protected)
        import_target="experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_capsule.read_bound"
        from_source_reads=[]
        def seen(item,cap):
            from_source_reads.append(item.path)
            return read_bound(item,cap)
        with patch(import_target,side_effect=seen):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        copied=[self.destination/item.relative_path for item in self.members]
        self.assertTrue(all(path in from_source_reads for path in copied))

    def test_tampered_destination_bytes_and_unlisted_extra_entry_do_not_get_sealed(self):
        import_target="experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_capsule"
        import_names=("tamper", "extra")
        for mode in import_names:
            output=self.root/("changed-"+mode)
            writes=0
            original_write=deployment_assets_module._write_new
            def write_and_mutate(path,data,permissions):
                nonlocal writes
                original_write(path,data,permissions)
                if path.name=="__init__.py":return
                writes+=1
                if writes==1:
                    if mode=="tamper":path.write_bytes(b"different copied source\n")
                    else:(output/"unlisted.py").write_bytes(b"EXTRA=True\n")
            with self.subTest(mode=mode),patch(import_target+"._write_new",side_effect=write_and_mutate),self.assertRaises(SyntheticCapsuleError):
                materialize_synthetic_capsule(output,self.members,protected_roots=self.protected)
            self.assertTrue(output.exists())
            with self.assertRaises(SyntheticCapsuleError):materialize_synthetic_capsule(output,self.members,protected_roots=self.protected)

    def test_protected_profile_is_not_a_valid_capsule_parent(self):
        profile=self.root/"profile"
        output=profile/"synthetic"
        with self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(output,self.members,protected_roots=self.protected)
        self.assertFalse(output.exists())

    def test_late_same_size_destination_tamper_is_not_resealed(self):
        capture_target="experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_capsule.capture_tree"
        original_capture=capture_tree
        target=self.destination/self.members[0].relative_path
        def mutate_before_capture(root,limits):
            data=target.read_bytes()
            target.write_bytes(bytes([data[0]^1])+data[1:])
            return original_capture(root,limits)
        with patch(capture_target,side_effect=mutate_before_capture),self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        self.assertTrue(self.destination.exists())

    def test_required_protected_identities_reject_missing_changed_or_overlapping_destinations(self):
        with self.assertRaises(TypeError):materialize_synthetic_capsule(self.destination,self.members)
        with self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=None)
        for name in ("raw","auth","profile","controller","public"):
            root=getattr(self.protected,name)
            output=root.path/"synthetic"
            with self.subTest(name=name),self.assertRaises(SyntheticCapsuleError):
                materialize_synthetic_capsule(output,self.members,protected_roots=self.protected)
            self.assertFalse(output.exists())
        wrong=replace(self.protected,raw=replace(self.protected.raw,inode=True))
        with self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=wrong)
        raw=self.protected.raw.path;raw.rename(self.root/"old-raw");raw.mkdir(mode=0o700)
        with self.assertRaises(SyntheticCapsuleError):
            materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        self.assertFalse(self.destination.exists())

    def test_protected_directory_contents_are_never_read(self):
        sentinels=[]
        for name in ("raw","auth","profile","controller","public"):
            path=getattr(self.protected,name).path/"sensitive-sentinel"
            path.write_bytes(b"synthetic protected content");sentinels.append(path)
        native_open=os.open
        def no_content(path,*args,**kwargs):
            if Path(path) in sentinels or str(path)=="sensitive-sentinel":
                raise AssertionError("protected content opened")
            return native_open(path,*args,**kwargs)
        with patch("os.open",side_effect=no_content):
            tree=materialize_synthetic_capsule(self.destination,self.members,protected_roots=self.protected)
        self.assertEqual(tree.file_count,29)

    def test_late_initializer_or_destination_root_change_does_not_pass_final_recipe(self):
        for mode in ("initializer","root"):
            output=self.root/("late-"+mode)
            original_capture=capture_tree
            def late_change(root,limits):
                if mode=="initializer":(output/"experiments/__init__.py").write_bytes(b"x")
                else:
                    output.rename(self.root/"renamed-destination")
                    output.mkdir(mode=0o700)
                return original_capture(root,limits)
            with self.subTest(mode=mode),patch("experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_capsule.capture_tree",side_effect=late_change),self.assertRaises(SyntheticCapsuleError):
                materialize_synthetic_capsule(output,self.members,protected_roots=self.protected)
            self.assertTrue(output.exists())

if __name__=="__main__":unittest.main(verbosity=2)
