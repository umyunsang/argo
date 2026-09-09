import argparse,importlib.util,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--module",type=Path,required=True);p.add_argument("--agent",type=Path,required=True);p.add_argument("--scorer",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
s=importlib.util.spec_from_file_location("environment_identity",a.module);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
agent=json.loads(a.agent.read_text());scorer=json.loads(a.scorer.read_text())
required={"ccobra","deepchem","geopandas","matplotlib","mdanalysis","neurokit2","numpy","pandas","prolif","rasterio","rdkit","scikit-learn","tensorflow","tf-keras","torch"}
result=m.require_parity(agent,scorer,required)
result.update({"debian_package_count":len(agent["debian_packages"]),"debian_manifest_sha256":agent["debian_manifest_sha256"],"debian_parity":agent["debian_packages"]==scorer["debian_packages"],"container_digest":agent["container_digest"],"package_digest_semantics":agent["package_digest_semantics"]})
a.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
