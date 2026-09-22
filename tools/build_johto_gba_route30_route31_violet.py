#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

MAPREC=9; ATTR=12; CONN=12; WARP=5; COORD=8; BG=5; OBJ=13
CONNS=(("north",8),("south",4),("west",2),("east",1))
EMERALD_MAP_GROUPS=0x45E998
EXPECTED={
 "gold_rev0":"7cfeceae00737a1f0713c9ab0b3a9e6eb8d05ff6002eb81308072a6f85e385e7",
 "gold_reva":"27a07a1d3faf9c6a0b1b60d5e88ee3a4159a751a47b4c46ab09f1202d52bac3e",
 "silver_rev0":"0a532063a3ff5750a464582aa7bbee2b6d42e1a92a136d9f4590e373487b615c",
 "silver_reva":"99e5267fbf5a7748d4f3b75ba1990cb5d91348339468607a04bfbc6081c62d71",
 "crystal_rev0":"136ada06cb68656b7de475fa4b278d37dbeff8f5257e7dfdf7f4a4aec19a90f3",
 "emerald":"33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c",
}
ROOTS={"gold_rev0":0x940ED,"gold_reva":0x940ED,"silver_rev0":0x940ED,"silver_reva":0x940ED,"crystal_rev0":0x94000}
SPECS={"route_30":(26,1,10,27),"route_31":(26,2,20,9),"violet_city":(10,5,20,18)}
C={
0x01:("FLOOR",)*4,0x02:("FLOOR",)*4,0x03:("TALL_GRASS",)*4,0x04:("FLOOR",)*4,0x05:("WALL",)*4,
0x08:("WALL",)*4,0x09:("WALL",)*4,0x0B:("WARP_LEFT","FLOOR","WARP_LEFT","FLOOR"),0x0E:("WALL",)*4,0x10:("WALL",)*4,0x11:("WALL",)*4,
0x14:("WALL","WALL","WALL","DOOR"),0x15:("WALL",)*4,0x16:("WALL","WALL","WALL","DOOR"),0x17:("WALL",)*4,0x18:("WALL",)*4,0x19:("WALL",)*4,
0x1A:("WALL","WALL","WALL","DOOR"),0x1B:("WALL",)*4,0x1C:("WALL",)*4,0x1D:("WALL","WALL","DOOR","WALL"),0x1E:("WALL",)*4,0x1F:("WALL",)*4,
0x20:("WALL",)*4,0x21:("WALL",)*4,0x22:("WALL",)*4,0x23:("WALL",)*4,0x26:("WALL",)*4,0x27:("WALL","WALL","DOOR","WALL"),
0x28:("WALL","WALL","WALL","DOOR"),0x2A:("HEADBUTT_TREE","HEADBUTT_TREE","WALL","WALL"),0x2C:("HEADBUTT_TREE","HEADBUTT_TREE","WALL","WALL"),
0x2D:("HEADBUTT_TREE","HEADBUTT_TREE","WALL","WALL"),0x2E:("WALL","WALL","WALL","DOOR"),0x2F:("WALL",)*4,
0x30:("BUOY","BUOY","BUOY","WATER"),0x31:("BUOY","BUOY","WATER","WATER"),0x32:("BUOY","BUOY","WATER","BUOY"),
0x33:("FLOOR","FLOOR","WALL","WALL"),0x34:("BUOY","WATER","BUOY","WATER"),0x35:("WATER",)*4,0x36:("WATER","BUOY","WATER","BUOY"),
0x37:("WALL",)*4,0x38:("BUOY","WATER","BUOY","BUOY"),0x39:("WATER","WATER","BUOY","BUOY"),0x3A:("WATER","BUOY","BUOY","BUOY"),0x3B:("WALL",)*4,
0x3C:("HEADBUTT_TREE","FLOOR","FLOOR","FLOOR"),0x3D:("FLOOR","HEADBUTT_TREE","FLOOR","FLOOR"),0x3E:("FLOOR","FLOOR","HEADBUTT_TREE","FLOOR"),
0x3F:("FLOOR","FLOOR","FLOOR","HEADBUTT_TREE"),0x40:("WALL","WALL","WALL","FLOOR"),0x41:("WALL","WALL","FLOOR","FLOOR"),
0x42:("WALL","WALL","FLOOR","WALL"),0x43:("WATER",)*4,0x44:("WALL","FLOOR","WALL","FLOOR"),0x45:("WALL","FLOOR","FLOOR","FLOOR"),
0x46:("FLOOR","WALL","FLOOR","WALL"),0x47:("FLOOR","FLOOR","FLOOR","WALL"),0x48:("WALL","FLOOR","WALL","WALL"),
0x49:("FLOOR","FLOOR","WALL","WALL"),0x4A:("FLOOR","WALL","WALL","WALL"),0x4B:("HOP_DOWN","FLOOR","WALL","FLOOR"),
0x4C:("WALL","HOP_LEFT","WALL","HOP_LEFT"),0x4D:("HOP_RIGHT","WALL","HOP_RIGHT","WALL"),0x4E:("WALL","HOP_LEFT","WALL","HOP_LEFT"),
0x4F:("HOP_RIGHT","WALL","HOP_RIGHT","WALL"),0x50:("WALL","HOP_DOWN_LEFT","WALL","WALL"),0x51:("HOP_DOWN_RIGHT","WALL","WALL","WALL"),
0x52:("WALL","HOP_DOWN_LEFT","WALL","WALL"),0x53:("HOP_DOWN_RIGHT","WALL","WALL","WALL"),0x54:("WATER",)*4,0x55:("WATER",)*4,
0x56:("HOP_DOWN","HOP_DOWN","WALL","WALL"),0x57:("HOP_DOWN","HOP_DOWN","WALL","WALL"),0x58:("WATER",)*4,0x59:("WATER",)*4,
0x5A:("HOP_DOWN","FLOOR","WALL","FLOOR"),0x5B:("HEADBUTT_TREE","CUT_TREE","FLOOR","FLOOR"),0x5C:("HEADBUTT_TREE","HEADBUTT_TREE","HEADBUTT_TREE","FLOOR"),
0x5D:("HEADBUTT_TREE","HEADBUTT_TREE","FLOOR","FLOOR"),0x5E:("HEADBUTT_TREE","HEADBUTT_TREE","FLOOR","HEADBUTT_TREE"),
0x5F:("FLOOR","HEADBUTT_TREE","FLOOR","CUT_TREE"),0x60:("HEADBUTT_TREE","FLOOR","HEADBUTT_TREE","FLOOR"),0x61:("HEADBUTT_TREE",)*4,
0x62:("FLOOR","HEADBUTT_TREE","FLOOR","HEADBUTT_TREE"),0x63:("FLOOR","FLOOR","CUT_TREE","HEADBUTT_TREE"),
0x64:("HEADBUTT_TREE","FLOOR","HEADBUTT_TREE","HEADBUTT_TREE"),0x65:("FLOOR","FLOOR","HEADBUTT_TREE","HEADBUTT_TREE"),
0x66:("FLOOR","HEADBUTT_TREE","HEADBUTT_TREE","HEADBUTT_TREE"),0x67:("CUT_TREE","FLOOR","HEADBUTT_TREE","FLOOR"),
0x68:("WALL","FLOOR","WALL","FLOOR"),0x69:("FLOOR","WALL","FLOOR","WALL"),0x6A:("WALL","UP_WALL","WALL","FLOOR"),
0x6B:("UP_WALL","WALL","FLOOR","WALL"),0x6C:("WALL","FLOOR","WALL","WALL"),0x6D:("FLOOR","WALL","WALL","WALL"),
0x6E:("FLOOR","FLOOR","WALL","FLOOR"),0x6F:("FLOOR","FLOOR","FLOOR","WALL"),0x70:("UP_WALL","UP_WALL","FLOOR","FLOOR"),
0x71:("FLOOR",)*4,0x72:("FLOOR","FLOOR","WALL","WALL"),0x73:("FLOOR","FLOOR","CAVE","WALL"),0x74:("WALL","FLOOR","FLOOR","FLOOR"),
0x75:("WALL","WALL","FLOOR","FLOOR"),0x76:("WATER",)*4,0x77:("WALL","WALL","DOOR","WALL"),0x78:("FLOOR","FLOOR","FLOOR","WALL"),
0x79:("WATER",)*4,0x7A:("WATER",)*4,
}

