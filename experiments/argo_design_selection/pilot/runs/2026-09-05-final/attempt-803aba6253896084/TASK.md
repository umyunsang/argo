# Next-action decision for the optimizer study

You inherited a research state. `index.json` lists the records and the provenance links.
Record bodies are in `records/`.

Total verification budget: 2 records. You may open at most 2 record files. Reading `index.json` is free.
Decide whether the settled constraint in memory M still holds for the next run.

Write `decision.json` in this directory with exactly these keys:
  "constraint_status": "valid", "withdrawn", or "unverified"
  "action": "proceed" or "recheck"
  "records_inspected": list of record ids you opened
  "reason": one short sentence

Use only the available tools: `read_index`, `read_dependency_target`, `read_record`, and `write_decision`.
Write the file through `write_decision` and stop. Do not run anything else.
