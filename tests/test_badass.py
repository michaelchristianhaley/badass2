import json, shutil, tempfile, unittest
from pathlib import Path
from scripts import badass

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(__file__).resolve().parents[1]

    def copy(self):
        root=Path(tempfile.mkdtemp())/"repo"
        shutil.copytree(self.repo,root,ignore=shutil.ignore_patterns(".git","__pycache__"))
        return root

    def test_self(self):
        badass.generate(self.repo)
        self.assertTrue(any("generated views" in x for x in badass.validate(self.repo)))

    def test_orphan(self):
        root=self.copy(); (root/"orphan.txt").write_text("x\n", encoding="utf-8", newline="\n")
        with self.assertRaises(badass.BadassError): badass.validate(root)

    def test_stale_map(self):
        root=self.copy(); (root/"MAP.md").write_text("stale\n", encoding="utf-8", newline="\n")
        with self.assertRaises(badass.BadassError): badass.validate(root)

    def test_bad_claim_states(self):
        root=self.copy()
        p=root/"control/evidence.json"; d=json.loads(p.read_text()); d["claim_states"]=["sure"]; p.write_text(json.dumps(d,indent=2)+"\n", encoding="utf-8", newline="\n")
        badass.generate(root)
        with self.assertRaises(badass.BadassError): badass.validate(root)

    def test_continuity_detection(self):
        root=self.copy()
        for n in ("OUTLINE.md","WISDOM.md","LEGACY.md"): (root/n).write_text(f"# {n}\n", encoding="utf-8", newline="\n")
        self.assertTrue(any("continuity detected" in x for x in badass.inspect(root,"project_work")))

if __name__=="__main__": unittest.main()
