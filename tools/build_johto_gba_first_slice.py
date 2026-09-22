#!/usr/bin/env python3
"""Extract New Bark -> Route 29 -> Cherrygrove geometry from Japanese Gen II ROMs.

ROMs are inputs only and are never emitted. Each 32x32 Gen II block becomes four
16x16 logical GBA metatiles: block*4 + NW/NE/SW/SE (0/1/2/3). The resulting
map.bin files are little-endian u16 GBA map-grid entries with collision/elevation 0.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

MAPREC=9; ATTR=12; CONN=12; WARP=5; COORD=8; BG=5; OBJ=13
CONNS=(("north",8),("south",4),("west",2),("east",1))

def h(b): return hashlib.sha256(b).hexdigest()
def n(v): return v if isinstance(v,int) else int(v,0)
def gb(bank,addr):
    if addr < 0x4000: return addr
    if not 0x4000 <= addr < 0x8000: raise ValueError(f"bad GB pointer {bank:02X}:{addr:04X}")
    return bank*0x4000 + addr-0x4000
def take(rom,off,size,what):
    if off < 0 or off+size > len(rom): raise ValueError(f"{what} out of bounds @ 0x{off:X}")
    return rom[off:off+size]
def maprec(rom,root,g,m):
    bank=root//0x4000; gp=int.from_bytes(take(rom,root+2*(g-1),2,"group ptr"),"little")
    off=gb(bank,gp)+MAPREC*(m-1); r=take(rom,off,MAPREC,"map record")
    return {"off":off,"attrBank":r[0],"tileset":r[1],"attrPtr":int.from_bytes(r[3:5],"little")}
def attrs(rom,r):
    off=gb(r["attrBank"],r["attrPtr"]); a=take(rom,off,ATTR,"attributes")
    return {"off":off,"h":a[1],"w":a[2],"blockBank":a[3],"blockPtr":int.from_bytes(a[4:6],"little"),
            "scriptBank":a[6],"eventPtr":int.from_bytes(a[9:11],"little"),"bits":a[11]}
def connections(rom,a):
    pos=a["off"]+ATTR; out=[]
    for direction,bit in CONNS:
        if not a["bits"] & bit: continue
        r=take(rom,pos,CONN,"connection"); pos+=CONN
        y=struct.unpack("b",r[8:9])[0]; x=struct.unpack("b",r[9:10])[0]
        off=(-x//2) if direction in ("north","south") else (-y//2)
        out.append({"direction":direction,"destGroup":r[0],"destMap":r[1],
                    "sourceOffsetBlocks":off,"targetOffsetMetatiles":off*2})
    return out
def events(rom,a):
    pos=gb(a["scriptBank"],a["eventPtr"])+2
    wc=rom[pos]; pos+=1; warps=[]
    for _ in range(wc):
        r=take(rom,pos,WARP,"warp"); pos+=WARP
        warps.append({"x":r[1],"y":r[0],"destWarp":r[2],"destGroup":r[3],"destMap":r[4]})
    cc=rom[pos]; pos+=1; coords=[]
    for _ in range(cc):
        r=take(rom,pos,COORD,"coord"); pos+=COORD; coords.append({"x":r[2],"y":r[1],"scene":r[0]})
    bc=rom[pos]; pos+=1; bgs=[]
    for _ in range(bc):
        r=take(rom,pos,BG,"bg"); pos+=BG; bgs.append({"x":r[1],"y":r[0],"type":r[2]})
    oc=rom[pos]; pos+=1; objs=[]
    for _ in range(oc):
        r=take(rom,pos,OBJ,"object"); pos+=OBJ
        objs.append({"x":r[2]-4,"y":r[1]-4,"sprite":r[0],"eventFlag":int.from_bytes(r[11:13],"little")})
    return {"warps":warps,"coord":coords,"bg":bgs,"objects":objs}
def blockgrid(rom,a):
    off=gb(a["blockBank"],a["blockPtr"]); return off,take(rom,off,a["w"]*a["h"],"block grid")
def expand(src,w,hgt):
    tw=w*2; th=hgt*2; out=[0]*(tw*th)
    for y in range(hgt):
        for x in range(w):
            b=src[y*w+x]*4; i=(y*2)*tw+x*2
            out[i:i+2]=[b,b+1]; out[i+tw:i+tw+2]=[b+2,b+3]
    if max(out,default=0)>0x3ff: raise ValueError("logical metatile id overflow")
    return tw,th,out
def sig(v): return h(json.dumps(v,sort_keys=True,separators=(",",":")).encode())
def romargs(values):
    out={}
    for v in values:
        k,p=v.split("=",1); out[k]=Path(p)
    return out
def build(spec_path,rom_paths,out_root,manifest_path):
    spec=json.loads(spec_path.read_text()); expected=set(spec["sourceRoms"])
    if set(rom_paths)!=expected: raise ValueError(f"ROM labels must be exactly {sorted(expected)}")
    roms={}; source={}
    for label,rs in spec["sourceRoms"].items():
        data=rom_paths[label].read_bytes(); digest=h(data)
        if digest!=rs["sha256"]: raise ValueError(f"{label}: SHA-256 mismatch")
        roms[label]=data; source[label]={"filename":rs["filename"],"size":len(data),"sha256":digest,"mapGroupPointers":rs["mapGroupPointers"]}
    out_root.mkdir(parents=True,exist_ok=True); maps=[]
    for ms in spec["maps"]:
        refs=[]; evidence={}; group=ms["source"]["group"]; num=ms["source"]["map"]
        for label,rs in spec["sourceRoms"].items():
            rom=roms[label]; r=maprec(rom,n(rs["mapGroupPointers"]),group,num); a=attrs(rom,r)
            if r["tileset"]!=1 or (a["w"],a["h"])!=(ms["source"]["widthBlocks"],ms["source"]["heightBlocks"]): raise ValueError(f"{ms['id']}/{label}: source metadata mismatch")
            bo,blocks=blockgrid(rom,a); ev=events(rom,a); co=connections(rom,a)
            refs.append((blocks,ev,co)); evidence[label]={"mapRecordOffset":f"0x{r['off']:X}","mapAttributesOffset":f"0x{a['off']:X}","sourceBlockOffset":f"0x{bo:X}"}
        first=refs[0]
        if any(x!=first for x in refs[1:]): raise ValueError(f"{ms['id']}: Japanese revisions differ semantically")
        blocks,ev,co=first; sw=ms["source"]["widthBlocks"]; sh=ms["source"]["heightBlocks"]; tw,th,vals=expand(blocks,sw,sh)
        if (tw,th)!=(ms["target"]["widthMetatiles"],ms["target"]["heightMetatiles"]): raise ValueError(f"{ms['id']}: target size mismatch")
        blob=b"".join(struct.pack("<H",v) for v in vals); fn=ms["id"].lower()+".map.bin"; (out_root/fn).write_bytes(blob)
        maps.append({"id":ms["id"],"source":{"group":group,"map":num,"widthBlocks":sw,"heightBlocks":sh,"blockBytes":len(blocks),"blockSha256":h(blocks)},
                     "target":{"file":spec["targetGeometry"]["generatedAssetRoot"].rstrip("/")+"/"+fn,"widthMetatiles":tw,"heightMetatiles":th,"bytes":len(blob),"sha256":h(blob),"maxLogicalMetatileId":max(vals)},
                     "events":ev,"connections":co,"revisionEvidence":{"allFiveJapaneseRevisionsAgree":True,"semanticTopologySha256":sig({"events":ev,"connections":co}),"offsets":evidence}})
    result={"schema":1,"name":"Johto GBA first vertical slice - direct ROM extraction","masterReference":"Japanese retail ROMs; ROM binaries are inputs only and are never committed","sourceRoms":source,"maps":maps,
            "invariants":{"blockExpansion":"32x32 Gen II block -> four 16x16 logical GBA metatiles","logicalId":"source_block*4 + quadrant (NW=0,NE=1,SW=2,SE=3)","eventCoordinates":"preserved on the 16px movement grid","connectionOffsets":"Gen II block offset * 2","gbaCell":"little-endian u16; bits 0..9 logical metatile id; collision/elevation zero"}}
    manifest_path.parent.mkdir(parents=True,exist_ok=True); manifest_path.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":"))+"\n")
    return result
def main():
    p=argparse.ArgumentParser(); p.add_argument("--spec",type=Path,required=True); p.add_argument("--rom",action="append",default=[]); p.add_argument("--output-root",type=Path,required=True); p.add_argument("--manifest-out",type=Path,required=True); a=p.parse_args()
    r=build(a.spec,romargs(a.rom),a.output_root,a.manifest_out); print(json.dumps({"maps":[m["id"] for m in r["maps"]],"sourceRoms":list(r["sourceRoms"])},indent=2))
if __name__=="__main__": main()
