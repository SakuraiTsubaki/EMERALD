#!/usr/bin/env python3
import hashlib,json,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'/'johto-gba-remake-slice'
def read(name):
 b=(ART/f'{name}.map.bin').read_bytes();return b,[x[0] for x in struct.iter_unpack('<H',b)]
def mid(v):return v&0x3ff
class T(unittest.TestCase):
 def test_route30(self):
  m=json.loads((ART/'route_30.remake.json').read_text());b,c=read('route_30');w=20
  self.assertEqual((m['target']['width'],m['target']['height'],len(b)),(20,54,2160))
  self.assertEqual(hashlib.sha256(b).hexdigest(),'be0f5000f0f50376eaabbd9609fd8c798d27350a934f1a4af59ab8037ac2bc5b')
  self.assertEqual(m['target']['tileset_profile'],'General+Petalburg')
  self.assertEqual(mid(c[39*w+7]),0x287);self.assertEqual(mid(c[5*w+17]),0x287)
  for x,y in ((9,43),(13,29),(15,5),(3,21)):self.assertEqual(mid(c[y*w+x]),0x003)
  self.assertEqual(len(m['source']['version_evidence']['canonical']['events']['objects']),10)
  self.assertEqual(len(m['source']['version_evidence']['revisions']['crystal_rev0']['differences_from_gold_rev0']['events']['objects']),11)
  self.assertEqual(m['source']['version_evidence']['canonical']['block_sha256'],m['source']['version_evidence']['revisions']['crystal_rev0']['block_sha256'])
 def test_route31(self):
  m=json.loads((ART/'route_31.remake.json').read_text());b,c=read('route_31');w=40
  self.assertEqual((m['target']['width'],m['target']['height'],len(b)),(40,18,1440))
  self.assertEqual(hashlib.sha256(b).hexdigest(),'fede6ba4ad05bb792dd8d8e5e075c1bcbe43cdaed3659f2f13bd280a8fdc2333')
  self.assertEqual(m['target']['tileset_profile'],'General+Rustboro')
  self.assertEqual(mid(c[6*w+4]),0x30e);self.assertEqual(mid(c[7*w+4]),0x30e)
  self.assertEqual(mid(c[5*w+34]),0x0a7)
  for x,y in ((7,5),(31,5)):self.assertEqual(mid(c[y*w+x]),0x003)
  self.assertEqual(m['source']['version_evidence']['canonical']['events']['warps'][2]['destMap'],70)
  self.assertEqual(m['source']['version_evidence']['revisions']['crystal_rev0']['differences_from_gold_rev0']['events']['warps'][2]['destMap'],78)
 def test_violet(self):
  m=json.loads((ART/'violet_city.remake.json').read_text());b,c=read('violet_city');w=40
  self.assertEqual((m['target']['width'],m['target']['height'],len(b)),(40,36,2880))
  self.assertEqual(hashlib.sha256(b).hexdigest(),'66a12508831c98c9c87c14304e8f0beb307b95e9d3bb65c6d08e870aaa5ffd4d')
  self.assertEqual(m['target']['tileset_profile'],'General+Rustboro')
  expected={(9,17):0x041,(18,17):0x1cd,(30,17):0x22f,(3,15):0x21f,(31,25):0x061,(21,29):0x21f,(23,5):0x2b5,(39,24):0x30e,(39,25):0x30e}
  for (x,y),v in expected.items():self.assertEqual(mid(c[y*w+x]),v,(x,y))
  for x,y in ((24,20),(15,17),(24,8),(27,17),(32,25),(10,17)):self.assertEqual(mid(c[y*w+x]),0x003)
  self.assertEqual(m['source']['gold_silver_block_sha256'],'4b16374929e3e1d1ed21844607051cd9d87c928b3cdb0d6e904faa9a5a52e43d')
  self.assertEqual(m['source']['crystal_block_sha256'],'a62ad6ab6e918e58fddfc3bd22ee0a0019643857407a631c8097784b13b17ff6')
  self.assertEqual(m['source']['source_block_differences'],[
   {'block_x':14,'block_y':7,'gs':'0x20','crystal':'0x2c'},
   {'block_x':15,'block_y':7,'gs':'0x3b','crystal':'0x2a'},
   {'block_x':16,'block_y':7,'gs':'0x21','crystal':'0x2d'}])
 def test_no_rom_paths_or_gsc_pixel_output(self):
  for name in ('route_30','route_31','violet_city'):
   p=ART/f'{name}.remake.json';m=json.loads(p.read_text());raw=p.read_text()
   self.assertNotIn('/mnt/data',raw);self.assertIn('GSC supplies',m['policy']);self.assertIn('Emerald',m['policy'])
if __name__=='__main__':unittest.main()
