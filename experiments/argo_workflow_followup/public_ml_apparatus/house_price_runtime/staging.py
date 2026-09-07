"""Read the selected private copy through the frozen TrustedIo output contract."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.grading import FileBinding, GradingError, read_bound
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.trusted_io import FinalSelection


@dataclass(frozen=True)
class DirectoryIdentity:
    path: Path
    device: int
    inode: int


class StagingError(ValueError):
    def __init__(self):
        super().__init__("SELECTED_CODE_INVALID")


def read_selected_code(state_root: DirectoryIdentity, selection: FinalSelection) -> bytes:
    if (not isinstance(state_root, DirectoryIdentity) or not isinstance(state_root.path, Path) or
            type(state_root.device) is not int or type(state_root.inode) is not int or
            state_root.device < 0 or state_root.inode <= 0 or not isinstance(selection,FinalSelection) or
            not isinstance(selection.code_sha256,str) or re.fullmatch(r"[0-9a-f]{64}",selection.code_sha256) is None):
        raise StagingError()
    root=state_root.path
    try:
        if not root.is_absolute() or ".." in root.parts or root.resolve(strict=True)!=root:
            raise StagingError()
        before=root.lstat()
        if not stat.S_ISDIR(before.st_mode) or (before.st_dev,before.st_ino)!=(state_root.device,state_root.inode):
            raise StagingError()
        path=root/"final-solution.py"
        info=path.lstat()
        binding=FileBinding(path,selection.code_sha256,info.st_size,info.st_mtime_ns)
        data=read_bound(binding,131072)
        after=root.lstat()
        if (after.st_dev,after.st_ino)!=(state_root.device,state_root.inode):
            raise StagingError()
        return data
    except (OSError,ValueError,GradingError,RuntimeError):
        raise StagingError() from None