def sha(b): return hashlib.sha256(b).hexdigest()
def gb(bank,addr):
 if addr<0x4000:return addr
 if not 0x4000<=addr<0x8000:raise ValueError(f"bad GB ptr {bank:02x}:{addr:04x}")
 return bank*0x4000+addr-0x4000
def maprec(rom,root,g,m):
 bank=root//0x4000;gp=int.from_bytes(rom[root+2*(g-1):root+2*g],"little");off=gb(bank,gp)+MAPREC*(m-1);r=rom[off:off+MAPREC]
 return {"off":off,"attrBank":r[0],"tileset":r[1],"attrPtr":int.from_bytes(r[3:5],"little")}
def attrs(rom,r):
 off=gb(r["attrBank"],r["attrPtr"]);a=rom[off:off+ATTR]
 return {"off":off,"h":a[1],"w":a[2],"blockBank":a[3],"blockPtr":int.from_bytes(a[4:6],"little"),"scriptBank":a[6],"eventPtr":int.from_bytes(a[9:11],"little"),"bits":a[11]}
def blockgrid(rom,a):
 off=gb(a["blockBank"],a["blockPtr"]);return off,rom[off:off+a["w"]*a["h"]]
def connections(rom,a):
 pos=a["off"]+ATTR;out=[]
 for direction,bit in CONNS:
  if not a["bits"]&bit:continue
  r=rom[pos:pos+CONN];pos+=CONN;y=struct.unpack("b",r[8:9])[0];x=struct.unpack("b",r[9:10])[0]
  o=(-x//2) if direction in ("north","south") else (-y//2)
  out.append({"direction":direction,"destGroup":r[0],"destMap":r[1],"sourceOffsetBlocks":o,"targetOffsetMetatiles":o*2})
 return out
def events(rom,a):
 pos=gb(a["scriptBank"],a["eventPtr"])+2;wc=rom[pos];pos+=1;warps=[]
 for _ in range(wc):
  r=rom[pos:pos+WARP];pos+=WARP;warps.append({"x":r[1],"y":r[0],"destWarp":r[2],"destGroup":r[3],"destMap":r[4]})
 cc=rom[pos];pos+=1;coord=[]
 for _ in range(cc):r=rom[pos:pos+COORD];pos+=COORD;coord.append({"x":r[2],"y":r[1],"scene":r[0]})
 bc=rom[pos];pos+=1;bg=[]
 for _ in range(bc):r=rom[pos:pos+BG];pos+=BG;bg.append({"x":r[1],"y":r[0],"type":r[2]})
 oc=rom[pos];pos+=1;objs=[]
 for _ in range(oc):
  r=rom[pos:pos+OBJ];pos+=OBJ;objs.append({"x":r[2]-4,"y":r[1]-4,"sprite":r[0],"eventFlag":int.from_bytes(r[11:13],"little")})
 return {"warps":warps,"coord":coord,"bg":bg,"objects":objs}
def ptr(rom,o):
 v=int.from_bytes(rom[o:o+4],"little")
 if v>>24 not in (8,9):raise ValueError(f"bad GBA ptr {v:#x} at {o:#x}")
 return v&0x1ffffff
def emap(rom,n):
 g=ptr(rom,EMERALD_MAP_GROUPS);h=ptr(rom,g+n*4);l=ptr(rom,h);w=int.from_bytes(rom[l:l+4],"little",signed=True);ht=int.from_bytes(rom[l+4:l+8],"little",signed=True);mo=ptr(rom,l+12);raw=rom[mo:mo+w*ht*2]
 return {"num":n,"header":h,"layout":l,"map_offset":mo,"w":w,"h":ht,"raw":raw,"c":[int.from_bytes(raw[i:i+2],"little") for i in range(0,len(raw),2)]}
def rect(m,x,y,w,h):return [m["c"][(y+j)*m["w"]+x:(y+j)*m["w"]+x+w] for j in range(h)]
def paste(g,w,h,x,y,p):
 for j,row in enumerate(p):
  for i,v in enumerate(row):
   if 0<=x+i<w and 0<=y+j<h:g[(y+j)*w+x+i]=v
def src(blocks,bw,x,y):
 b=blocks[(y//2)*bw+x//2];q=(y&1)*2+(x&1);return b,q,C.get(b,("WALL",)*4)[q]
def pack(g):return b"".join(v.to_bytes(2,"little") for v in g)
def donor_evidence(rom,ds,names):
 out={}
 for k in names:
  m=ds[k];out[k]={"map_num":m["num"],"header":hex(m["header"]),"layout":hex(m["layout"]),"map_offset":hex(m["map_offset"]),"width":m["w"],"height":m["h"],"map_sha256":sha(m["raw"])}
 return {"rom_sha256":sha(rom),"map_groups_offset":hex(EMERALD_MAP_GROUPS),"maps":out}
def source_versions(roms,key):
 g,m,bw,bh=SPECS[key];out={};blocks={}
 for label,rom in roms.items():
  r=maprec(rom,ROOTS[label],g,m);a=attrs(rom,r);bo,b=blockgrid(rom,a);ev=events(rom,a);co=connections(rom,a)
  if (a["w"],a["h"],r["tileset"])!=(bw,bh,1):raise ValueError(f"{key}/{label}: source metadata mismatch")
  out[label]={"map_record_offset":hex(r["off"]),"attributes_offset":hex(a["off"]),"block_offset":hex(bo),"block_sha256":sha(b),"events":ev,"connections":co};blocks[label]=b
 return out,blocks
def compact_versions(versions):
 master=versions["gold_rev0"];out={"canonical":{"label":"gold_rev0",**master},"revisions":{}}
 for label,v in versions.items():
  if label=="gold_rev0":continue
  e={k:v[k] for k in ("map_record_offset","attributes_offset","block_offset","block_sha256")};dif={}
  if v["events"]!=master["events"]:dif["events"]=v["events"]
  if v["connections"]!=master["connections"]:dif["connections"]=v["connections"]
  e["same_topology_events_as_gold_rev0"]=not bool(dif)
  if dif:e["differences_from_gold_rev0"]=dif
  out["revisions"][label]=e
 return out
def donors(e):
 ds={"rustboro":emap(e,3),"oldale":emap(e,10),"r101":emap(e,16),"r102":emap(e,17),"r104":emap(e,19),"r116":emap(e,31)}
 ds["ground"]=ds["oldale"]["c"][10*20+10];ds["detail"]=ds["oldale"]["c"][10*20+1];ds["grass"]=ds["r101"]["c"][2*20+2];ds["water"]=ds["r102"]["c"][3*50+41];ds["sign"]=ds["oldale"]["c"][9*20+11]
 ds["pet_tree"]={0:ds["r101"]["c"][0],1:ds["r101"]["c"][1],2:ds["r101"]["c"][20],3:ds["r101"]["c"][21]}
 ds["rust_wall"]={0:ds["r104"]["c"][0],1:ds["r104"]["c"][1],2:ds["r104"]["c"][40],3:ds["r104"]["c"][41]}
 ds["jump"]={"HOP_DOWN":0x0487,"HOP_LEFT":0x0485,"HOP_RIGHT":0x0486,"HOP_DOWN_LEFT":0x048D,"HOP_DOWN_RIGHT":0x048E}
 return ds
def terrain(blocks,bw,bh,ds,profile):
 w,h=bw*2,bh*2;g=[ds["ground"]]*(w*h)
 for y in range(h):
  for x in range(w):
   b,q,s=src(blocks,bw,x,y);v=ds["ground"]
   if s=="TALL_GRASS":v=ds["grass"]
   elif s in ("WATER","BUOY"):v=ds["water"]
   elif s in ("HEADBUTT_TREE","CUT_TREE"):v=(ds["pet_tree"] if profile=="petalburg" else ds["rust_wall"])[q]
   elif s.startswith("HOP_"):v=ds["jump"][s]
   elif s in ("WALL","UP_WALL","CAVE","DOOR","WARP_LEFT"):v=(ds["pet_tree"] if profile=="petalburg" else ds["rust_wall"])[q]
   elif b in (0x02,0x04,0x71):v=ds["detail"]
   g[y*w+x]=v
 return g,w,h
def build_route30(blocks,ds):
 g,w,h=terrain(blocks,10,27,ds,"petalburg");paste(g,w,h,6,36,rect(ds["oldale"],4,4,4,4));paste(g,w,h,16,2,rect(ds["oldale"],14,13,4,4))
 for x,y in ((9,43),(13,29),(15,5),(3,21)):g[y*w+x]=ds["sign"]
 return pack(g)
def build_route31(blocks,ds):
 g,w,h=terrain(blocks,20,9,ds,"rustboro");gateway=ds["r104"]["c"][30*40+10];g[6*w+4]=gateway;g[7*w+4]=gateway
 paste(g,w,h,32,2,rect(ds["r116"],45,5,5,4))
 for x,y in ((7,5),(31,5)):g[y*w+x]=ds["sign"]
 return pack(g)
def build_violet(blocks,ds):
 g,w,h=terrain(blocks,20,18,ds,"rustboro");r=ds["rustboro"]
 paste(g,w,h,19,0,rect(r,7,10,9,6));paste(g,w,h,0,11,rect(r,30,15,7,5));paste(g,w,h,6,14,rect(r,13,42,7,4));paste(g,w,h,15,13,rect(r,24,15,7,5))
 paste(g,w,h,27,13,rect(r,24,30,8,5));paste(g,w,h,28,22,rect(r,13,35,7,4));paste(g,w,h,18,25,rect(r,30,15,7,5))
 gate=ds["r104"]["c"][30*40+10];g[24*w+39]=gate;g[25*w+39]=gate
 for x,y in ((24,20),(15,17),(24,8),(27,17),(32,25),(10,17)):g[y*w+x]=ds["sign"]
 return pack(g)
def main():
 p=argparse.ArgumentParser();p.add_argument("--rom",action="append",default=[]);p.add_argument("--emerald-rom",required=True,type=Path);p.add_argument("--out-dir",required=True,type=Path);a=p.parse_args()
 rp={k:Path(v) for k,v in (x.split("=",1) for x in a.rom)}
 if set(rp)!=set(ROOTS):raise ValueError(f"need ROM labels {sorted(ROOTS)}")
 roms={k:v.read_bytes() for k,v in rp.items()};e=a.emerald_rom.read_bytes()
 for k,b in roms.items():
  if sha(b)!=EXPECTED[k]:raise ValueError(f"{k} sha mismatch")
 if sha(e)!=EXPECTED["emerald"]:raise ValueError("emerald sha mismatch")
 ds=donors(e);a.out_dir.mkdir(parents=True,exist_ok=True)
 for key,fn,profile in (("route_30",build_route30,"General+Petalburg"),("route_31",build_route31,"General+Rustboro")):
  vers,bs=source_versions(roms,key);common=bs["gold_rev0"]
  if not all(v==common for v in bs.values()):raise ValueError(f"{key}: expected shared block grid")
  blob=fn(common,ds);(a.out_dir/f"{key}.map.bin").write_bytes(blob)
  man={"schema":3,"policy":"GSC supplies topology/semantic intent/events; Japanese Emerald supplies all final visible GBA metatiles. No GSC pixels are emitted.","target":{"map":key,"width":SPECS[key][2]*2,"height":SPECS[key][3]*2,"bytes":len(blob),"sha256":sha(blob),"tileset_profile":profile},"source":{"shared_block_sha256":sha(common),"version_evidence":compact_versions(vers)},"emerald":donor_evidence(e,ds,["oldale","r101","r102"] if key=="route_30" else ["r104","r116","rustboro"])}
  (a.out_dir/f"{key}.remake.json").write_text(json.dumps(man,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 vers,bs=source_versions(roms,"violet_city");gs=bs["gold_rev0"]
 if not (bs["gold_reva"]==gs==bs["silver_rev0"]==bs["silver_reva"]):raise ValueError("Violet GS revisions diverge unexpectedly")
 cry=bs["crystal_rev0"];diffs=[{"block_x":i%20,"block_y":i//20,"gs":hex(gs[i]),"crystal":hex(cry[i])} for i in range(len(gs)) if gs[i]!=cry[i]]
 expected=[{"block_x":14,"block_y":7,"gs":"0x20","crystal":"0x2c"},{"block_x":15,"block_y":7,"gs":"0x3b","crystal":"0x2a"},{"block_x":16,"block_y":7,"gs":"0x21","crystal":"0x2d"}]
 if diffs!=expected:raise ValueError(f"unexpected Violet variant diff {diffs}")
 blob=build_violet(gs,ds);(a.out_dir/"violet_city.map.bin").write_bytes(blob)
 man={"schema":3,"policy":"GSC supplies topology/semantic intent/events; Japanese Emerald General+Rustboro supplies the final GBA visual grammar. Gold/Silver and Crystal source differences remain explicit even where the enlarged GBA building footprint reconciles them visually.","target":{"map":"Violet City","width":40,"height":36,"bytes":len(blob),"sha256":sha(blob),"tileset_profile":"General+Rustboro"},"source":{"gold_silver_block_sha256":sha(gs),"crystal_block_sha256":sha(cry),"source_block_differences":diffs,"reconciliation":"The three Crystal-vs-GS block changes are at source block row 7, columns 14..16 (target cells x=28..33,y=14..15). The GBA Academy exterior expands over this exact area, so both source variants intentionally share the same final Academy footprint; the original variant evidence is retained here.","version_evidence":compact_versions(vers)},"emerald":donor_evidence(e,ds,["rustboro","r104","r116"]),"johto_specific_replacements":[{"feature":"Sprout Tower exterior","current_structural_donor":"Rustboro Devon multi-storey facade","rule":"replace with a Johto-specific Gen III secondary asset later; keep warp (23,5) and surrounding topology"}]}
 (a.out_dir/"violet_city.remake.json").write_text(json.dumps(man,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({p.name:sha(p.read_bytes()) for p in sorted(a.out_dir.glob("*.map.bin"))},indent=2))
if __name__=="__main__":main()
