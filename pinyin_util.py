"""Hanyu Pinyin for every Chinese character, with fixes for the polyphones pypinyin gets wrong in these papers."""
from functools import lru_cache
import re

from pypinyin import pinyin, Style

HAN = re.compile(r"[一-鿿]")

# (phrase, index of the char inside the phrase, correct reading)
PHRASE_FIX = [
    ("太长", 1, "cháng"), ("只受伤", 0, "zhī"), ("那只", 1, "zhī"), ("乱发", 1, "fā"),
    ("尽一份", 0, "jìn"), ("想尽", 1, "jìn"), ("重画", 0, "chóng"), ("对着", 1, "zhe"),
    ("还得", 1, "děi"), ("照片", 1, "piàn"), ("推倒", 1, "dǎo"), ("伯伯", 0, "bó"),
    ("伯伯", 1, "bo"), ("值得", 1, "dé"), ("舍不得", 2, "de"), ("记得", 1, "de"),
    ("觉得", 1, "de"), ("显得", 1, "de"), ("第一", 1, "yī"),
]

DI_NOUN_NEXT = set("铁方上下面球图点区址毯板位址步")
DI_NOUN_PREV = set("营土场园基田草陆大天本外各当")
DE_DE_PREV = set("取获赢值")
DE_DE_NEXT = set("到奖")
JIAO_NEXT = set("育导训室练师授")


@lru_cache(maxsize=4096)
def py_list(text: str):
    """Return a list of (char, reading-or-None) for each character in text."""
    raw = pinyin(text, style=Style.TONE, errors=lambda s: [[None] for _ in s])
    out = [r[0] for r in raw]
    if len(out) != len(text):  # safety: fall back char-by-char
        out = [pinyin(c, style=Style.TONE)[0][0] if HAN.match(c) else None for c in text]
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else ""
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if ch == "都":
            out[i] = "dōu"
        elif ch == "地":
            out[i] = "dì" if (nxt in DI_NOUN_NEXT or prev in DI_NOUN_PREV) else "de"
        elif ch == "得":
            if prev in DE_DE_PREV or nxt in DE_DE_NEXT or nxt == "了" or (nxt and nxt in "第冠"):
                out[i] = "dé"
            else:
                out[i] = "de"
        elif ch == "教":
            out[i] = "jiào" if nxt in JIAO_NEXT else "jiāo"
    for phrase, k, reading in PHRASE_FIX:
        start = 0
        while True:
            j = text.find(phrase, start)
            if j < 0:
                break
            out[j + k] = reading
            start = j + 1
    return list(zip(text, out))


def ruby(text: str, hide=()):
    """HTML with pinyin above each Chinese character. Characters at positions in `hide` get no pinyin."""
    parts = []
    for i, (ch, p) in enumerate(py_list(text)):
        if p and HAN.match(ch) and i not in hide:
            parts.append(f"<ruby>{ch}<rt>{p}</rt></ruby>")
        else:
            parts.append(ch)
    return "".join(parts)


def plain(text: str):
    """Pinyin as a plain string (words not split), e.g. for flashcards."""
    return " ".join(p for ch, p in py_list(text) if p and HAN.match(ch))
