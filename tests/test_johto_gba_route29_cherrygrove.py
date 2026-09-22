#!/usr/bin/env python3
import hashlib, json, struct, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'/'johto-gba-remake-slice'

def cells(name):
 b=(ART/f'{name}.map.bin').read_bytes(); return b,[x[0] for x in struct.iter_unpack('<H',b)]
def mid(v): return v&0x3ff
class JohtoRoute29CherrygroveTest(unittest.TestCase):
 def test_route29(self):
  m=json.loads((ART/'route_29.remake.json').read_text()); b,c=cells('route_29'); w=60
  self.assertEqual((m['target']['width'],m['target']['height'],len(b)),(60,18,2160))
  self.assertEqual(hashlib.sha256(b).hexdigest(),'61831f1d329cd823cd0d3153cb7297dd3e58a8bb27aadcb32e36631d131a2a97')
  self.assertEqual(mid(c[1*w+27]),0x287)
  self.assertEqual([mid(c[y*w+x]) for x,y in ((51,7),(3,5))],[0x003,0x003])
  ids=[mid(v) for v in c]
  for x in (0x00D,0x085,0x086,0x087,0x08D,0x08E): self.assertIn(x,ids)
  self.assertEqual(m['preserved_coord_events'],[[53,8],[53,9]])
  self.assertEqual(m['connections'][0],{'direction':'north','target_offset_metatiles':20})
 def test_cherrygrove(self):
  m=json.loads((ART/'cherrygrove_city.remake.json').read_text()); b,c=cells('cherrygrove_city'); w=40
  self.assertEqual((m['target']['width'],m['target']['height'],len(b)),(40,18,1440))
  self.assertEqual(hashlib.sha256(b).hexdigest(),'dd1bdede9b8c053ec4b98eec3ce72232b0b472300347cd91f6b471b10518a5fe')
  expected={(23,3):0x041,(29,3):0x061,(17,7):0x287,(25,9):0x287,(31,11):0x287,(24,3):0x042,(30,3):0x062,(30,8):0x003,(23,9):0x003}
  for (x,y),v in expected.items(): self.assertEqual(mid(c[y*w+x]),v,(x,y))
  self.assertGreater(sum(mid(v)==0x170 for v in c),100)
  self.assertEqual(m['preserved_coord_events'],[[33,6],[33,7]])
 def test_master_reference_hashes_and_policy(self):
  for name in ('route_29','cherrygrove_city'):
   m=json.loads((ART/f'{name}.remake.json').read_text())
   self.assertEqual(m['source']['gsc_rom_sha256'],'7cfeceae00737a1f0713c9ab0b3a9e6eb8d05ff6002eb81308072a6f85e385e7')
   self.assertEqual(m['emerald']['rom_sha256'],'33f5610b9186b4add09fef68895deb00f552b997b3d133b5a961e5123506343c')
   self.assertNotIn('.gbc',json.dumps(m)); self.assertNotIn('.gba',json.dumps(m))
   self.assertIn('GSC',m['policy']); self.assertIn('Emerald',m['policy'])
if __name__=='__main__':unittest.main()
