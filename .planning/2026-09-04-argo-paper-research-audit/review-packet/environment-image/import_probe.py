import importlib, json, platform, sys
modules=["ccobra","deepchem","geopandas","matplotlib","MDAnalysis","neurokit2","numpy","pandas","prolif","rasterio","rdkit","sklearn","tensorflow","tf_keras","torch"]
results=[]
for name in modules:
 try:
  module=importlib.import_module(name);results.append({"module":name,"imported":True,"version":getattr(module,"__version__",None)})
 except Exception as exc:results.append({"module":name,"imported":False,"error":repr(exc)})
print(json.dumps({"python":platform.python_version(),"machine":platform.machine(),"platform":sys.platform,"modules":results,"all_imported":all(x["imported"] for x in results)},sort_keys=True))
