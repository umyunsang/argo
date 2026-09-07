"""Run one explicitly root-admitted synthetic A2 case, never a production P0.

The separate trusted preflight must verify source bytes before importing this
module. Import has no effects; unit tests replace every fixture/process call.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import threading
import time
from typing import Sequence

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_acceptance import (
    CombinationAssessment, CombinationExpectation, assess_combination,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.combination_fixture import (
    CombinationFixture, CombinationFixtureError, FixtureCloseResult, prepare_fixture,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment import (
    FrontendDeploymentInput, write_extension_binding, write_frontend_deployment, write_process_config,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    ControllerRunReceipt, RunControllerConfig, capture_interpreter_identity, capture_path_identity,
    config_to_dict, run_controller, _validate_config,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.deployment_assets import (
    _new_private_path, _write_new, write_module_bootstrap,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_driver import _current_session
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import _gate_json, _gate_read
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.source_closure import (
    ClosureLimits, SourceTree, capture_tree, verify_tree,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.usage_observer import UsageObserver, UsageObserverConfig

KERNEL="/Users/um-yunsang/.prime/agent/kernel-venv/bin/python"
PRIME_ROOT=Path("/opt/homebrew/lib/node_modules/prime-agent")
PRIME_ENTRY=PRIME_ROOT/"dist/index.js"
MODULE="experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime."
PREFIX="experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/"
FAUX_RELATIVE="a2-frontend-probes/a2-combination-frontend.ts"
NORMAL_SHA256="dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21"
EXTENSION_SHA256="8e2ca3351e601b5d4733000dc9c704f0327fdc941851fadbc0d3f59357d2d3fe"
PROCESS_SHA256="135a3e28291ea8e7db3b85cdd4fda05124113baaeb0d1a1335a905bc5bdd3f33"
EXEC_SHA256="c8c19b2d87bb155f8886ba0a696aa962a1fa9d55feb17e1f01ba65bc95054840"
CONFIG_SCHEMA="argo-house-price-a2-combination-case-config/v2"
TREE_LIMITS=ClosureLimits(160,8388608,1048576,8,4096)
PRIME_LIMITS=ClosureLimits(30000,268435456,67108864,32,4096)
HEX64=re.compile(r"[0-9a-f]{64}")
EVIDENCE_FILES={"controller-process-receipt.json":1048576,"case-receipt.json":65536}
CONTROL_FILES={"normal-process-config.json":65536,"synthetic-process-config.json":65536}
LIMITATIONS=(
    "Synthetic integration only; production main entry, fixed factory list and OAuth transport were not executed.",
    "Fake ORX/runner receipts are fabricated; no real model fit, task data or hidden score is observed.",
    "RSS/current-response usage and whole-case stage budgets are monitored, not hard aggregate limits.",
    "Source and cleanup proof use a root-private no-concurrent-same-UID-mutator TCB, not hostile-host isolation.",
)


@dataclass(frozen=True)
class CaseProtectedRoots:
    raw: DirectoryIdentity
    auth: DirectoryIdentity
    profile: DirectoryIdentity
    controller: DirectoryIdentity
    public: DirectoryIdentity


@dataclass(frozen=True)
class CombinationCaseConfig:
    case_root: Path
    namespace_tree: SourceTree
    frontend_seed_tree: SourceTree
    installed_prime_tree: SourceTree
    expected_faux_frontend_sha256: str
    expected_fixture_module_sha256: str
    expected_acceptance_module_sha256: str
    protected_roots: CaseProtectedRoots


@dataclass(frozen=True)
class CombinationCaseResult:
    status: str
    stage: str
    reason: str
    receipt: FileBinding | None
    process_attempts: int
    controller_context_id: str | None


@dataclass(frozen=True)
class _PreparedEnvironment:
    normal_process: FileBinding
    synthetic_process: FileBinding
    process_config: RunControllerConfig
    gate_config: FileBinding
    synthetic_frontend: FileBinding
    frontend_tree: SourceTree
    session_directory: DirectoryIdentity
    cwd: str
    artifact_root: Path


class CaseError(ValueError):
    def __init__(self):super().__init__("COMBINATION_CASE_INVALID")


def _canonical(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def _binding_dict(value: FileBinding | None):
    if value is None:return None
    return {"path":str(value.path),"sha256":value.sha256,"bytes":value.bytes,"mtime_ns_max":value.mtime_ns_max}


def _config_record(config: CombinationCaseConfig):
    value=asdict(config);value["case_root"]=str(config.case_root)
    for field in fields(CaseProtectedRoots):
        value["protected_roots"][field.name]["path"]=str(getattr(config.protected_roots,field.name).path)
    return {"schema_version":CONFIG_SCHEMA,**value}


def _directory(path: Path) -> DirectoryIdentity:
    if not isinstance(path,Path) or not path.is_absolute() or ".." in path.parts or path.resolve(strict=True)!=path:
        raise CaseError()
    info=path.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o700 or info.st_uid!=os.getuid():raise CaseError()
    return DirectoryIdentity(path,info.st_dev,info.st_ino)


def _assert_directory(fd: int, identity: DirectoryIdentity) -> None:
    for info in (os.fstat(fd),identity.path.lstat()):
        if (not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o700 or info.st_uid!=os.getuid() or
                (info.st_dev,info.st_ino)!=(identity.device,identity.inode)):raise CaseError()


def _verify_protected_roots(case_root: Path, policy: CaseProtectedRoots) -> None:
    if type(policy) is not CaseProtectedRoots:raise CaseError()
    descriptors=[]
    try:
        for field in fields(CaseProtectedRoots):
            identity=getattr(policy,field.name)
            if (type(identity) is not DirectoryIdentity or not isinstance(identity.path,Path) or
                    type(identity.device) is not int or not 0<=identity.device<=2**64-1 or
                    type(identity.inode) is not int or not 1<=identity.inode<=2**64-1):raise CaseError()
            path=identity.path
            if (not path.is_absolute() or ".." in path.parts or path.resolve(strict=True)!=path or
                    case_root==path or path in case_root.parents or case_root in path.parents):raise CaseError()
            descriptor=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            descriptors.append((descriptor,identity))
        for descriptor,identity in descriptors:
            for info in (os.fstat(descriptor),identity.path.lstat()):
                if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or
                        (info.st_dev,info.st_ino)!=(identity.device,identity.inode)):raise CaseError()
    finally:
        for descriptor,_ in reversed(descriptors):os.close(descriptor)


def _elapsed_since(started: float) -> float:
    now=time.monotonic()
    if (type(now) not in (int,float) or not math.isfinite(now) or now<started):raise CaseError()
    return float(now-started)


def _file(path: Path, cap: int, expected: str | None=None) -> FileBinding:
    info=path.lstat()
    data=_gate_read(path,cap,expected,info.st_size,info.st_mtime_ns)
    return FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),info.st_mtime_ns)


def _publish(directory: DirectoryIdentity, name: str, payload: object, allowed: dict[str,int], total_cap: int) -> FileBinding:
    data=_canonical(payload)
    if name not in allowed or not 0<len(data)<=allowed[name]:raise CaseError()
    fd=os.open(directory.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        _assert_directory(fd,directory)
        names=set();total=len(data)
        with os.scandir(fd) as entries:
            for entry in entries:
                info=entry.stat(follow_symlinks=False)
                if (entry.name not in allowed or not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or
                        stat.S_IMODE(info.st_mode)!=0o600 or info.st_uid!=os.getuid() or
                        not 0<=info.st_size<=allowed[entry.name]):raise CaseError()
                names.add(entry.name);total+=info.st_size
                if len(names)>=len(allowed) or total>total_cap:raise CaseError()
        if name in names or total>total_cap:raise CaseError()
        output=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:
            written=0
            while written<len(data):
                count=os.write(output,data[written:])
                if count<=0:raise CaseError()
                written+=count
            os.fsync(output)
            info=os.fstat(output)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size!=len(data):raise CaseError()
        finally:os.close(output)
        os.fsync(fd);_assert_directory(fd,directory)
        binding=FileBinding(directory.path/name,hashlib.sha256(data).hexdigest(),len(data),info.st_mtime_ns)
        if _gate_read(binding.path,allowed[name],binding.sha256,binding.bytes,binding.mtime_ns_max)!=data:raise CaseError()
        return binding
    finally:os.close(fd)


def _census_case(identity: DirectoryIdentity) -> None:
    rootfd=os.open(identity.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    files=0;total=0
    try:
        _assert_directory(rootfd,identity)
        stack=[(identity.path,0)]
        while stack:
            path,depth=stack.pop()
            if depth>20:raise CaseError()
            with os.scandir(path) as entries:
                for entry in entries:
                    info=entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        stack.append((Path(entry.path),depth+1))
                    elif stat.S_ISREG(info.st_mode) and info.st_nlink==1:
                        files+=1;total+=info.st_size
                    else:raise CaseError()
                    if files+len(stack)>2048 or total>67108864:raise CaseError()
        _assert_directory(rootfd,identity)
    finally:os.close(rootfd)


def _verify_sources(config: CombinationCaseConfig) -> None:
    trees=(config.namespace_tree,config.frontend_seed_tree,config.installed_prime_tree)
    if any(type(tree) is not SourceTree for tree in trees):raise CaseError()
    roots=tuple(Path(tree.root) for tree in trees)
    for index,left in enumerate(roots):
        for right in roots[index+1:]:
            if left==right or left in right.parents or right in left.parents:raise CaseError()
    if any(config.case_root==root or root in config.case_root.parents or config.case_root in root.parents for root in roots):
        raise CaseError()
    if roots[2]!=PRIME_ROOT:raise CaseError()
    for tree,limits in zip(trees,(TREE_LIMITS,TREE_LIMITS,PRIME_LIMITS)):
        verify_tree(Path(tree.root),tree,limits)
    runtime=roots[0]/PREFIX
    if Path(__file__).resolve()!=runtime/"combination_driver.py":raise CaseError()
    for name,digest in (("combination_fixture.py",config.expected_fixture_module_sha256),
                        ("combination_acceptance.py",config.expected_acceptance_module_sha256),
                        ("controller_process.py",PROCESS_SHA256),("process_exec.py",EXEC_SHA256)):
        _file(runtime/name,1048576,digest)
    for relative,digest in (("controller-main.ts",NORMAL_SHA256),("controller-extension.ts",EXTENSION_SHA256),
                             (FAUX_RELATIVE,config.expected_faux_frontend_sha256)):
        _file(roots[1]/relative,1048576,digest)


def _prepare_environment(config: CombinationCaseConfig, fixture: CombinationFixture, started_ns: int) -> _PreparedEnvironment:
    case=config.case_root
    paths={name:case/name for name in ("frontend","profile","public","artifacts","control","gate-outcomes")}
    for path in paths.values():path.mkdir(mode=0o700)
    frontend=paths["frontend"];(frontend/"a2-frontend-probes").mkdir(mode=0o700)
    artifact=paths["artifacts"];session=artifact/"session";session.mkdir(mode=0o700)
    temporary=artifact/"tmp";temporary.mkdir(mode=0o700)
    source=Path(config.frontend_seed_tree.root)
    for relative,digest in (("controller-main.ts",NORMAL_SHA256),("controller-extension.ts",EXTENSION_SHA256),
                             (FAUX_RELATIVE,config.expected_faux_frontend_sha256)):
        binding=_file(source/relative,1048576,digest)
        data=_gate_read(binding.path,1048576,binding.sha256,binding.bytes,binding.mtime_ns_max)
        _write_new(frontend/relative,data,0o600)
        _file(frontend/relative,1048576,digest)
    _write_new(paths["profile"]/"settings.json",_canonical({"retry":{"enabled":False,"provider":{"timeoutMs":120000,"maxRetries":0}}}),0o600)
    _write_new(frontend/"system.md",b"This is a bounded synthetic integration check. Use read_public_result once, then finish. No scientific claim or other action.\n",0o600)
    _write_new(frontend/"task.md",b"Read the current public result once and finish this synthetic integration check.\n",0o600)
    _write_new(frontend/"prime-tree.json",_canonical(asdict(config.installed_prime_tree)),0o600)
    gate={"schema_version":"argo-house-price-a2-phase-gate-deployment/v1","context":"initial",
        "bridge_config":_binding_dict(fixture.bridge_config),"session_directory":asdict(_directory(session)),
        "cwd":str(paths["public"]),"provider":"openai-codex","model":"gpt-5.6-sol","budget":120000,
        "prior_session":None,"prior_session_id":None,"prior_cwd":None,
        "final_lock_path":str(fixture.bridge_state.path/"final-artifact-lock.json"),
        "gate_outcome_directory":asdict(_directory(paths["gate-outcomes"])),"expected_rows":292}
    gate["session_directory"]["path"]=str(session)
    gate["gate_outcome_directory"]["path"]=str(paths["gate-outcomes"])
    _write_new(frontend/"gate-config.json",_canonical(gate),0o600)
    gate_binding=_file(frontend/"gate-config.json",65536)
    interpreter=capture_interpreter_identity(KERNEL,Path(KERNEL).parent.parent/"pyvenv.cfg")
    bridge_entry=write_module_bootstrap(frontend/"bridge-entry.py",config.namespace_tree,interpreter,MODULE+"bridge",fixture.bridge_config)
    gate_entry=write_module_bootstrap(frontend/"gate-entry.py",config.namespace_tree,interpreter,MODULE+"phase_gate",gate_binding)
    extension=_file(frontend/"controller-extension.ts",1048576,EXTENSION_SHA256)
    binding=write_extension_binding(extension,bridge_entry)
    assets={"prime_entry":_file(PRIME_ENTRY,1048576),"prime_closure_manifest":_file(frontend/"prime-tree.json",65536),
        "controller_main":_file(frontend/"controller-main.ts",1048576,NORMAL_SHA256),
        "frontend_closure_manifest":_file(frontend/"controller-extension.closure.json",65536),
        "extension":extension,"binding":binding,"settings":_file(paths["profile"]/"settings.json",65536),
        "system_prompt":_file(frontend/"system.md",131072),"task_prompt":_file(frontend/"task.md",131072),
        "autonomous_gate":gate_entry,"node_executable":_file(Path("/opt/homebrew/bin/node").resolve(),268435456)}
    directories={"artifact_root":artifact,"cwd":paths["public"],"profile":paths["profile"],"session_dir":session,"temporary_dir":temporary}
    deployment=write_frontend_deployment(artifact/"deployment.json",FrontendDeploymentInput(assets,interpreter,directories,"dev"))
    frontend_tree=capture_tree(frontend,TREE_LIMITS)
    executor=_file(Path(config.namespace_tree.root)/PREFIX/"process_exec.py",1048576,EXEC_SHA256)
    normal=write_process_config(paths["control"]/"normal-process-config.json",deployment,executor,started_ns)
    normal_value=_gate_json(_gate_read(normal.path,65536,normal.sha256,normal.bytes,normal.mtime_ns_max))
    normal_config=RunControllerConfig.from_dict(normal_value)
    faux=_file(frontend/FAUX_RELATIVE,1048576,config.expected_faux_frontend_sha256)
    synthetic=replace(normal_config,frontend_path=str(faux.path),frontend_identity=capture_path_identity(faux.path,hash_file=True,max_file_bytes=1048576))
    if synthetic.frontend_identity.sha256!=faux.sha256:raise CaseError()
    _validate_config(synthetic)
    synthetic_binding=_publish(_directory(paths["control"]),"synthetic-process-config.json",config_to_dict(synthetic),CONTROL_FILES,131072)
    verify_tree(frontend,frontend_tree,TREE_LIMITS)
    return _PreparedEnvironment(normal,synthetic_binding,synthetic,gate_binding,faux,frontend_tree,
                                _directory(session),str(paths["public"]),artifact)


def _capture_final_directories(prepared: _PreparedEnvironment, fixture: CombinationFixture,
                               evidence: DirectoryIdentity) -> tuple[DirectoryIdentity,...]:
    identities=(evidence,prepared.session_directory,
        DirectoryIdentity(prepared.artifact_root,prepared.process_config.artifact_root_identity.device,
                          prepared.process_config.artifact_root_identity.inode),
        DirectoryIdentity(Path(prepared.frontend_tree.root),prepared.frontend_tree.root_device,
                          prepared.frontend_tree.root_inode),
        _directory(prepared.normal_process.path.parent),_directory(fixture.bridge_config.path.parent))
    for item in identities:
        descriptor=os.open(item.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:_assert_directory(descriptor,item)
        finally:os.close(descriptor)
    return identities


def _reopen_final_references(expectation: CombinationExpectation, fixture: CombinationFixture,
                              directories: tuple[DirectoryIdentity,...], *, sync_metadata: bool=False) -> None:
    held=[]
    try:
        for identity in directories:
            descriptor=os.open(identity.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            held.append((descriptor,identity));_assert_directory(descriptor,identity)
        for binding,cap in ((expectation.normal_process_config,65536),(expectation.synthetic_process_config,65536),
                            (expectation.process_receipt,1048576),(expectation.gate_config,65536),
                            (fixture.bridge_config,65536),(expectation.synthetic_frontend,1048576),
                            (expectation.metadata,4096),(expectation.current_session,8388608)):
            if type(binding) is not FileBinding:raise CaseError()
            if not any(identity.path in binding.path.parents for _,identity in held):raise CaseError()
            _gate_read(binding.path,cap,binding.sha256,binding.bytes,binding.mtime_ns_max)
        if sync_metadata:
            metadata=expectation.metadata
            parent=next((fd for fd,identity in held if identity.path==metadata.path.parent),None)
            if parent is None or metadata.path.name!="a2-synthetic-provider-metadata.json":raise CaseError()
            descriptor=os.open(metadata.path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
            try:
                info=os.fstat(descriptor)
                if (not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=os.getuid() or
                        stat.S_IMODE(info.st_mode)!=0o600 or info.st_size!=metadata.bytes or
                        info.st_mtime_ns>metadata.mtime_ns_max):raise CaseError()
                os.fsync(descriptor)
                current=os.stat(metadata.path.name,dir_fd=parent,follow_symlinks=False)
                if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(
                        current.st_dev,current.st_ino,current.st_size,current.st_mtime_ns,current.st_ctime_ns):
                    raise CaseError()
            finally:os.close(descriptor)
            os.fsync(parent)
            _gate_read(metadata.path,4096,metadata.sha256,metadata.bytes,metadata.mtime_ns_max)
        for descriptor,identity in held:_assert_directory(descriptor,identity)
    finally:
        for descriptor,_ in reversed(held):os.close(descriptor)


def _revalidate_final(config: CombinationCaseConfig, expectation: CombinationExpectation,
                      fixture: CombinationFixture, directories: tuple[DirectoryIdentity,...],
                      original: CombinationAssessment) -> None:
    _verify_protected_roots(config.case_root,config.protected_roots)
    _reopen_final_references(expectation,fixture,directories,sync_metadata=True)
    _verify_sources(config)
    repeated=assess_combination(expectation)
    if (type(repeated) is not CombinationAssessment or repeated!=original or repeated.status!="PASS" or
            repeated.reason!="VERIFIED_SYNTHETIC_COMBINATION"):raise CaseError()
    _reopen_final_references(expectation,fixture,directories)
    _verify_protected_roots(config.case_root,config.protected_roots)


def _close_is_confirmed(result: object) -> bool:
    return (type(result) is FixtureCloseResult and result.schema_version=="argo-house-price-a2-fixture-close/v1" and
            result.confirmed is True and result.shutdown_completed is True and result.serve_thread_stopped is True and
            result.socket_closed is True and result.cleanup_thread_stopped is True and result.timed_out is False and
            result.error is None and type(result.elapsed_seconds) is float and math.isfinite(result.elapsed_seconds) and
            0<=result.elapsed_seconds<=2.0)


def run_case(config: CombinationCaseConfig) -> CombinationCaseResult:
    stage="INPUT";reason="INVALID_INPUT";status="NOT_STARTED";context=None;attempts=0
    try:
        started=time.monotonic();started_ns=time.monotonic_ns()
        if (type(started) not in (int,float) or not math.isfinite(started) or started<0 or
                type(started_ns) is not int or started_ns<=0):raise CaseError()
        if (type(config) is not CombinationCaseConfig or not isinstance(config.case_root,Path) or
                any(type(value) is not str or HEX64.fullmatch(value) is None for value in (
                    config.expected_faux_frontend_sha256,config.expected_fixture_module_sha256,config.expected_acceptance_module_sha256))):raise CaseError()
        if os.path.lexists(config.case_root):return CombinationCaseResult("NOT_STARTED","INPUT","ALREADY_ATTEMPTED",None,0,None)
        _new_private_path(config.case_root)
        _verify_protected_roots(config.case_root,config.protected_roots)
    except Exception:return CombinationCaseResult(status,stage,reason,None,0,None)
    try:_verify_sources(config)
    except Exception:return CombinationCaseResult("NOT_STARTED","SOURCE","SOURCE_MISMATCH",None,0,None)
    try:
        _verify_protected_roots(config.case_root,config.protected_roots)
        if _elapsed_since(started)>=160:
            return CombinationCaseResult("NOT_STARTED","SOURCE","STAGE_FAILED",None,0,None)
    except Exception:return CombinationCaseResult("NOT_STARTED","SOURCE","STAGE_FAILED",None,0,None)
    root=None;evidence=None;fixture=None;prepared=None;process_binding=None;metadata=None;current=None;session_id=None
    assessment=None;close_result=None;final_binding=None;fixture_owned=False;expectation=None;reference_directories=()
    try:
        stage="ADMISSION";reason="STAGE_FAILED";status="NOT_ADMITTED"
        config.case_root.mkdir(mode=0o700);root=_directory(config.case_root)
        _publish(root,"case-admission.json",{"schema_version":"argo-house-price-a2-synthetic-case-admission/v1",
            "case_id":"A2-Faux-C1","synthetic_only":True,"actual_P0":False,"config":_config_record(config)},
            {"case-admission.json":65536},65536)
        evidence_path=config.case_root/"evidence";evidence_path.mkdir(mode=0o700);evidence=_directory(evidence_path)
        stage="FIXTURE"
        fixture=prepare_fixture(config.case_root/"fixture");fixture_owned=True;context=fixture.context_id
        _census_case(root)
        if _elapsed_since(started)>=160:raise CaseError()
        stage="DEPLOYMENT";prepared=_prepare_environment(config,fixture,started_ns)
        reference_directories=_capture_final_directories(prepared,fixture,evidence)
        _census_case(root)
        if _elapsed_since(started)>=160:raise CaseError()
        observer=UsageObserver(UsageObserverConfig(prepared.session_directory,prepared.cwd,"openai-codex","gpt-5.6-sol",120000,()))
        abort=threading.Event();timer=threading.Timer(20,abort.set);timer.daemon=True
        stage="CONTROLLER"
        timer.start()
        try:
            attempts=1
            process=run_controller(prepared.process_config,abort_event=abort,campaign_guard=lambda:observer.observe().stop_reason)
        finally:timer.cancel()
        if type(process) is not ControllerRunReceipt:raise CaseError()
        process_binding=_publish(evidence,"controller-process-receipt.json",process.to_dict(),EVIDENCE_FILES,1114112)
        observation=observer.observe()
        current=_current_session(prepared.process_config,prepared.session_directory,observation)
        if current is None:raise CaseError()
        session_id=observation.session_id
        metadata=_file(prepared.artifact_root/"a2-synthetic-provider-metadata.json",4096)
        _census_case(root)
        if abort.is_set() or _elapsed_since(started)>=180:raise CaseError()
        stage="ACCEPTANCE"
        expectation=CombinationExpectation(context,prepared.normal_process,prepared.synthetic_process,process_binding,
            prepared.gate_config,metadata,current,session_id,prepared.synthetic_frontend,fixture.verified_dev_run_ids,
            fixture.research_sha256,(fixture.source_tree,fixture.trusted_state_tree,fixture.state_tree),config.namespace_tree,
            prepared.frontend_tree,config.installed_prime_tree,20)
        assessment=assess_combination(expectation)
        if type(assessment) is not CombinationAssessment or assessment.status!="PASS" or assessment.reason!="VERIFIED_SYNTHETIC_COMBINATION":
            reason="ASSESSMENT_REJECTED"
        else:status="VERIFIED_SYNTHETIC_COMBINATION";stage="COMPLETE";reason="VERIFIED"
    except CombinationFixtureError as error:
        close_result=error.close_result
        fixture_owned=error.base is not None or error.close_result is not None
    except Exception:
        pass
    finally:
        if fixture is not None:
            try:close_result=fixture.close()
            except Exception:close_result=None
        if fixture_owned and not _close_is_confirmed(close_result):
            status="NOT_ADMITTED";stage="CLEANUP";reason="CLEANUP_UNCONFIRMED"
        if status=="VERIFIED_SYNTHETIC_COMBINATION":
            try:
                if expectation is None or fixture is None or not reference_directories:raise CaseError()
                _revalidate_final(config,expectation,fixture,reference_directories,assessment)
            except Exception:
                status="NOT_ADMITTED";stage="ACCEPTANCE";reason="STAGE_FAILED"
        if evidence is not None:
            try:
                _verify_protected_roots(config.case_root,config.protected_roots)
                _census_case(root)
                elapsed=_elapsed_since(started)
                if not math.isfinite(elapsed) or elapsed<0:raise CaseError()
                if elapsed>=180:
                    status="NOT_ADMITTED";reason="STAGE_FAILED"
                payload={"schema_version":"argo-house-price-a2-synthetic-combination-case/v2","case_id":"A2-Faux-C1",
                    "synthetic_only":True,"production_entry_executed":False,"actual_P0":False,"status":status,"stage":stage,
                    "reason":reason,"context_id":context,"process_attempts":attempts,"source_bindings":_config_record(config),
                    "normal_process_config":_binding_dict(prepared.normal_process) if prepared else None,
                    "synthetic_process_config":_binding_dict(prepared.synthetic_process) if prepared else None,
                    "process_receipt":_binding_dict(process_binding),"gate_config":_binding_dict(prepared.gate_config) if prepared else None,
                    "metadata":_binding_dict(metadata),"current_session":_binding_dict(current),"current_session_id":session_id,
                    "assessment":asdict(assessment) if type(assessment) is CombinationAssessment else None,
                    "elapsed_seconds":elapsed,"cleanup_confirmed":_close_is_confirmed(close_result),
                    "fixture_close_result":asdict(close_result) if type(close_result) is FixtureCloseResult else None,"limitations":list(LIMITATIONS)}
                final_binding=_publish(evidence,"case-receipt.json",payload,EVIDENCE_FILES,1114112)
                if status=="VERIFIED_SYNTHETIC_COMBINATION":
                    _reopen_final_references(expectation,fixture,reference_directories)
                    _verify_protected_roots(config.case_root,config.protected_roots)
                    if _elapsed_since(started)>=180:raise CaseError()
            except Exception:
                status="NOT_ADMITTED";reason="STAGE_FAILED";final_binding=None
    return CombinationCaseResult(status,stage,reason,final_binding,attempts,context)


def _load_case_config(path: Path, digest: str) -> CombinationCaseConfig:
    if type(digest) is not str or HEX64.fullmatch(digest) is None:raise CaseError()
    data=_gate_read(path,65536,digest)
    value=_gate_json(data)
    required={field.name for field in fields(CombinationCaseConfig)}|{"schema_version"}
    if type(value) is not dict or set(value)!=required or value.pop("schema_version")!=CONFIG_SCHEMA:raise CaseError()
    if type(value["case_root"]) is not str:raise CaseError()
    value["case_root"]=Path(value["case_root"])
    for name in ("namespace_tree","frontend_seed_tree","installed_prime_tree"):
        if type(value[name]) is not dict or set(value[name])!={field.name for field in fields(SourceTree)}:raise CaseError()
        value[name]=SourceTree(**value[name])
    roots=value["protected_roots"]
    if type(roots) is not dict or set(roots)!={field.name for field in fields(CaseProtectedRoots)}:raise CaseError()
    protected={}
    for name,identity in roots.items():
        if (type(identity) is not dict or set(identity)!={"path","device","inode"} or
                type(identity["path"]) is not str):raise CaseError()
        protected[name]=DirectoryIdentity(Path(identity["path"]),identity["device"],identity["inode"])
    value["protected_roots"]=CaseProtectedRoots(**protected)
    return CombinationCaseConfig(**value)


def main(argv: Sequence[str] | None=None) -> int:
    values=list(sys.argv[1:] if argv is None else argv)
    try:
        if len(values)!=4 or values[0]!="--config" or values[2]!="--config-sha256":raise CaseError()
        result=run_case(_load_case_config(Path(values[1]),values[3]))
        output=asdict(result);output["receipt"]=_binding_dict(result.receipt)
        print(_canonical(output).decode("ascii"))
        return 0 if result.status=="VERIFIED_SYNTHETIC_COMBINATION" else 1
    except Exception:
        print("COMBINATION_CASE_INVALID",file=sys.stderr)
        return 2


if __name__=="__main__":raise SystemExit(main())
