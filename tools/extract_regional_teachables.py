#!/usr/bin/env python3
"""Extract surveyed regional-form teachable arrays from a generated header."""
from __future__ import annotations
import argparse,csv,hashlib,json,re

ARRAY_RE=re.compile(r"(?:static\s+)?const\s+u16\s+(?P<symbol>[A-Za-z0-9_]+)\s*\[\s*\]\s*=\s*\{(?P<body>.*?)\};",re.DOTALL)
MOVE_RE=re.compile(r"\bMOVE_[A-Z0-9_]+\b")

def parse_arrays(text:str)->dict[str,list[str]]:
 return {m.group("symbol"):MOVE_RE.findall(m.group("body")) for m in ARRAY_RE.finditer(text)}

def extract(master_text:str,header_text:str)->dict:
 rows=list(csv.DictReader(master_text.splitlines()));arrays=parse_arrays(header_text);entries=[];missing=[]
 for row in rows:
  symbol=row.get("teachableLearnset","").strip();item={"key":row["key"],"category":row["category"],"region":row["region"],"japaneseName":row["japaneseName"],"koreanName":row["koreanName"],"symbol":symbol}
  if symbol and symbol in arrays:item["moves"]=arrays[symbol];item["moveCount"]=len(arrays[symbol])
  else:item["moves"]=[];item["moveCount"]=0;missing.append({"key":row["key"],"symbol":symbol})
  entries.append(item)
 return {"schema_version":1,"master_rows":len(rows),"generated_arrays":len(arrays),"complete":not missing,"missing":missing,"entries":entries}

def markdown(report:dict)->str:
 lines=["# Regional forms teachable-learnset reference","",f"Survey entries: {report['master_rows']}",f"Complete: {'yes' if report['complete'] else 'no'}","","| Key | Symbol | Moves |","| --- | --- | ---: |"]
 lines.extend(f"| `{x['key']}` | `{x['symbol']}` | {x['moveCount']} |" for x in report["entries"])
 if report["missing"]:lines.extend(["","## Missing arrays",""]+[f"- `{x['key']}` → `{x['symbol']}`" for x in report["missing"]])
 return "\n".join(lines)+"\n"

def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("master_csv");p.add_argument("generated_header");p.add_argument("--json-output");p.add_argument("--markdown-output");p.add_argument("--require-complete",action="store_true");a=p.parse_args();master=open(a.master_csv,encoding="utf-8",newline="").read();header=open(a.generated_header,encoding="utf-8").read();r=extract(master,header);r["provenance"]={"master_sha256":hashlib.sha256(master.encode()).hexdigest(),"generated_header_sha256":hashlib.sha256(header.encode()).hexdigest()};j=json.dumps(r,ensure_ascii=False,indent=2)+"\n"
 if a.json_output:open(a.json_output,"w",encoding="utf-8",newline="\n").write(j)
 else:print(j,end="")
 if a.markdown_output:open(a.markdown_output,"w",encoding="utf-8",newline="\n").write(markdown(r))
 return 1 if a.require_complete and not r["complete"] else 0
if __name__=="__main__":raise SystemExit(main())
