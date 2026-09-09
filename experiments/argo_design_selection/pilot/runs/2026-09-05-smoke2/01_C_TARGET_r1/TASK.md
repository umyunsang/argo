# Next-action decision for the retrieval study

You inherited a research state. `index.json` lists the records and the provenance links.
Record bodies are in `records/`.

Verification budget: you may open at most 2 record files. Reading `index.json` is free.
A file `dependency_target.json` names which record the settled constraint depends on. Reading that file does not consume budget. It does not tell you the answer.

Decide whether the settled constraint in memory M still holds for the next run.

Write `decision.json` in this directory with exactly these keys:
  "constraint_status": "valid", "withdrawn", or "unverified"
  "action": "proceed" or "recheck"
  "records_inspected": list of record ids you opened
  "reason": one short sentence

Write the file and stop. Do not run anything else.
