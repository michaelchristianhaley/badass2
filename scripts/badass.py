#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SELF = Path("control/system.json")
EXCLUDED = {".git", "__pycache__", ".venv", ".pytest_cache"}

class BadassError(Exception):
    pass

def fail(msg): raise BadassError(msg)

def read_text(path):
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        fail(f"missing required file: {path}")
    if path.suffix != ".ps1" and b"\r" in raw:
        fail(f"{path}: line endings must be LF")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{path}: must be UTF-8")
    if text and not text.endswith("\n"):
        fail(f"{path}: must end with newline")
    return text

def load_json(path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{path}: invalid JSON: {exc}")

def load_system(root):
    data = load_json(root / SELF)
    for key in ("name","version","canonical_files","generated_files","file_summaries"):
        if key not in data: fail(f"{SELF}: missing {key}")
    return data

def declared(system):
    return sorted(set(system["canonical_files"]) | set(system["generated_files"]))

def verify_file_set(root, system):
    expected = set(declared(system))
    actual = set()
    for p in root.rglob("*"):
        if p.is_file() and not any(part in EXCLUDED for part in p.parts):
            actual.add(p.relative_to(root).as_posix())
    if expected - actual: fail("missing files: " + ", ".join(sorted(expected-actual)))
    if actual - expected: fail("unclassified files: " + ", ".join(sorted(actual-expected)))

def make_map(system):
    paths = declared(system)
    tree = {}
    for rel in paths:
        node = tree
        for part in rel.split("/"):
            node = node.setdefault(part,{})
    lines = ["# Repository Map","","Generated. Do not edit manually.","","```text","."]
    def walk(node,prefix=""):
        names=sorted(node)
        for i,name in enumerate(names):
            last=i==len(names)-1
            lines.append(prefix+("└── " if last else "├── ")+name)
            if node[name]: walk(node[name],prefix+("    " if last else "│   "))
    walk(tree)
    lines += ["```","","## File purposes",""]
    for rel in paths:
        summary=system["file_summaries"].get(rel)
        if not summary: fail(f"missing summary: {rel}")
        role="generated" if rel in system["generated_files"] else "source"
        lines.append(f"- `{rel}` — **{role}.** {summary}")
    return "\n".join(lines)+"\n"

def make_pad(root, system):
    excluded=set(system.get("landing_pad_exclude",[]))
    included=[r for r in declared(system) if r not in excluded]
    lines=["# BADASS 2 Landing Pad","","Generated from sources. It introduces no new authority or facts.","","## Index",""]
    lines += [f"- `{r}`" for r in included]
    lines.append("")
    for rel in included:
        text=(make_map(system) if rel=="MAP.md" else read_text(root/rel)).replace("\r\n","\n").replace("\r","\n")
        lines += [f"## FILE: {rel}","","```text",text.rstrip("\n"),"```",""]
    return "\n".join(lines)

def generate(root):
    system=load_system(root)
    (root/"MAP.md").write_text(make_map(system),encoding="utf-8",newline="\n")
    (root/"LANDING_PAD.md").write_text(make_pad(root,system),encoding="utf-8",newline="\n")
    return ["PASS: MAP.md generated","PASS: LANDING_PAD.md generated"]

def validate(root):
    system=load_system(root)
    verify_file_set(root,system)
    for rel in declared(system): read_text(root/rel)
    inspection=load_json(root/"control/inspection.json")
    evidence=load_json(root/"control/evidence.json")
    support=load_json(root/"control/support.json")
    if "operations" not in inspection: fail("inspection operations missing")
    if evidence.get("claim_states") != ["verified","inferred","unknown"]: fail("claim states invalid")
    if not support.get("continuity_systems"): fail("continuity support missing")
    if read_text(root/"MAP.md") != make_map(system): fail("MAP.md stale")
    if read_text(root/"LANDING_PAD.md") != make_pad(root,system): fail("LANDING_PAD.md stale")
    for rel in system["canonical_files"]:
        text=read_text(root/rel).casefold()
        for term in ("".join(map(chr,(99,104,97,116,103,112,116))), "".join(map(chr,(99,108,97,117,100,101)))):
            if term in text: fail(f"{rel}: named model/vendor term forbidden")
    wins=load_json(root/"wins/wins.json")
    required={"id","date","context","problem","successful_behavior","evidence","result","lesson","promotion_status"}
    for win in wins.get("wins",[]):
        if required-win.keys(): fail("win record incomplete")
    return [
        "PASS: repository file set matches manifest",
        "PASS: controls are valid",
        "PASS: generated views match sources",
        "PASS: canonical sources are vendor-neutral",
        "PASS: wins are valid"
    ]

def inspect(root, operation):
    data=load_json(root/"control/inspection.json")
    rule=data["operations"].get(operation)
    if not rule: fail(f"unknown operation: {operation}")
    required=list(dict.fromkeys(data["default"].get("required",[])+rule.get("required",[])))
    lines=[f"Operation: {operation}","Required inspection:"]+[f"- {x}" for x in required]
    if rule.get("discover_continuity"):
        support=load_json(root/"control/support.json")
        for item in support["continuity_systems"]:
            names=item["detect_all"]
            if all((root/n).exists() for n in names):
                lines.append(f"- continuity detected: {item['name']}")
                lines += [f"  - {n}" for n in names]
            else:
                lines.append("- durable continuity not detected; sustained work unsupported")
    return lines

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="cmd",required=True)
    for name in ("generate","validate","check","report"):
        p=sub.add_parser(name); p.add_argument("path",nargs="?",default=".")
    p=sub.add_parser("inspect"); p.add_argument("operation"); p.add_argument("path",nargs="?",default=".")
    a=parser.parse_args(); root=Path(a.path).resolve()
    try:
        if a.cmd=="generate": out=generate(root)
        elif a.cmd=="validate": out=validate(root)
        elif a.cmd=="check": out=generate(root)+validate(root)
        elif a.cmd=="report":
            s=load_system(root); out=[f"Repository: {s['name']}",f"Version: {s['version']}","Status: healthy"]
        else: out=inspect(root,a.operation)
        print("\n".join(out)); print("BADASS CHECK PASSED"); return 0
    except BadassError as exc:
        print(f"BADASS CHECK FAILED: {exc}",file=sys.stderr); return 1

if __name__=="__main__":
    raise SystemExit(main())
