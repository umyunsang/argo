"""Observe one root-selected native session directory with bounded file reads.

Stops are sticky. Unknown usage is never a grant of free model calls. This observer
is sampled; it does not impose provider backpressure or a current-response cap.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.campaign_usage import (
    MAX_COUNTER, MAX_SESSION_BYTES, UUID, SessionUsage, UsageError, combine_usage, parse_session_usage,
)
from experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.staging import DirectoryIdentity


class UsageObservationError(ValueError):
    def __init__(self):
        super().__init__("USAGE_OBSERVATION_INVALID")


@dataclass(frozen=True)
class UsageObserverConfig:
    session_directory: DirectoryIdentity
    cwd: str
    provider: str
    model: str
    budget: int
    prior_sessions: tuple[SessionUsage, ...]


@dataclass(frozen=True)
class UsageObservation:
    state: str
    stop_reason: str | None
    complete: bool
    current_tokens: int | None
    total_tokens: int | None
    session_id: str | None
    session_sha256: str | None
    observed_bytes: int


def _file_identity(info: os.stat_result) -> tuple[int,...]:
    return info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns


def _canonical(value: object) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()


def _integer(value: object, low: int, high: int) -> bool:
    return type(value) is int and low<=value<=high


def _digest(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}",value) is not None


def _config_digest(config: UsageObserverConfig) -> str:
    value=asdict(config)
    value["session_directory"]["path"]=str(config.session_directory.path)
    return hashlib.sha256(_canonical(value)).hexdigest()


class UsageObserver:
    def __init__(self,config: UsageObserverConfig, *, checkpoint: object=None):
        if (not isinstance(config,UsageObserverConfig) or
                not isinstance(config.session_directory,DirectoryIdentity) or
                not isinstance(config.session_directory.path,Path) or
                type(config.budget) is not int or not 0<config.budget<=120000 or
                any(not isinstance(value,str) or not value for value in (config.cwd,config.provider,config.model)) or
                not isinstance(config.prior_sessions,tuple) or len(config.prior_sessions)>1):
            raise UsageObservationError()
        identity=config.session_directory
        if type(identity.device) is not int or identity.device<0 or type(identity.inode) is not int or identity.inode<=0:
            raise UsageObservationError()
        if config.prior_sessions:
            try:
                prior=combine_usage(config.prior_sessions,config.budget)
            except UsageError:
                raise UsageObservationError() from None
            if not prior.complete or prior.total_tokens>=config.budget:
                raise UsageObservationError()
        self.config=config
        self._last: UsageObservation | None=None
        self._seen_session: str | None=None
        self._file: tuple[str,int,int] | None=None
        self._counts: tuple[int,int,int,int] | None=None
        self._prefix: tuple[int,str] | None=None
        if checkpoint is not None:
            self._restore_checkpoint(checkpoint)

    def export_checkpoint(self) -> dict[str,object]:
        return {"schema_version":"argo-house-price-a2-usage-checkpoint/v1",
                "config_sha256":_config_digest(self.config),
                "observation":asdict(self._last) if self._last is not None else None,
                "seen_session":self._seen_session,
                "file_identity":list(self._file) if self._file is not None else None,
                "counts":list(self._counts) if self._counts is not None else None,
                "prefix":{"bytes":self._prefix[0],"sha256":self._prefix[1]} if self._prefix is not None else None}

    def _restore_checkpoint(self, value: object) -> None:
        expected={"schema_version","config_sha256","observation","seen_session","file_identity","counts","prefix"}
        if (type(value) is not dict or set(value)!=expected or
                value["schema_version"]!="argo-house-price-a2-usage-checkpoint/v1" or
                value["config_sha256"]!=_config_digest(self.config)):
            raise UsageObservationError()
        try:
            if len(_canonical(value))>4096:raise UsageObservationError()
            seen,file_identity,counts,prefix=(value[key] for key in ("seen_session","file_identity","counts","prefix"))
            if seen is not None and (type(seen) is not str or UUID.fullmatch(seen) is None):
                raise UsageObservationError()
            if seen is None:
                if file_identity is not None or counts is not None or prefix is not None:raise UsageObservationError()
            elif (type(file_identity) is not list or len(file_identity)!=3 or
                    file_identity[0]!=seen+".jsonl" or not _integer(file_identity[1],0,2**64-1) or
                    not _integer(file_identity[2],1,2**64-1) or type(prefix) is not dict or
                    set(prefix)!={"bytes","sha256"} or not _integer(prefix["bytes"],1,MAX_SESSION_BYTES) or
                    not _digest(prefix["sha256"])):
                raise UsageObservationError()
            if counts is not None and (type(counts) is not list or len(counts)!=4 or
                    any(not _integer(item,0,MAX_COUNTER) for item in counts) or sum(counts)>MAX_COUNTER):
                raise UsageObservationError()
            raw=value["observation"]
            if raw is None:
                if seen is not None:raise UsageObservationError()
                last=None
            else:
                if type(raw) is not dict or set(raw)!={field.name for field in fields(UsageObservation)}:
                    raise UsageObservationError()
                last=UsageObservation(**raw)
                shapes={"WAITING_FIRST_USAGE":(None,False),"WITHIN_BUDGET":(None,True),
                        "BUDGET_EXHAUSTED":("CAMPAIGN_TOKEN_TRIGGER",True),
                        "USAGE_UNKNOWN":("CAMPAIGN_USAGE_UNKNOWN",False)}
                if (type(last.state) is not str or last.state not in shapes or type(last.complete) is not bool or
                        (last.stop_reason,last.complete)!=shapes[last.state] or last.session_id!=seen or
                        not _integer(last.observed_bytes,0,MAX_SESSION_BYTES)):
                    raise UsageObservationError()
                if prefix is None:
                    if last.session_sha256 is not None or last.observed_bytes!=0:raise UsageObservationError()
                elif last.session_sha256!=prefix["sha256"] or last.observed_bytes!=prefix["bytes"]:
                    raise UsageObservationError()
                if counts is None:
                    if last.current_tokens is not None or last.total_tokens is not None:raise UsageObservationError()
                else:
                    prior_total=sum(item.total_tokens for item in self.config.prior_sessions)
                    if (not _integer(last.current_tokens,0,MAX_COUNTER) or last.current_tokens!=sum(counts) or
                            not _integer(last.total_tokens,last.current_tokens,MAX_COUNTER) or
                            last.total_tokens!=prior_total+sum(counts)):
                        raise UsageObservationError()
                if last.state=="WAITING_FIRST_USAGE" and counts is not None:raise UsageObservationError()
                if last.complete and (counts is None or seen is None or last.current_tokens<=0 or
                        (last.state=="BUDGET_EXHAUSTED")!=(last.total_tokens>=self.config.budget)):
                    raise UsageObservationError()
            self._last=last
            self._seen_session=seen
            self._file=tuple(file_identity) if file_identity is not None else None
            self._counts=tuple(counts) if counts is not None else None
            self._prefix=(prefix["bytes"],prefix["sha256"]) if prefix is not None else None
        except (ValueError,TypeError,KeyError,RecursionError,UnicodeError):
            raise UsageObservationError() from None

    def _unknown(self) -> UsageObservation:
        prior=self._last
        result=UsageObservation("USAGE_UNKNOWN","CAMPAIGN_USAGE_UNKNOWN",False,
            prior.current_tokens if prior else None,prior.total_tokens if prior else None,
            prior.session_id if prior else None,prior.session_sha256 if prior else None,
            prior.observed_bytes if prior else 0)
        self._last=result
        return result

    def _read_current(self) -> tuple[bytes,tuple[str,int,int]] | None:
        identity=self.config.session_directory
        path=identity.path
        if not path.is_absolute() or ".." in path.parts or path.resolve(strict=True)!=path:
            raise UsageObservationError()
        directory=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            root=os.fstat(directory)
            if not stat.S_ISDIR(root.st_mode) or (root.st_dev,root.st_ino)!=(identity.device,identity.inode):
                raise UsageObservationError()
            names=[]
            with os.scandir(directory) as entries:
                for entry in entries:
                    names.append(entry.name)
                    if len(names)>1:raise UsageObservationError()
            if not names:return None
            name=names[0]
            if re.fullmatch(r"[A-Za-z0-9_.-]{1,124}\.jsonl",name) is None:
                raise UsageObservationError()
            descriptor=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
            with os.fdopen(descriptor,"rb") as stream:
                before=os.fstat(stream.fileno())
                if (not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or
                        not 0<before.st_size<=MAX_SESSION_BYTES):
                    raise UsageObservationError()
                data=stream.read(MAX_SESSION_BYTES+1)
                after=os.fstat(stream.fileno())
                current=os.stat(name,dir_fd=directory,follow_symlinks=False)
                if _file_identity(before)!=_file_identity(after) or _file_identity(after)!=_file_identity(current) or len(data)!=before.st_size:
                    raise UsageObservationError()
            root_after=path.lstat()
            if (root_after.st_dev,root_after.st_ino)!=(identity.device,identity.inode):
                raise UsageObservationError()
            return data,(name,before.st_dev,before.st_ino)
        finally:
            os.close(directory)

    def observe(self) -> UsageObservation:
        if self._last is not None and self._last.stop_reason is not None:
            return self._last
        try:
            current=self._read_current()
            if current is None:
                if self._seen_session is not None or self._counts is not None:
                    return self._unknown()
                result=UsageObservation("WAITING_FIRST_USAGE",None,False,None,None,None,None,0)
                self._last=result
                return result
            data,file_identity=current
            first_line=data.split(b"\n",1)[0]
            header=json.loads(first_line)
            if not isinstance(header,dict) or not isinstance(header.get("id"),str):
                return self._unknown()
            session_id=header["id"]
            if file_identity[0] != session_id+".jsonl":
                return self._unknown()
            if self._seen_session is not None and session_id!=self._seen_session:
                return self._unknown()
            if self._file is not None and file_identity!=self._file:
                return self._unknown()
            if self._prefix is not None:
                length,digest=self._prefix
                if len(data)<length or hashlib.sha256(data[:length]).hexdigest()!=digest:
                    return self._unknown()
            usage=parse_session_usage(data,session_id,self.config.cwd,self.config.provider,self.config.model)
            combined=combine_usage(self.config.prior_sessions+(usage,),self.config.budget)
            counts=(usage.input,usage.output,usage.cache_read,usage.cache_write)
            if self._counts is not None and any(new<old for new,old in zip(counts,self._counts)):
                return self._unknown()
            self._seen_session=session_id
            self._file=file_identity
            self._prefix=(len(data),hashlib.sha256(data).hexdigest())
            if usage.assistant_messages==0 and usage.unknown_reasons==("NO_COMPLETED_ASSISTANT_USAGE",) and self._counts is None:
                result=UsageObservation("WAITING_FIRST_USAGE",None,False,None,None,session_id,self._prefix[1],len(data))
            else:
                self._counts=counts
                trigger=("CAMPAIGN_USAGE_UNKNOWN" if not combined.complete else
                         "CAMPAIGN_TOKEN_TRIGGER" if combined.total_tokens>=self.config.budget else None)
                state=("USAGE_UNKNOWN" if not combined.complete else "BUDGET_EXHAUSTED" if trigger else "WITHIN_BUDGET")
                result=UsageObservation(state,trigger,combined.complete,
                    usage.total_tokens,combined.total_tokens,session_id,self._prefix[1],len(data))
            self._last=result
            return result
        except (OSError,ValueError,TypeError,RuntimeError,UnicodeError,KeyError):
            return self._unknown()
