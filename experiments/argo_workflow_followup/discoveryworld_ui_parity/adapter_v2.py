#!/usr/bin/env python3
"""Pinned-source-mirrored nonvisual UI observation adapter candidate."""
from __future__ import annotations

def get_ui_only_observation(api, agent_index: int) -> dict:
    if agent_index < 0 or agent_index >= api.numUserAgents:
        return {"errors": [f"Agent index out of range. Specified agent index: {agent_index}. Number of agents: {api.numUserAgents} (i.e. value must be between 0 and {api.numUserAgents - 1})"], "ui": {}}
    if api.world is None:
        return {"errors": ["World is not initialized"], "ui": {}}
    ui = api.ui[agent_index]
    agent = ui.currentAgent
    ui.inModal = False
    inventory = agent.getInventory() if agent is not None else []
    environment = agent.getObjectsAgentFacing(respectContainerStatus=True) if agent is not None else []
    environment = ui._filterEnvObjects(inventory, environment)
    objects = ui._filterDuplicateObjects(inventory + environment)
    ui.updateArgumentObjects(objects)
    if ui.curSelectedArgument1Idx >= len(objects):
        ui.curSelectedArgument1Idx = len(objects) - 1
    ui.changeArgumentBox(delta=0, whichBox=1)
    if ui.curSelectedArgument2Idx >= len(objects):
        ui.curSelectedArgument2Idx = len(objects) - 1
    ui.changeArgumentBox(delta=0, whichBox=2)
    if ui.dialogToDisplay is not None:
        ui.inModal = False
    elif len(ui.messageQueueText) > 0:
        ui.inModal = True
    ui_json = ui.renderJSON()
    api.taskProgress = ui_json["taskProgress"]
    api.steps = ui_json["world_steps"]
    return {"errors": [], "ui": ui_json}
