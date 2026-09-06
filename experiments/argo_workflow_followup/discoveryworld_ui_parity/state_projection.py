#!/usr/bin/env python3
"""Exact allowlisted post-observation state projection for UI parity."""
from __future__ import annotations
import copy,hashlib,json

def uuid_or_none(value):
    if value is None:return None
    return getattr(value,"uuid",None)

def project_state(api, agent_index: int) -> dict:
    ui=api.ui[agent_index];agent=ui.currentAgent;dialog=ui.dialogToDisplay
    return copy.deepcopy({
        "inModal":bool(ui.inModal),
        "inDiscoveryFeedModal":bool(getattr(ui,"inDiscoveryFeedModal",False)),
        "dialog_present":dialog is not None,
        "dialog_text":None if dialog is None else dialog.get("dialogText"),
        "dialog_options":None if dialog is None else dialog.get("dialogOptions"),
        "message_queue":list(ui.messageQueueText),
        "arg_object_uuids":[uuid_or_none(x) for x in ui.argObjectsList],
        "arg1_index":ui.curSelectedArgument1Idx,
        "arg2_index":ui.curSelectedArgument2Idx,
        "arg1_uuid":uuid_or_none(ui.curSelectedArgument1Obj),
        "arg2_uuid":uuid_or_none(ui.curSelectedArgument2Obj),
        "object_to_show_uuid":uuid_or_none(agent.attributes.get("objectToShow")),
        "task_progress":api.taskProgress,
        "api_steps":api.steps,
        "world_counter":api.world.getStepCounter(),
    })

def canonical_bytes(value: object) -> bytes:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def projection_sha256(value: dict) -> str:return hashlib.sha256(canonical_bytes(value)).hexdigest()
