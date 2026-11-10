"""List every Chinese string that needs an English translation, per school, in a fixed order."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "questions.json").read_text(encoding="utf-8"))

def needed(sid):
    out = []
    def add(s):
        if s not in out:
            out.append(s)
    for q in D["mcq"]:
        if q["school"] != sid: continue
        add(q["stem"])
        m = re.search(r"【(.+?)】", q["stem"])
        if m: add(m.group(1))
        if q["type"] == "usage":
            add(re.search(r"（(.+?)）", q["stem"]).group(1))
        if q["type"] not in ("pinyin", "hanzi"):
            for o in q["options"]: add(o)
    for c in D["cloze"]:
        if c["school"] != sid: continue
        for p in c["passage"].split("\n"): add(p)
        for b in c["blanks"]:
            for o in b["options"]: add(o)
    for d in D["dialogues"]:
        if d["school"] != sid: continue
        for o in d["options"]: add(o)
        for l in d["lines"]: add(l["text"])
    for v in D["vocab"]:
        if v["school"] != sid or v["src"] != "def": continue
        add(v["word"]); add(v["meaning"])
    return out

if __name__ == "__main__":
    import sys
    for s in D["schools"]:
        if len(sys.argv) > 1 and s["id"] not in sys.argv[1:]: continue
        items = needed(s["id"])
        print(f"### {s['id']} ({len(items)})")
        for i, x in enumerate(items, 1):
            print(f"{i}\t{x}")
