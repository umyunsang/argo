from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime import controller_deployment as deployment
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.controller_deployment import (
    DeploymentConfigError,
    _revalidate_frontend_deployment,
    write_frontend_deployment,
    write_process_config,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_controller_deployment import (
    ControllerDeploymentTest,
    bind,
)

RESULTS: dict[str, object] = {}
HERE = Path(__file__).parent.joinpath(
    "source-copy/experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime"
).resolve()


def fixture():
    value = ControllerDeploymentTest(methodName="test_extension_binding_is_fixed_bounded_and_no_overwrite")
    value.setUp()
    return value


def bootstrap_provenance() -> None:
    value = fixture()
    try:
        spec = value.spec()
        manifest_path = value.extension.path.with_name("controller-extension.closure.json")
        manifest = json.loads(manifest_path.read_bytes())
        assert set(manifest) == {"schema_version", "extension", "binding", "bridge_bootstrap"}
        assert manifest["schema_version"] == "argo-house-price-a2-extension-provenance/v1"
        assert manifest["bridge_bootstrap"]["sha256"] == value.bootstrap.sha256
        assert manifest["binding"]["sha256"] == spec.assets["binding"].sha256
        value.bootstrap.path.write_bytes(b"#!/usr/bin/false\n# replacement\n")
        output = value.artifact / "rejected-bootstrap.json"
        rejected = False
        try:
            write_frontend_deployment(output, spec)
        except DeploymentConfigError:
            rejected = True
        assert rejected and not output.exists()
        RESULTS["I1_bootstrap_replacement"] = {
            "manifest_exact": True,
            "replacement_rejected": True,
            "no_output": True,
        }
    finally:
        value.tearDown()


def file_reseal_race() -> None:
    value = fixture()
    try:
        spec = value.spec()
        receipt = write_frontend_deployment(value.artifact / "deployment.json", spec)
        target = spec.assets["controller_main"].path
        real_capture = deployment.capture_path_identity
        mutated = False
        def replace_before_capture(path, **kwargs):
            nonlocal mutated
            if Path(path) == target and not mutated:
                mutated = True
                target.write_bytes(b"export const changed = 999;\n")
            return real_capture(path, **kwargs)
        output = value.root / "rejected-process.json"
        rejected = False
        with patch.object(deployment, "capture_path_identity", side_effect=replace_before_capture):
            try:
                write_process_config(output, receipt, bind(HERE / "process_exec.py"), 1)
            except DeploymentConfigError:
                rejected = True
        assert mutated and rejected and not output.exists()
        RESULTS["I2_after_read_mutation"] = {
            "mutation_reached_capture": True,
            "replacement_rejected": True,
            "no_output": True,
        }
    finally:
        value.tearDown()


def output_disjointness() -> None:
    value = fixture()
    try:
        spec = value.spec()
        output = value.directories["temporary_dir"] / "deployment.json"
        rejected = False
        try:
            write_frontend_deployment(output, spec)
        except DeploymentConfigError:
            rejected = True
        assert rejected and not output.exists()
        RESULTS["I3_frontend_in_tmp"] = {"rejected": True, "no_output": True}
    finally:
        value.tearDown()

    value = fixture()
    try:
        spec = value.spec()
        frontend_path = value.artifact / "deployment.json"
        receipt = write_frontend_deployment(frontend_path, spec)
        output = value.directories["profile"] / "process.json"
        rejected = False
        try:
            write_process_config(output, receipt, bind(HERE / "process_exec.py"), 1)
        except DeploymentConfigError:
            rejected = True
        assert rejected and not output.exists()
        _revalidate_frontend_deployment(frontend_path, json.loads(frontend_path.read_bytes()))
        RESULTS["I3_process_in_profile"] = {
            "rejected": True,
            "no_output": True,
            "frontend_still_valid": True,
        }
    finally:
        value.tearDown()


def successful_publication_remains_valid() -> None:
    value = fixture()
    try:
        spec = value.spec()
        frontend_path = value.artifact / "deployment.json"
        receipt = write_frontend_deployment(frontend_path, spec)
        _revalidate_frontend_deployment(frontend_path, json.loads(frontend_path.read_bytes()))
        result = write_process_config(value.root / "process.json", receipt, bind(HERE / "process_exec.py"), 1)
        _revalidate_frontend_deployment(frontend_path, json.loads(frontend_path.read_bytes()))
        assert result.path.exists()
        assert list(value.directories["session_dir"].iterdir()) == []
        assert list(value.directories["temporary_dir"].iterdir()) == []
        RESULTS["positive_control"] = {
            "frontend_revalidates_after_process_publication": True,
            "session_empty": True,
            "temporary_empty": True,
        }
    finally:
        value.tearDown()


bootstrap_provenance()
file_reseal_race()
output_disjointness()
successful_publication_remains_valid()
print(json.dumps(RESULTS, indent=2, sort_keys=True))
