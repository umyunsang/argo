import csv, hashlib, json, pandas as pd, sys
from pathlib import Path
csv_path=Path(sys.argv[1]); pq_path=Path(sys.argv[2]); out=Path(sys.argv[3])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
csv_rows=list(csv.DictReader(csv_path.open(encoding="utf-8")))
pq=pd.read_parquet(pq_path).fillna("")
pq_rows=[{k:str(v) for k,v in r.items()} for r in pq.to_dict(orient="records")]
# Normalize instance id only; preserve all text exactly otherwise.
for r in csv_rows: r["instance_id"]=str(int(r["instance_id"]))
for r in pq_rows: r["instance_id"]=str(int(r["instance_id"]))
cm={r["instance_id"]:r for r in csv_rows}; pm={r["instance_id"]:r for r in pq_rows}
diffs=[]
for i in sorted(set(cm)|set(pm),key=int):
 if i not in cm or i not in pm: diffs.append({"instance_id":i,"presence":"csv" if i in cm else "parquet"});continue
 fields=[k for k in cm[i] if cm[i].get(k,"")!=pm[i].get(k,"")]
 if fields: diffs.append({"instance_id":i,"fields":fields})
obj={"csv_sha256":sha(csv_path),"verified_parquet_sha256":sha(pq_path),"csv_rows":len(csv_rows),"verified_rows":len(pq_rows),"differing_task_count":len(diffs),"differences":diffs}
out.write_text(json.dumps(obj,indent=2)+"\n");print(json.dumps(obj))
