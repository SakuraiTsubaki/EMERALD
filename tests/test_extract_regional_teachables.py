from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location("extract_regional_teachables",ROOT/"tools"/"extract_regional_teachables.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
MASTER="""category,region,japaneseName,koreanName,key,teachableLearnset
regional_form,Alola,コラッタ,꼬렛,SPECIES_RATTATA_ALOLA,sRattataAlolaTeachableLearnset
regional_evolution,Galar,タチフサグマ,가로막구리,SPECIES_OBSTAGOON,sObstagoonTeachableLearnset
"""
HEADER="""static const u16 sRattataAlolaTeachableLearnset[] = { MOVE_PROTECT, MOVE_THIEF, };
const u16 sObstagoonTeachableLearnset[] = { MOVE_TAUNT, MOVE_SNARL, MOVE_END, };
"""
class ExtractRegionalTeachablesTests(unittest.TestCase):
 def test_complete_extract(self):
  r=m.extract(MASTER,HEADER);self.assertTrue(r["complete"]);self.assertEqual(r["master_rows"],2);self.assertEqual(r["entries"][0]["moves"],["MOVE_PROTECT","MOVE_THIEF"]);self.assertEqual(r["entries"][1]["moveCount"],3)
 def test_missing_symbol_is_reported(self):
  r=m.extract(MASTER,HEADER.splitlines()[0]);self.assertFalse(r["complete"]);self.assertEqual(r["missing"],[{"key":"SPECIES_OBSTAGOON","symbol":"sObstagoonTeachableLearnset"}])
 def test_markdown_contains_counts(self):
  text=m.markdown(m.extract(MASTER,HEADER));self.assertIn("Survey entries: 2",text);self.assertIn("`SPECIES_RATTATA_ALOLA`",text)
if __name__=="__main__":unittest.main()
