#!/usr/bin/env python3
"""Condition-blind scorer with unambiguous action semantics."""
from __future__ import annotations
import json
class Violation(ValueError):pass

def score(payload,truth,critical_record,budget,observed):
 blob=json.dumps(payload,sort_keys=True).lower()
 if any(x in blob for x in ("c_base","c_target","treatment","control","arm")):raise Violation("CONDITION_LEAK")
 required={"constraint_status","constraint_disposition","needs_more_verification","records_inspected","reason"}
 if set(payload)!=required:return {"admissible":False,"reason":"SCHEMA_KEYS"}
 status=payload["constraint_status"];disp=payload["constraint_disposition"];need=payload["needs_more_verification"]
 if status not in ("valid","withdrawn","unverified") or disp not in ("apply","do_not_apply","undetermined") or not isinstance(need,bool):return {"admissible":False,"reason":"ENUM"}
 reads=sorted(set(observed));budget_bad=len(reads)>budget
 consistent=((status=="valid" and disp=="apply" and not need) or (status=="withdrawn" and disp=="do_not_apply" and not need) or (status=="unverified" and disp=="undetermined" and need))
 complete=all(payload[k]==truth[k] for k in ("constraint_status","constraint_disposition","needs_more_verification"))
 partial=status=="unverified" and disp=="undetermined" and need
 stale=(truth["constraint_status"]=="withdrawn" and (status=="valid" or disp=="apply"))
 overreact=(truth["constraint_status"]=="valid" and (status=="withdrawn" or disp=="do_not_apply"))
 return {"admissible":True,"schema_semantically_consistent":consistent,"fully_correct":complete and consistent and not budget_bad,"partial_safe":partial,"stale_consistent":stale,"overreaction":overreact,"critical_inspected":critical_record in reads,"budget_violation":budget_bad,"observed_reads":reads}
