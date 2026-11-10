"""Parse the hand-checked transcriptions in data/*.txt + keys.txt into questions.json."""
import json, re, pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
keys = {}
for line in (HERE / "keys.txt").read_text(encoding="utf-8").splitlines():
    parts = line.split()
    keys[parts[0]] = [int(x) for x in parts[1:]]

out = {"schools": [], "mcq": [], "cloze": [], "dialogues": [], "vocab": []}

for f in sorted((HERE / "source").glob("*.txt")):
    sid = None
    cloze = None
    dialog = None
    for raw in f.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        if raw.startswith("@school"):
            sid, zh, en = raw.split(" ", 1)[1].split("|")
            out["schools"].append({"id": sid, "zh": zh, "en": en})
            key = keys[sid]
            continue
        tag, *rest = raw.split("|")
        if tag == "CLOZE":
            cloze = {"school": sid, "passage": rest[0].replace("\\n", "\n"), "blanks": []}
            out["cloze"].append(cloze)
        elif tag == "DOPT":
            dialog = {"school": sid, "options": rest[0].split(";"), "lines": [], "answers": {}}
            for n in (26, 27, 28, 29):
                dialog["answers"][str(n)] = key[n - 1] - 1
            out["dialogues"].append(dialog)
        elif tag == "L":
            dialog["lines"].append({"who": rest[0], "text": rest[1]})
        elif tag == "V":
            out["vocab"].append({"school": sid, "word": rest[0], "meaning": rest[1], "src": "def"})
        elif tag.startswith("Q"):
            n = int(tag[1:])
            override = None
            if rest and rest[-1].startswith("!"):
                override = int(rest[-1][1:])
                rest = rest[:-1]
            ans = (override or key[n - 1]) - 1
            note = None
            if override and override != key[n - 1]:
                note = f"（学校答案卷写的是 {key[n-1]}，但根据上下文，正确答案应为 {override}。）"
            if 16 <= n <= 20:
                cloze["blanks"].append({"n": n, "options": rest[0].split(";"), "answer": ans, "note": note})
            else:
                qtype, stem, opts = rest
                out["mcq"].append({
                    "id": f"{sid}-Q{n}", "school": sid, "n": n, "type": qtype,
                    "stem": stem, "options": opts.split(";"), "answer": ans, "note": note,
                })

# Derive vocab from meaning questions (underlined word -> correct meaning) and pinyin questions.
for q in out["mcq"]:
    m = re.search(r"【(.+?)】", q["stem"])
    if not m:
        continue
    w = m.group(1)
    if q["type"] == "meaning":
        out["vocab"].append({"school": q["school"], "word": w, "meaning": q["options"][q["answer"]],
                             "src": "meaning", "example": q["stem"].replace("【", "").replace("】", "")})
    elif q["type"] == "pinyin":
        out["vocab"].append({"school": q["school"], "word": w, "pinyin": q["options"][q["answer"]],
                             "src": "pinyin", "example": q["stem"].replace("【", "").replace("】", "")})

# Sanity checks
for q in out["mcq"]:
    assert len(q["options"]) == 4, q["id"]
for c in out["cloze"]:
    assert len(c["blanks"]) == 5 and all(len(b["options"]) == 4 for b in c["blanks"]), c["school"]
    for b in c["blanks"]:
        assert "{%d}" % b["n"] in c["passage"], (c["school"], b["n"])
for d in out["dialogues"]:
    text = "".join(l["text"] for l in d["lines"])
    for n in d["answers"]:
        assert "{%s}" % n in text, (d["school"], n)

(ROOT / "data").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "questions.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print(len(out["mcq"]), "mcq", Counter(q["type"] for q in out["mcq"]))
print(len(out["cloze"]), "cloze", len(out["dialogues"]), "dialogues", len(out["vocab"]), "vocab")
