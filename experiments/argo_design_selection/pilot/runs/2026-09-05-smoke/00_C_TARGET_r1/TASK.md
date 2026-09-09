# Next-action decision for the thermal study

You inherited a research state. `index.json` lists the records and the provenance links.
Record bodies are in `records/`.

Verification budget: you may open at most 2 record files. Reading `index.json` is free.
A file `dependency_target.json` lists the nodes that lose support according to the state's own dependency graph. Reading it does not consume budget.

Decide whether the settled constraint in memory M still holds for the next run.

Write `decision.json` in this directory with exactly these keys:
  "constraint_status": "valid" or "withdrawn"
  "action": "proceed" or "recheck"
  "records_inspected": list of record ids you opened
  "reason": one short sentence

Write the file and stop. Do not run anything else.
