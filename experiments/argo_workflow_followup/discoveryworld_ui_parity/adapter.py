#!/usr/bin/env python3
"""Evaluator-owned UI-only adapter candidate for pinned DiscoveryWorld."""
from __future__ import annotations

def get_ui_only_observation(api, agent_index: int) -> dict:
    if agent_index < 0 or agent_index >= api.numUserAgents:
        return {"errors": ["Agent index out of range"], "ui": {}}
    if api.world is None:
        return {"errors": ["World is not initialized"], "ui": {}}
    ui_json = api.ui[agent_index].renderJSON()
    api.taskProgress = ui_json["taskProgress"]
    api.steps = ui_json["world_steps"]
    return {"errors": [], "ui": ui_json}
