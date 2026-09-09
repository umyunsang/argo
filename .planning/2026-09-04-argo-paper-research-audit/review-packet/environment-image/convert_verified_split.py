import argparse,hashlib,json
from pathlib import Path
import pandas as pd
p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--receipt",type=Path,required=True);a=p.parse_args()
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
df=pd.read_parquet(a.source)
cols=list(df.columns); rows=[]
for raw in df.to_dict(orient="records"):
 row={}
 for c in cols:
  v=raw[c]
  if c=="instance_id":v=str(int(v))
  elif pd.isna(v):v=""
  else:v=str(v)
  row[c]=v
 rows.append(row)
a.out.write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
read=json.loads(a.out.read_text(encoding="utf-8"))
assert read==rows and len({r["instance_id"] for r in rows})==len(rows)
receipt={"schema_version":"argo-sab-verified-split-conversion/v1","source_path":str(a.source),"source_sha256":sha(a.source),"output_path":str(a.out),"output_sha256":sha(a.out),"rows":len(rows),"columns":cols,"roundtrip_equal":read==rows}
a.receipt.write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps(receipt))
