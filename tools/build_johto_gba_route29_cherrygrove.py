#!/usr/bin/env python3
"""Build Route 29 and Cherrygrove as Gen III-style Johto remakes.

Japanese GSC ROM data supplies topology and per-quadrant semantic intent.
Japanese Emerald supplies every visible target metatile and packed map behavior.
GSC graphics are classification evidence only; no GSC pixels are emitted.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

MAP_GROUPS=0x45E998
MAPS={
 "route_29":(0xA92D5,30,9,60,18),
 "cherrygrove_city":(0xACE0F,20,9,40,18),
}
# Exact Johto block quadrant semantics needed by this slice (NW,NE,SW,SE).
C={
0x01:("FLOOR",)*4,0x02:("FLOOR",)*4,0x03:("TALL_GRASS",)*4,0x04:("FLOOR",)*4,
0x05:("WALL",)*4,0x0A:("WALL",)*4,0x11:("WALL",)*4,
0x14:("WALL","WALL","WALL","DOOR"),0x15:("WALL",)*4,0x16:("WALL","WALL","WALL","DOOR"),
0x17:("WALL",)*4,0x18:("WALL",)*4,0x19:("WALL",)*4,0x1A:("WALL","WALL","WALL","DOOR"),
0x1B:("WALL",)*4,0x1C:("WALL",)*4,0x1E:("WALL",)*4,0x1F:("WALL",)*4,
0x30:("BUOY","BUOY","BUOY","WATER"),0x31:("BUOY","BUOY","WATER","WATER"),
0x32:("BUOY","BUOY","WATER","BUOY"),0x34:("BUOY","WATER","BUOY","WATER"),0x35:("WATER",)*4,
0x36:("WATER","BUOY","WATER","BUOY"),0x39:("WATER","WATER","BUOY","BUOY"),
0x3C:("HEADBUTT_TREE","FLOOR","FLOOR","FLOOR"),0x3D:("FLOOR","HEADBUTT_TREE","FLOOR","FLOOR"),
0x3E:("FLOOR","FLOOR","HEADBUTT_TREE","FLOOR"),0x3F:("FLOOR","FLOOR","FLOOR","HEADBUTT_TREE"),
0x45:("WALL","FLOOR","FLOOR","FLOOR"),0x47:("FLOOR","FLOOR","FLOOR","WALL"),
0x4B:("HOP_DOWN","FLOOR","WALL","FLOOR"),0x4E:("WALL","HOP_LEFT","WALL","HOP_LEFT"),
0x4F:("HOP_RIGHT","WALL","HOP_RIGHT","WALL"),0x52:("WALL","HOP_DOWN_LEFT","WALL","WALL"),
0x53:("HOP_DOWN_RIGHT","WALL","WALL","WALL"),0x54:("WATER",)*4,
0x57:("HOP_DOWN","HOP_DOWN","WALL","WALL"),0x58:("WATER",)*4,0x59:("WATER",)*4,
0x5C:("HEADBUTT_TREE","HEADBUTT_TREE","HEADBUTT_TREE","FLOOR"),
0x5D:("HEADBUTT_TREE","HEADBUTT_TREE","FLOOR","FLOOR"),
0x5E:("HEADBUTT_TREE","HEADBUTT_TREE","FLOOR","HEADBUTT_TREE"),
0x5F:("FLOOR","HEADBUTT_TREE","FLOOR","CUT_TREE"),0x61:("HEADBUTT_TREE",)*4,
0x62:("FLOOR","HEADBUTT_TREE","FLOOR","HEADBUTT_TREE"),
0x63:("FLOOR","FLOOR","CUT_TREE","HEADBUTT_TREE"),
0x64:("HEADBUTT_TREE","FLOOR","HEADBUTT_TREE","HEADBUTT_TREE"),
0x65:("FLOOR","FLOOR","HEADBUTT_TREE","HEADBUTT_TREE"),
0x66:("FLOOR","HEADBUTT_TREE","HEADBUTT_TREE","HEADBUTT_TREE"),
0x71:("FLOOR",)*4,0x76:("WATER",)*4,0x77:("WALL","WALL","DOOR","WALL"),0x79:("WATER",)*4,0x7A:("WATER",)*4,
}
TREE={0x05,0x11,0x3C,0x3D,0x3E,0x3F,0x5C,0x5D,0x5E,0x5F,0x61,0x62,0x63,0x64,0x65,0x66}
COAST={0x0A,0x30,0x31,0x32,0x34,0x35,0x36,0x39,0x54,0x58,0x59,0x71,0x76,0x79,0x7A}
BUILD={0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1E,0x1F,0x77}
LEDGE={0x4B,0x4E,0x4F,0x52,0x53,0x57}

def sha(b): return hashlib.sha256(b).hexdigest()
def u32(b,o): return int.from_bytes(b[o:o+4],"little")
def ptr(b,o):
 v=u32(b,o)
 if v>>24 not in (8,9): raise ValueError(f"bad GBA pointer {v:#x} at {o:#x}")
 return v&0x1ffffff

def emap(rom,n):
 g=ptr(rom,MAP_GROUPS); h=ptr(rom,g+n*4); l=ptr(rom,h)
 w=int.from_bytes(rom[l:l+4],"little",signed=True); ht=int.from_bytes(rom[l+4:l+8],"little",signed=True)
 mo=ptr(rom,l+12); raw=rom[mo:mo+w*ht*2]
 return {"num":n,"header":h,"layout":l,"off":mo,"w":w,"h":ht,"raw":raw,
         "c":[int.from_bytes(raw[i:i+2],"little") for i in range(0,len(raw),2)]}

def rect(m,x,y,w,h): return [m["c"][(y+j)*m["w"]+x:(y+j)*m["w"]+x+w] for j in range(h)]
def paste(g,w,h,x,y,p):
 for j,row in enumerate(p):
  for i,v in enumerate(row):
   if 0<=x+i<w and 0<=y+j<h:g[(y+j)*w+x+i]=v

def src(blocks,bw,x,y):
 b=blocks[(y//2)*bw+x//2]; q=(y&1)*2+(x&1)
 return b,q,C.get(b,("FLOOR",)*4)[q]
def outbytes(g): return b"".join(v.to_bytes(2,"little") for v in g)

def apply_ledge_grammar(g,sem,w,h,ground):
 # Japanese Emerald General: cap/body/corner entries from retail maps.
 left_cap,right_cap=0x04D5,0x04D6
 top_left,top_right=0x04FE,0x04FF
 core={"HOP_DOWN":0x0487,"HOP_LEFT":0x0485,"HOP_RIGHT":0x0486,
       "HOP_DOWN_LEFT":0x048D,"HOP_DOWN_RIGHT":0x048E}
 for i,s in enumerate(sem):
  if s in core:g[i]=core[s]
 for y in range(h):
  for x in range(w):
   s=sem[y*w+x]
   if s=="HOP_LEFT" and (y==0 or sem[(y-1)*w+x]!="HOP_LEFT"):g[y*w+x]=top_left
   elif s=="HOP_RIGHT" and (y==0 or sem[(y-1)*w+x]!="HOP_RIGHT"):g[y*w+x]=top_right
 for y in range(h):
  x=0
  while x<w:
   if sem[y*w+x]!="HOP_DOWN":x+=1;continue
   start=x
   while x+1<w and sem[y*w+x+1]=="HOP_DOWN":x+=1
   end=x
   linked_left=start>0 and sem[y*w+start-1]=="HOP_DOWN_LEFT"
   linked_right=end+1<w and sem[y*w+end+1]=="HOP_DOWN_RIGHT"
   if start==end:
    if linked_left and not linked_right:g[y*w+start]=right_cap
    elif linked_right and not linked_left:g[y*w+start]=left_cap
   else:
    if not linked_left:g[y*w+start]=left_cap
    if not linked_right:g[y*w+end]=right_cap
   x+=1
 # GSC ledge blocks are 32x32. Their low-side WALL quadrants represent the
 # same ledge face, not an extra GBA cell. Collapse those quadrants to the
 # lower walkable terrain so the Gen III ledge stays one metatile thick.
 def collapse(xx,yy):
  if 0<=xx<w and 0<=yy<h and sem[yy*w+xx]=="WALL":
   g[yy*w+xx]=ground
 for y in range(h):
  for x in range(w):
   s=sem[y*w+x]
   if s=="HOP_DOWN":collapse(x,y+1)
   elif s=="HOP_LEFT":collapse(x-1,y)
   elif s=="HOP_RIGHT":collapse(x+1,y)
   elif s=="HOP_DOWN_LEFT":
    collapse(x-1,y);collapse(x,y+1)
   elif s=="HOP_DOWN_RIGHT":
    collapse(x+1,y);collapse(x,y+1)


def donors(e):
 l,o,r101,r102,r103=[emap(e,n) for n in (9,10,16,17,18)]
 d={"l":l,"o":o,"r101":r101,"r102":r102,"r103":r103}
 d.update(ground=l["c"][3*l["w"]+3],detail=l["c"][10*l["w"]+1],sign=l["c"][13*l["w"]+15],
  grass=r101["c"][2*r101["w"]+2],ledge=r101["c"][6*r101["w"]+6],
  tree={0:r101["c"][0],1:r101["c"][1],2:r101["c"][r101["w"]],3:r101["c"][r101["w"]+1]},
  jump={"HOP_DOWN":r101["c"][6*r101["w"]+7],"HOP_RIGHT":r102["c"][5*r102["w"]+34],
        "HOP_LEFT":0x0485,"HOP_DOWN_LEFT":0x048D,"HOP_DOWN_RIGHT":0x048E},
  ocean=0x1170,edge=0x0592,shore=0x0473)
 for v in (d["ocean"],d["edge"],d["shore"]):
  if v not in r103["c"]: raise AssertionError(f"Route103 donor {v:#x} missing")
 return d

def evidence(e,d,names):
 maps={}
 for name in names:
  m=d[name]; maps[name]={"map_num":m["num"],"header":hex(m["header"]),"layout":hex(m["layout"]),"map_offset":hex(m["off"]),"width":m["w"],"height":m["h"],"map_sha256":sha(m["raw"])}
 return {"rom_sha256":sha(e),"map_groups_offset":hex(MAP_GROUPS),"maps":maps}

def build_route29(gsc,e,d):
 off,bw,bh,w,h=MAPS["route_29"]; blocks=gsc[off:off+bw*bh]; g=[d["ground"]]*(w*h); counts={}; sem=[None]*(w*h)
 for y in range(h):
  for x in range(w):
   b,q,s=src(blocks,bw,x,y); sem[y*w+x]=s; counts[s]=counts.get(s,0)+1; v=d["ground"]
   if s=="TALL_GRASS":v=d["grass"]
   elif s in {"HEADBUTT_TREE","CUT_TREE"} or (s=="WALL" and b in TREE):v=d["tree"][q]
   elif s.startswith("HOP_"):v=d["jump"][s]
   elif s=="WALL" and b in LEDGE:v=d["ledge"]
   elif b==0x02:v=d["detail"]
   g[y*w+x]=v
 apply_ledge_grammar(g,sem,w,h,d["ground"])
 paste(g,w,h,26,0,rect(d["o"],4,6,4,2))
 for x,y in ((51,7),(3,5)):g[y*w+x]=d["sign"]
 blob=outbytes(g)
 m={"schema":2,"policy":"GSC Route 29 supplies topology/cell semantics and events; Japanese Emerald supplies every visible target metatile.",
 "target":{"map":"Route 29","width":w,"height":h,"bytes":len(blob),"sha256":sha(blob)},
 "source":{"gsc_block_offset":hex(off),"block_sha256":sha(blocks),"gsc_rom_sha256":sha(gsc),"semantic_counts":counts},
 "emerald":evidence(e,d,["r101","r102","o","l"]),"preserved_warp_anchors":[[27,1]],
 "preserved_coord_events":[[53,8],[53,9]],"preserved_bg_events":[[51,7],[3,5]],
 "connections":[{"direction":"north","target_offset_metatiles":20},{"direction":"west","target_offset_metatiles":0},{"direction":"east","target_offset_metatiles":0}]}
 return blob,m

def build_cherry(gsc,e,d):
 off,bw,bh,w,h=MAPS["cherrygrove_city"]; blocks=gsc[off:off+bw*bh]; g=[d["ground"]]*(w*h); counts={}
 for y in range(h):
  for x in range(w):
   b,q,s=src(blocks,bw,x,y); counts[s]=counts.get(s,0)+1; v=d["ground"]
   if s=="WATER":v=d["ocean"]
   elif s=="BUOY":v=d["edge"]
   elif s in {"HEADBUTT_TREE","CUT_TREE"} or (s=="WALL" and b in TREE):v=d["tree"][q]
   elif s=="WALL" and b in COAST:v=d["shore"]
   elif b in {0x02,0x04,0x71}:v=d["detail"]
   g[y*w+x]=v
 o=d["o"]
 for x,y,p in ((22,0,rect(o,13,3,4,4)),(28,0,rect(o,5,13,4,4)),(16,4,rect(o,4,4,4,4)),(24,6,rect(o,14,13,4,4)),(30,8,rect(o,4,4,4,4))):paste(g,w,h,x,y,p)
 for x,y in ((30,8),(23,9)):g[y*w+x]=d["sign"]
 blob=outbytes(g)
 m={"schema":2,"policy":"GSC Cherrygrove supplies topology/coast/warps/events; Japanese Emerald Oldale+Route103 supply final town/building/ocean metatiles.",
 "target":{"map":"Cherrygrove City","width":w,"height":h,"bytes":len(blob),"sha256":sha(blob)},
 "source":{"gsc_block_offset":hex(off),"block_sha256":sha(blocks),"gsc_rom_sha256":sha(gsc),"semantic_counts":counts},
 "emerald":evidence(e,d,["o","r103","r101","l"]),"preserved_warp_anchors":[[23,3],[29,3],[17,7],[25,9],[31,11]],
 "preserved_coord_events":[[33,6],[33,7]],"preserved_bg_events":[[30,8],[23,9],[24,3],[30,3]],
 "connections":[{"direction":"north","target_offset_metatiles":10},{"direction":"east","target_offset_metatiles":0}]}
 return blob,m

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--gold-rom",required=True,type=Path); ap.add_argument("--emerald-rom",required=True,type=Path); ap.add_argument("--out-dir",required=True,type=Path); a=ap.parse_args()
 gsc=a.gold_rom.read_bytes(); e=a.emerald_rom.read_bytes(); d=donors(e); a.out_dir.mkdir(parents=True,exist_ok=True)
 for stem,fn in (("route_29",build_route29),("cherrygrove_city",build_cherry)):
  blob,m=fn(gsc,e,d); (a.out_dir/f"{stem}.map.bin").write_bytes(blob); (a.out_dir/f"{stem}.remake.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(m["target"]))
if __name__=="__main__":main()
