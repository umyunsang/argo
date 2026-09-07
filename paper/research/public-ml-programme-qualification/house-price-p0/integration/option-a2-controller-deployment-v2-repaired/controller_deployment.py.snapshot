"""Root-only producers for exact A2 frontend and process configuration files."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Mapping

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_process import (
    FROZEN_PRODUCTION_CAPS, InterpreterIdentity, PathIdentity, RunControllerCaps, RunControllerConfig,
    capture_interpreter_identity, capture_path_identity, config_to_dict, _validate_config,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.deployment_assets import _new_private_path, _write_new
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.phase_gate import _gate_json, _gate_read

KERNEL="/Users/um-yunsang/.prime/agent/kernel-venv/bin/python"
PRIME="/opt/homebrew/lib/node_modules/prime-agent/dist/index.js"
NODE=str(Path("/opt/homebrew/bin/node").resolve())
ASSET_KEYS=frozenset({"prime_entry","prime_closure_manifest","controller_main","frontend_closure_manifest",
    "extension","binding","settings","system_prompt","task_prompt","autonomous_gate","node_executable"})
DIRECTORY_KEYS=frozenset({"artifact_root","cwd","profile","session_dir","temporary_dir"})
TOOLS=("read_solution","write_solution","request_R1_run","read_public_result","read_dev_result","lock_final_artifact")
EXTENSION_LIMITS={"maxRequestBytes":262144,"maxResponseBytes":262144,"maxListItems":5,
    "maxSourceContentBytes":131072,"maxPathBytes":32,"maxMetricAbs":1000000000000,
    "maxMetricDecimalPlaces":6,"maxRows":292,"bridgeTimeoutMs":30000}
FRONTEND_LIMITS={"provider_timeout_ms":120000,"provider_retries":0,"phase_wall_seconds":3600,
    "campaign_wall_seconds":10800,"cpu_seconds_per_process":600,"file_size_bytes":8388608,
    "rss_trigger_bytes":2147483648,"rss_sample_ms":250,"v8_old_space_mib":1024,
    "model_tokens_between_turns":120000,"controller_turn_limit_per_phase":20,"source_text_max_bytes":131072,
    "bridge_close_grace_ms":1000,"autonomous_max_continuations":20,"autonomous_gate_retries":20,"autonomous_gate_timeout_ms":30000}


class DeploymentConfigError(ValueError):
    def __init__(self):super().__init__("DEPLOYMENT_CONFIG_INVALID")


@dataclass(frozen=True)
class FrontendDeploymentInput:
    assets: Mapping[str,FileBinding]
    kernel_interpreter: InterpreterIdentity
    directories: Mapping[str,Path]
    phase: str
    model: str="openai-codex/gpt-5.6-sol"
    thinking: str="xhigh"


def _data(binding: FileBinding, cap: int) -> bytes:
    if (not isinstance(binding,FileBinding) or type(binding.bytes) is not int or not 0<binding.bytes<=cap or
            type(binding.mtime_ns_max) is not int or not 0<=binding.mtime_ns_max<=2**63-1 or
            type(binding.sha256) is not str or re.fullmatch(r"[0-9a-f]{64}",binding.sha256) is None):
        raise DeploymentConfigError()
    return _gate_read(binding.path,cap,binding.sha256,binding.bytes,binding.mtime_ns_max)


def _seal(binding: FileBinding) -> dict[str,object]:
    return {"path":str(binding.path),"sha256":binding.sha256,"bytes":binding.bytes,"mtime_ns_max":str(binding.mtime_ns_max)}


def _capture_binding(binding: FileBinding, cap: int, *, private_executable: bool=False) -> PathIdentity:
    _data(binding,cap)
    current=capture_path_identity(binding.path,hash_file=True,max_file_bytes=cap)
    if (current.resolved_path!=str(binding.path) or current.path_kind!="regular_file" or
            current.sha256!=binding.sha256 or current.size!=binding.bytes or
            current.mtime_ns_max>binding.mtime_ns_max):
        raise DeploymentConfigError()
    if private_executable:
        _directory(binding.path.parent,False)
        if current.uid!=os.getuid() or current.mode!=0o700:raise DeploymentConfigError()
    return replace(current,mtime_ns_max=binding.mtime_ns_max)


def _binding_from_seal(seal: object) -> FileBinding:
    if (type(seal) is not dict or set(seal)!={"path","sha256","bytes","mtime_ns_max"} or
            type(seal["path"]) is not str or type(seal["mtime_ns_max"]) is not str or
            re.fullmatch(r"(?:0|[1-9][0-9]{0,18})",seal["mtime_ns_max"]) is None):
        raise DeploymentConfigError()
    return FileBinding(Path(seal["path"]),seal["sha256"],seal["bytes"],int(seal["mtime_ns_max"]))


def _verify_binding_manifest(manifest: FileBinding, extension: FileBinding, binding: FileBinding) -> PathIdentity:
    expected_path=extension.path.with_name("controller-extension.closure.json")
    if manifest.path!=expected_path:raise DeploymentConfigError()
    value=_gate_json(_data(manifest,65536))
    if (type(value) is not dict or set(value)!={"schema_version","extension","binding","bridge_bootstrap"} or
            value["schema_version"]!="argo-house-price-a2-extension-provenance/v1" or
            json_bytes(value["extension"])!=json_bytes(_seal(extension)) or
            json_bytes(value["binding"])!=json_bytes(_seal(binding))):
        raise DeploymentConfigError()
    _data(extension,1048576)
    runtime=_gate_json(_data(binding,65536))
    expected=PathIdentity.from_dict(value["bridge_bootstrap"])
    original=FileBinding(Path(expected.resolved_path),expected.sha256,expected.size,expected.mtime_ns_max)
    current=_capture_binding(original,16384,private_executable=True)
    if json_bytes(asdict(current))!=json_bytes(asdict(expected)):
        raise DeploymentConfigError()
    if (type(runtime) is not dict or runtime.get("bridge")!={"command":str(original.path),"argv":[]}):
        raise DeploymentConfigError()
    return expected


def _path_seal(path: Path, cap: int) -> dict[str,object]:
    identity=capture_path_identity(path,hash_file=True,max_file_bytes=cap)
    return {"path":identity.resolved_path,"sha256":identity.sha256,"bytes":identity.size,"mtime_ns_max":str(identity.mtime_ns_max)}


def _directory(path: Path, empty: bool) -> dict[str,object]:
    if not isinstance(path,Path) or not path.is_absolute() or ".." in path.parts or path.resolve(strict=True)!=path:
        raise DeploymentConfigError()
    info=path.lstat()
    if (not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o700 or info.st_uid!=os.getuid() or
            empty and any(path.iterdir())):raise DeploymentConfigError()
    return {"path":str(path),"realpath":str(path),"device":str(info.st_dev),"inode":str(info.st_ino),
            "mtime_ns_max":str(info.st_mtime_ns),"mode_octal":"0700","must_be_empty":empty}


def _publish(path: Path, value: object) -> FileBinding:
    _new_private_path(path)
    data=json_bytes(value)
    if not 0<len(data)<=65536:raise DeploymentConfigError()
    _write_new(path,data,0o600)
    binding=FileBinding(path,hashlib.sha256(data).hexdigest(),len(data),path.lstat().st_mtime_ns)
    _data(binding,65536)
    return binding


def json_bytes(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()


def write_extension_binding(extension: FileBinding, bridge_bootstrap: FileBinding) -> FileBinding:
    try:
        _capture_binding(extension,1048576)
        bootstrap=_capture_binding(bridge_bootstrap,16384,private_executable=True)
        binding_path=extension.path.with_name("controller-extension.binding.json")
        manifest_path=extension.path.with_name("controller-extension.closure.json")
        _new_private_path(binding_path);_new_private_path(manifest_path)
        value={"schemaVersion":"argo-house-price-controller-extension-binding/v1",
               "expectedExtensionSha256":extension.sha256,
               "bridge":{"command":str(bridge_bootstrap.path),"argv":[]},"limits":EXTENSION_LIMITS}
        binding=_publish(binding_path,value)
        manifest=_publish(manifest_path,{"schema_version":"argo-house-price-a2-extension-provenance/v1",
            "extension":_seal(extension),"binding":_seal(binding),"bridge_bootstrap":asdict(bootstrap)})
        _verify_binding_manifest(manifest,extension,binding)
        return binding
    except Exception:raise DeploymentConfigError() from None


def _prepare_frontend_deployment(path: Path, spec: FrontendDeploymentInput) -> dict[str,object]:
    try:
        if (not isinstance(spec,FrontendDeploymentInput) or set(spec.assets)!=ASSET_KEYS or
                set(spec.directories)!=DIRECTORY_KEYS or spec.phase not in ("dev","final_refit") or
                spec.model!="openai-codex/gpt-5.6-sol" or spec.thinking!="xhigh"):
            raise DeploymentConfigError()
        assets=spec.assets;dirs=spec.directories
        for key,binding in assets.items():_data(binding,268435456 if key=="node_executable" else 1048576)
        if assets["prime_entry"].path!=Path(PRIME) or assets["node_executable"].path!=Path(NODE):raise DeploymentConfigError()
        if assets["settings"].path!=dirs["profile"]/"settings.json" or assets["binding"].path!=assets["extension"].path.with_name("controller-extension.binding.json"):
            raise DeploymentConfigError()
        _verify_binding_manifest(assets["frontend_closure_manifest"],assets["extension"],assets["binding"])
        settings=_gate_json(_data(assets["settings"],65536))
        expected={"retry":{"enabled":False,"provider":{"timeoutMs":120000,"maxRetries":0}}}
        if settings!=expected or settings["retry"]["enabled"] is not False or any(type(settings["retry"]["provider"][k]) is not int for k in ("timeoutMs","maxRetries")):
            raise DeploymentConfigError()
        binding=_gate_json(_data(assets["binding"],65536))
        if (not isinstance(binding,dict) or set(binding)!={"schemaVersion","expectedExtensionSha256","bridge","limits"} or
                binding["schemaVersion"]!="argo-house-price-controller-extension-binding/v1" or
                binding["expectedExtensionSha256"]!=assets["extension"].sha256 or binding["limits"]!=EXTENSION_LIMITS or
                not isinstance(binding["bridge"],dict) or set(binding["bridge"])!={"command","argv"} or
                binding["bridge"]["argv"]!=[] or not Path(binding["bridge"]["command"]).is_absolute()):
            raise DeploymentConfigError()
        for key in ("system_prompt","task_prompt"):
            data=_data(assets[key],131072);text=data.decode("utf-8")
            if not text.strip() or "\0" in text:raise DeploymentConfigError()
        gate=assets["autonomous_gate"].path
        if re.fullmatch(r"[A-Za-z0-9_./-]+",str(gate)) is None or gate.stat().st_mode&0o111==0:raise DeploymentConfigError()
        if not isinstance(spec.kernel_interpreter,InterpreterIdentity) or spec.kernel_interpreter.invocation_path!=KERNEL:
            raise DeploymentConfigError()
        interpreter=capture_interpreter_identity(KERNEL,Path(KERNEL).parent.parent/"pyvenv.cfg")
        if interpreter!=spec.kernel_interpreter:raise DeploymentConfigError()
        link=Path(KERNEL).lstat()
        if not stat.S_ISLNK(link.st_mode):raise DeploymentConfigError()
        if (dirs["temporary_dir"]!=dirs["artifact_root"]/"tmp" or
                dirs["artifact_root"] not in dirs["session_dir"].parents or dirs["session_dir"]==dirs["temporary_dir"] or
                dirs["profile"]==dirs["artifact_root"] or dirs["artifact_root"] in dirs["profile"].parents or
                path.parent!=dirs["artifact_root"] or len(set(dirs.values()))!=5 or
                any(path==dirs[key] or dirs[key] in path.parents for key in ("cwd","profile","session_dir","temporary_dir"))):
            raise DeploymentConfigError()
        for ancestor in (dirs["cwd"],*dirs["cwd"].parents):
            if (ancestor/".git").exists():raise DeploymentConfigError()
        if (dirs["cwd"]/".prime").exists() or any(p.name not in {"auth.json","settings.json"} for p in dirs["profile"].iterdir()):
            raise DeploymentConfigError()
        directory_seals={key:_directory(value,key in {"session_dir","temporary_dir"}) for key,value in dirs.items()}
        environment={"PRIME_AGENT_CODING_AGENT_DIR":str(dirs["profile"]),"PRIME_AGENT_KERNEL_PYTHON":KERNEL,
            "PRIME_AGENT_TELEMETRY":"0","PATH":"/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
            "TMPDIR":str(dirs["temporary_dir"])+"/","LANG":"C.UTF-8","LC_ALL":"C.UTF-8","TZ":"UTC"}
        seals={key:_seal(value) for key,value in assets.items()}
        seals["kernel_interpreter"]={"invocation_path":KERNEL,
            "invocation_link":{"device":str(link.st_dev),"inode":str(link.st_ino),"mtime_ns_max":str(link.st_mtime_ns),"link_target":os.readlink(KERNEL)},
            "resolved_target":_seal(FileBinding(Path(interpreter.resolved_target.resolved_path),interpreter.resolved_target.sha256,
                interpreter.resolved_target.size,interpreter.resolved_target.mtime_ns_max)),
            "pyvenv_cfg":_seal(FileBinding(Path(interpreter.pyvenv_cfg_path),interpreter.pyvenv_cfg.sha256,
                interpreter.pyvenv_cfg.size,interpreter.pyvenv_cfg.mtime_ns_max))}
        value={"schema_version":"argo-house-price-a2-controller-main-deployment/v1","status":"TRUSTED_FIXED_DEPLOYMENT",
            "assets":seals,"directories":directory_seals,"runtime":{"phase":spec.phase,"model":spec.model,"thinking":spec.thinking,
            "mode":"text","print":True,"offline":True,"fresh_session":True,"tools":list(TOOLS)},
            "environment":{"exact":environment,"home_must_be_unset":True,"forbidden_prefixes":["PRIME_AGENT_INTERNAL_"]},"limits":FRONTEND_LIMITS}
        return value
    except Exception:raise DeploymentConfigError() from None


def write_frontend_deployment(path: Path, spec: FrontendDeploymentInput) -> FileBinding:
    try:
        value=_prepare_frontend_deployment(path,spec)
        binding=_publish(path,value)
        _revalidate_frontend_deployment(path,_gate_json(_data(binding,65536)))
        return binding
    except Exception:raise DeploymentConfigError() from None


def _revalidate_frontend_deployment(path: Path, value: object) -> None:
    if (type(value) is not dict or set(value)!={"schema_version","status","assets","directories","runtime","environment","limits"} or
            type(value["assets"]) is not dict or set(value["assets"])!=ASSET_KEYS|{"kernel_interpreter"} or
            type(value["directories"]) is not dict or set(value["directories"])!=DIRECTORY_KEYS):
        raise DeploymentConfigError()
    bindings={}
    for name,seal in value["assets"].items():
        if name=="kernel_interpreter":continue
        if (type(seal) is not dict or set(seal)!={"path","sha256","bytes","mtime_ns_max"} or
                type(seal["path"]) is not str or type(seal["mtime_ns_max"]) is not str or
                re.fullmatch(r"(?:0|[1-9][0-9]{0,18})",seal["mtime_ns_max"]) is None):
            raise DeploymentConfigError()
        bindings[name]=FileBinding(Path(seal["path"]),seal["sha256"],seal["bytes"],int(seal["mtime_ns_max"]))
    directories={name:Path(seal["path"]) for name,seal in value["directories"].items()}
    interpreter=capture_interpreter_identity(KERNEL,Path(KERNEL).parent.parent/"pyvenv.cfg")
    runtime=value["runtime"]
    actual=_prepare_frontend_deployment(path,FrontendDeploymentInput(bindings,interpreter,directories,
            runtime["phase"],runtime["model"],runtime["thinking"]))
    for name,seal in value["directories"].items():
        current=actual["directories"][name]
        if (type(seal) is not dict or set(seal)!=set(current) or type(seal["mtime_ns_max"]) is not str or
                re.fullmatch(r"(?:0|[1-9][0-9]{0,18})",seal["mtime_ns_max"]) is None):
            raise DeploymentConfigError()
        if name!="artifact_root" and int(current["mtime_ns_max"])>int(seal["mtime_ns_max"]):
            raise DeploymentConfigError()
        current["mtime_ns_max"]=seal["mtime_ns_max"]
    # Canonical bytes distinguish booleans from numeric values and unknown fields.
    if json_bytes(actual)!=json_bytes(value):raise DeploymentConfigError()


def write_process_config(path: Path, frontend_deployment: FileBinding, process_exec: FileBinding,
                         campaign_started_monotonic_ns: int) -> FileBinding:
    try:
        deployment=_gate_json(_data(frontend_deployment,65536));_data(process_exec,1048576)
        _revalidate_frontend_deployment(frontend_deployment.path,deployment)
        dirs={key:Path(value["path"]) for key,value in deployment["directories"].items()}
        assets=deployment["assets"]
        bootstrap=_verify_binding_manifest(_binding_from_seal(assets["frontend_closure_manifest"]),
                    _binding_from_seal(assets["extension"]),_binding_from_seal(assets["binding"]))
        protected=tuple(dirs.values())+tuple(Path(value["path"]).parent for name,value in assets.items()
                    if name!="kernel_interpreter")+(process_exec.path.parent,Path(bootstrap.resolved_path).parent)
        if any(path==root or root in path.parents for root in protected):raise DeploymentConfigError()
        for name,value in assets.items():
            if name=="kernel_interpreter":continue
            _data(_binding_from_seal(value),268435456 if name=="node_executable" else 1048576)
        interpreter=capture_interpreter_identity(KERNEL,Path(KERNEL).parent.parent/"pyvenv.cfg")
        kernel=assets["kernel_interpreter"]
        if (json_bytes(_seal(FileBinding(Path(interpreter.resolved_target.resolved_path),interpreter.resolved_target.sha256,
                interpreter.resolved_target.size,interpreter.resolved_target.mtime_ns_max)))!=json_bytes(kernel["resolved_target"]) or
                json_bytes(_seal(FileBinding(Path(interpreter.pyvenv_cfg_path),interpreter.pyvenv_cfg.sha256,
                interpreter.pyvenv_cfg.size,interpreter.pyvenv_cfg.mtime_ns_max)))!=json_bytes(kernel["pyvenv_cfg"])):
            raise DeploymentConfigError()
        executor_identity=_capture_binding(process_exec,1048576)
        node_identity=_capture_binding(_binding_from_seal(assets["node_executable"]),268435456)
        frontend_identity=_capture_binding(_binding_from_seal(assets["controller_main"]),1048576)
        deployment_identity=_capture_binding(frontend_deployment,65536)
        def directory_identity(value):return capture_path_identity(value,hash_file=False)
        config=RunControllerConfig(
            KERNEL,interpreter,str(process_exec.path),executor_identity,
            assets["node_executable"]["path"],node_identity,
            assets["controller_main"]["path"],frontend_identity,
            str(frontend_deployment.path),deployment_identity,
            str(dirs["artifact_root"]),directory_identity(dirs["artifact_root"]),
            str(dirs["temporary_dir"]),directory_identity(dirs["temporary_dir"]),
            str(dirs["session_dir"]),directory_identity(dirs["session_dir"]),
            str(dirs["profile"]),directory_identity(dirs["profile"]),
            deployment["environment"]["exact"],RunControllerCaps(**FROZEN_PRODUCTION_CAPS,
                terminate_grace_seconds=2,kill_grace_seconds=2,observer_timeout_seconds=3),
            campaign_started_monotonic_ns,False)
        _data(frontend_deployment,65536)
        _revalidate_frontend_deployment(frontend_deployment.path,deployment)
        _validate_config(config)
        result=_publish(path,config_to_dict(config))
        _data(frontend_deployment,65536)
        _revalidate_frontend_deployment(frontend_deployment.path,deployment)
        _validate_config(config)
        return result
    except Exception:raise DeploymentConfigError() from None
