# Next-action decision for the calibration study

You inherited a research state. `index.json` lists the records and the provenance links.
Record bodies are in `records/`.

Total verification budget: 2 records. You may open at most 1 record files. Reading `index.json` is free.
The dependency policy allocated one of the 2 verification slots to R1. `dependency_target.json` contains that prefetched record. You may open at most 1 additional record file.

Decide whether the settled constraint in memory M still holds for the next run.

Write `decision.json` in this directory with exactly these keys:
  "constraint_status": "valid", "withdrawn", or "unverified"
  "action": "proceed" or "recheck"
  "records_inspected": list of record ids you opened
  "reason": one short sentence

Write the file and stop. Do not run anything else.
