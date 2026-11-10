"""
小六华文冲冲冲！ — P6 Chinese practice app (with Hanyu Pinyin + English support)
Questions come from 10 schools' 2026 P6 Chinese Preliminary Examination papers (Paper 2).
Run locally:  streamlit run app.py
"""
import json
import random
import re
import datetime as dt
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from pinyin_util import py_list, plain, HAN

st.set_page_config(page_title="小六华文冲冲冲！", page_icon="🐼", layout="centered",
                   initial_sidebar_state="auto")

DATA = json.loads((Path(__file__).parent / "data" / "questions.json").read_text(encoding="utf-8"))
SCHOOLS = {s["id"]: s for s in DATA["schools"]}
MCQ = {q["id"]: q for q in DATA["mcq"]}
CLOZE = DATA["cloze"]
DIALOGUES = DATA["dialogues"]
VOCAB = DATA["vocab"]
EN = DATA["en"]                                   # school -> {chinese: english}
EN_ALL = {}
for _d in EN.values():
    for _k, _v in _d.items():
        EN_ALL.setdefault(_k, _v)
EN_STRIPPED = {re.sub("【|】", "", k): v for k, v in EN_ALL.items()}


def en(zh, school=None):
    if school and zh in EN.get(school, {}):
        return EN[school][zh]
    return EN_ALL.get(zh) or EN_STRIPPED.get(zh) or ""


# --------------------------------------------------------------------------- help levels
LEVELS = {
    "learn":    dict(icon="🟢", zh="学习", en="Learn", desc="Pinyin + English shown", mult=1.0),
    "practice": dict(icon="🟡", zh="练习", en="Practice", desc="Pinyin shown · English on tap", mult=1.5),
    "exam":     dict(icon="🔴", zh="考试", en="Exam", desc="Chinese only, like the real paper", mult=2.0),
}

CATS = {
    "pinyin":    dict(icon="🔤", zh="拼音小达人", en="Hanyu Pinyin", color="#FF6B6B", tip="选出画线词语的汉语拼音", tip_en="Choose the pinyin of the underlined word"),
    "hanzi":     dict(icon="✍️", zh="汉字侦探",   en="Correct character", color="#FFA94D", tip="选出正确的字", tip_en="Choose the correct character for the blank"),
    "word":      dict(icon="📚", zh="词语百宝箱", en="Choose the word", color="#FFD43B", tip="选出最适当的词语", tip_en="Choose the most suitable word"),
    "meaning":   dict(icon="💡", zh="词义解码",   en="Word meanings", color="#69DB7C", tip="画线词语是什么意思？", tip_en="What does the underlined word mean?"),
    "connector": dict(icon="🔗", zh="关联词魔法", en="Connectors (grammar)", color="#38D9A9", tip="选出正确的关联词", tip_en="Choose the correct linking words"),
    "sentence":  dict(icon="🧩", zh="句子拼图",   en="Complete the sentence", color="#4DABF7", tip="选出最适当的句子", tip_en="Choose the best part to complete the sentence"),
    "usage":     dict(icon="⚖️", zh="用词小法官", en="Correct usage", color="#748FFC", tip="哪一个句子是正确的？", tip_en="Which sentence uses the word correctly?"),
    "cloze":     dict(icon="📖", zh="短文填空",   en="Passage fill-in-the-blanks", color="#DA77F2", tip="根据上下文选出适当的词语", tip_en="Choose the best word for the highlighted blank"),
    "dialog":    dict(icon="💬", zh="完成对话",   en="Complete the dialogue", color="#F783AC", tip="从表中选出适当的短语或短句", tip_en="Choose the best phrase from the box for the blank"),
    "vocab":     dict(icon="🌏", zh="词语大考验", en="Word quiz", color="#20C997", tip="词语和意思配对", tip_en="Match words and meanings"),
}
CORE_CATS = [c for c in CATS if c != "vocab"]
CHEERS = [("太棒了！", "Awesome!"), ("真厉害！", "So clever!"), ("答对啦！", "Correct!"), ("好聪明！", "Smart!"),
          ("继续加油！", "Keep going!"), ("你是华文小高手！", "You're a Chinese star!"), ("完全正确！", "Totally right!")]
COMFORT = [("没关系，再接再厉！", "That's OK — try the next one!"), ("别灰心！", "Don't give up!"),
           ("错了也是学习哦！", "Mistakes help us learn!"), ("记住它，下次就会了！", "Remember it for next time!")]

CONNECTOR_NOTES = {
    "只要": ("只要……就……：条件关系", "'as long as … then': if this condition is met, the result follows"),
    "只有": ("只有……才……：条件关系", "'only if … then': this is the ONLY condition that works"),
    "虽然": ("虽然……但是……：转折关系", "'although … but': the two parts go against each other"),
    "尽管": ("尽管……还是……：转折关系", "'even though … still': the result doesn't change"),
    "就算": ("就算……也……：假设让步", "'even if … still': even in that case, the result stays the same"),
    "即使": ("即使……也……：假设让步", "'even if … still': even in that case, the result stays the same"),
    "如果": ("如果……就……：假设关系", "'if … then': imagine a situation and its result"),
    "要是": ("要是……就……：假设关系", "'if … then' (same as 如果……就……)"),
    "不管": ("不管……都/还是/仍然……：条件关系", "'no matter … still': the result is the same in every case"),
    "无论": ("无论……都……：条件关系", "'no matter … all': the result is the same in every case"),
    "不仅": ("不仅……而且……：递进关系", "'not only … but also': the second part goes one step further"),
    "不但": ("不但……而且……：递进关系", "'not only … but also' (不但不……反而 = 'not only not … but instead')"),
    "除了": ("除了……还/也……：补充关系", "'besides … also': adds something extra"),
    "因为": ("因为……所以……：因果关系", "'because … so': cause and effect"),
    "由于": ("由于……因此/所以……：因果关系", "'due to … therefore': cause and effect"),
    "不是": ("不是……而是…… / 不是……就是……", "'not A but B' (而是), or 'if not A then B' — always one of the two (就是)"),
    "一边": ("一边……一边……：并列关系", "'while … while': doing two things at the same time"),
    "首先": ("首先……然后……：顺承关系", "'first … then': the order of steps"),
    "反正": ("反正……不如……", "'anyway … might as well': since things are like this, choose the second"),
    "除非": ("除非……不然……", "'unless … otherwise': the only way to avoid the result"),
    "凡是": ("凡是……都/就……", "'all / whatever': everything that fits the condition"),
    "与其": ("与其……不如……：选择关系", "'rather than … it's better to': compare and pick the second"),
    "简直": ("简直", "'simply / practically': strong, exaggerated tone"),
    "明明": ("明明", "'clearly / obviously' (usually followed by a 'but')"),
    "竟然": ("竟然", "'unexpectedly': something surprising happened"),
    "大约": ("大约", "'about / approximately': a guess at a number or time"),
}


def css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, li, label, button { font-family: 'Noto Sans SC', sans-serif; }
.stApp { background: radial-gradient(circle at 10% 0%, #FFF3BF 0, transparent 35%),
                     radial-gradient(circle at 100% 30%, #D0EBFF 0, transparent 40%),
                     radial-gradient(circle at 0% 100%, #FFDEEB 0, transparent 40%), #FFFDF7; }
h1, h2, h3, .fun { font-family: 'ZCOOL KuaiLe', 'Noto Sans SC', cursive !important; letter-spacing: 1px; }
ruby { ruby-align: center; margin: 0 .09em; } rt { font-size: .52em; color: #E8590C; font-family: 'Noto Sans SC', sans-serif; letter-spacing: 0; font-weight: 400; }
.en { color:#1971C2; font-size:1rem; line-height:1.5rem; margin-top:6px; font-style: italic; }
.en.small { font-size:.92rem; }
.hero { text-align:center; padding: 6px 0 2px 0; }
.hero h1 { font-size: 2.6rem; margin: 0; background: linear-gradient(90deg,#FF6B6B,#FFA94D,#FCC419,#51CF66,#339AF0,#CC5DE8);
  -webkit-background-clip:text; background-clip:text; color: transparent; }
.hero p { color:#555; margin:0; }
.bubble { background:#fff; border:3px solid #FFD43B; border-radius:22px; padding:12px 18px; margin:8px 0 14px 0;
  box-shadow: 0 4px 0 #FCC419; font-size:1.05rem; line-height:1.9rem; }
.qcard { background:#fff; border-radius:22px; padding:20px 22px; margin:6px 0 14px 0;
  box-shadow: 0 6px 0 rgba(0,0,0,.08), 0 10px 24px rgba(0,0,0,.06); border-top: 10px solid var(--c); }
.qtag { display:inline-block; background: var(--c); color:#fff; border-radius:999px; padding:2px 12px; font-size:.85rem; margin-bottom:8px; }
.qtext { font-size:1.45rem; line-height:2.7rem; color:#222; }
.qtext u, .hl, .res u, .feedback u, .say u, .passage u { text-decoration: none; border-bottom: 4px solid #FF6B6B; padding: 0 2px; font-weight:700; }
.blank { display:inline-block; min-width:70px; border-bottom:3px dashed #868E96; text-align:center; color:#868E96; }
.passage { font-size:1.2rem; line-height:2.6rem; background:#fff; border-radius:18px; padding:16px 20px; box-shadow: inset 0 0 0 3px #F3D9FA; }
.chip { display:inline-block; border-radius:10px; padding:0 8px; margin:0 2px; font-weight:700; line-height:2.2rem; }
.chip.ok { background:#D3F9D8; color:#2B8A3E; } .chip.no { background:#FFE3E3; color:#C92A2A; }
.chip.now { background:#FFF3BF; color:#E67700; border:2px solid #FCC419; animation: pulse 1.2s infinite; }
.chip.todo { background:#F1F3F5; color:#868E96; }
@keyframes pulse { 0%{transform:scale(1)} 50%{transform:scale(1.08)} 100%{transform:scale(1)} }
.chat { display:flex; gap:10px; margin:8px 0; align-items:flex-start; }
.chat .who { min-width:62px; font-weight:700; color:#fff; border-radius:12px; padding:4px 8px; text-align:center; font-size:.95rem; }
.chat .say { background:#fff; border-radius:16px; padding:8px 14px; font-size:1.12rem; line-height:2.4rem; box-shadow:0 2px 0 rgba(0,0,0,.07); }
.bank { background:#FFF9DB; border:2px dashed #FCC419; border-radius:16px; padding:10px 16px; font-size:1.05rem; line-height:2.3rem; }
.res { border-radius:16px; padding:10px 16px; margin:6px 0; font-size:1.15rem; line-height:2.3rem; border:3px solid transparent; background:#fff; }
.res.right { border-color:#40C057; background:#EBFBEE; } .res.wrong { border-color:#FA5252; background:#FFF5F5; }
.res.dim { opacity:.6; }
.feedback { border-radius:18px; padding:14px 18px; margin:10px 0; font-size:1.1rem; line-height:2.3rem; }
.feedback.good { background: linear-gradient(135deg,#D3F9D8,#C3FAE8); border:3px solid #51CF66; }
.feedback.bad { background: linear-gradient(135deg,#FFE3E3,#FFF0F6); border:3px solid #FF8787; }
.stat { background:#fff; border-radius:16px; padding:8px; text-align:center; box-shadow:0 3px 0 rgba(0,0,0,.08); }
.stat b { font-size:1.5rem; display:block; font-family:'ZCOOL KuaiLe',cursive; }
.flash { background: linear-gradient(135deg,#E5DBFF,#D0EBFF); border-radius:26px; padding:30px 20px; text-align:center;
  box-shadow:0 8px 0 #B197FC; margin: 10px 0 16px 0; }
.flash .w { font-size:3.2rem; line-height:5rem; font-family:'ZCOOL KuaiLe',cursive; color:#5F3DC4; }
.flash .m { font-size:1.2rem; color:#333; margin-top:8px; line-height:2.3rem; }
.badge { display:inline-block; background:#fff; border-radius:14px; padding:6px 10px; margin:4px; box-shadow:0 2px 0 rgba(0,0,0,.1); }
.lvl { border-radius:16px; padding:8px 12px; margin:4px 0 10px 0; font-size:.95rem; background:#fff; border:2px solid #E9ECEF; }
div.stButton > button { border-radius:16px; font-size:1.12rem; padding:.55rem 1rem; border:3px solid #E9ECEF;
  box-shadow:0 4px 0 #DEE2E6; transition: transform .05s; width:100%; white-space: normal; }
div.stButton > button p { white-space: pre-line !important; overflow: visible !important; text-overflow: clip !important; line-height:1.6rem; }
div.stButton > button em { color:#1971C2; font-size:.92rem; }
.tile { background: linear-gradient(160deg, #fff 0%, #fff 55%, color-mix(in srgb, var(--c) 22%, #fff) 100%);
  border-radius: 22px 22px 8px 8px; padding: 14px 12px 10px 12px; text-align:center; border: 3px solid var(--c);
  box-shadow: 0 5px 0 var(--c); margin-bottom: 8px; }
.tile .ti { font-size: 2.3rem; line-height: 2.8rem; }
.tile .tz { font-family:'ZCOOL KuaiLe',cursive; font-size: 1.45rem; color:#222; line-height:2.6rem; }
.tile .te { font-size: .82rem; color:#777; }
.tile .ts { display:inline-block; margin-top:6px; font-size:.82rem; background: var(--c); color:#fff; border-radius:999px; padding:1px 10px; }
[class*="st-key-go_"] button { background: #fff; font-weight:700; padding:.3rem .8rem; margin-bottom: 14px; }
[class*="st-key-hint"] button { font-size:.95rem; padding:.25rem .6rem; background:#E7F5FF; border-color:#A5D8FF; box-shadow:0 3px 0 #A5D8FF; }
div.stButton > button:hover { border-color:#FCC419; transform: translateY(-1px); }
div.stButton > button:active { transform: translateY(3px); box-shadow:0 1px 0 #DEE2E6; }
[class*="st-key-c0_"] button { background:#FFF5F5; } [class*="st-key-c1_"] button { background:#F4FCE3; }
[class*="st-key-c2_"] button { background:#E7F5FF; } [class*="st-key-c3_"] button { background:#FFF9DB; }
[class*="st-key-c4_"] button { background:#F8F0FC; } [class*="st-key-c5_"] button { background:#E6FCF5; }
[class*="st-key-c6_"] button { background:#FFF4E6; } [class*="st-key-c7_"] button { background:#EDF2FF; }
[class*="st-key-c8_"] button { background:#FFF0F6; }
.st-key-next button, .st-key-start button { background: linear-gradient(90deg,#51CF66,#38D9A9) !important; color:#fff !important;
  border-color:#2F9E44 !important; box-shadow:0 4px 0 #2F9E44 !important; font-weight:700; }
</style>""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- text rendering
TOK = re.compile(r"(【|】|___|\{\d+\})")


def rich(text, py=True, repl=None, hide_ul=False):
    """Chinese text -> HTML with pinyin (ruby) above each character.
    【…】 underline, ___ blank, {n} replaced from repl. hide_ul hides pinyin inside 【…】."""
    parts = TOK.split(text)
    clean = "".join(p for p in parts if not TOK.fullmatch(p))
    pl = py_list(clean) if py else None
    out, pos, in_ul = [], 0, False
    for p in parts:
        if p == "【":
            out.append("<u>")
            in_ul = True
        elif p == "】":
            out.append("</u>")
            in_ul = False
        elif p == "___":
            out.append("<span class='blank'>？</span>")
        elif TOK.fullmatch(p):
            out.append((repl or {}).get(p, p))
        else:
            for ch in p:
                r = pl[pos][1] if pl else None
                if r and HAN.match(ch) and not (hide_ul and in_ul):
                    out.append(f"<ruby>{ch}<rt>{r}</rt></ruby>")
                else:
                    out.append(ch)
                pos += 1
    return "".join(out)


def en_line(text, small=False):
    return f"<div class='en{' small' if small else ''}'>🇬🇧 {text}</div>" if text else ""


def clean_opt(o):
    return re.sub(r"（.*?）", "", o)


def fill(stem, answer):
    """Put the answer into the ___ blanks, marked with 【】 so it is highlighted."""
    out = stem.replace("【", "").replace("】", "")
    for part in answer.split("……"):
        out = out.replace("___", f"【{part}】", 1)
    return out


def fill_en(stem_en, ans_en):
    if not stem_en:
        return ""
    parts = [p.strip() for p in re.split(r"\s*…\s*", ans_en)] if "…" in ans_en else [ans_en]
    out = stem_en
    for p in parts:
        out = out.replace("___", f"<b>{p}</b>", 1)
    return out


def btn_label(zh, py=False, en_text=None, num=None):
    head = f"{num}　{zh}" if num else zh
    lab = f"**{head}**"
    if py:
        p = plain(zh)
        if p:
            lab += f"\n{p}"
    if en_text:
        lab += f"\n*{en_text}*"
    return lab


# --------------------------------------------------------------------------- state
def init_state():
    ss = st.session_state
    ss.setdefault("page", "home")
    ss.setdefault("name", "")
    ss.setdefault("level", "learn")
    ss.setdefault("xp", 0)
    ss.setdefault("streak", 0)
    ss.setdefault("best_streak", 0)
    ss.setdefault("answered", 0)
    ss.setdefault("correct", 0)
    ss.setdefault("by_cat", {})          # cat -> [correct, total]
    ss.setdefault("by_level", {})        # level -> [correct, total]
    ss.setdefault("pure", [0, 0])        # Exam mode with no hints: true Chinese understanding
    ss.setdefault("mistakes", {})
    ss.setdefault("badges", [])
    ss.setdefault("quiz", None)
    ss.setdefault("flash", None)
    ss.setdefault("wq", None)
    ss.setdefault("schools", list(SCHOOLS))


def level_info(xp):
    lvl = xp // 100 + 1
    titles = ["华文小芽 🌱", "华文小苗 🌿", "华文小树 🌳", "华文小勇士 🛡️", "华文小侠 🥋", "华文状元 🏆", "华文大师 🐉"]
    return lvl, titles[min(lvl - 1, len(titles) - 1)], xp % 100


BADGE_NAMES = {
    "first": "🌟 First correct", "s5": "🔥 5 in a row", "s10": "⚡ 10 in a row", "s20": "🚀 20 in a row",
    "c50": "🎖️ 50 correct", "c150": "👑 150 correct", "all": "🌈 Tried every type",
    "exam10": "🧠 10 right in Exam mode", "exam50": "🐉 50 right in Exam mode", "perfect": "💯 Perfect round",
}


def award_badges():
    ss = st.session_state
    rules = [
        ("first", ss.correct >= 1), ("s5", ss.best_streak >= 5), ("s10", ss.best_streak >= 10),
        ("s20", ss.best_streak >= 20), ("c50", ss.correct >= 50), ("c150", ss.correct >= 150),
        ("all", all(c in ss.by_cat for c in CORE_CATS)),
        ("exam10", ss.pure[0] >= 10), ("exam50", ss.pure[0] >= 50),
    ]
    for key, ok in rules:
        if ok and key not in ss.badges:
            ss.badges.append(key)
            st.toast(f"New badge 新徽章：{BADGE_NAMES[key]}", icon="🏅")


def show_py(h):
    return st.session_state.level in ("learn", "practice") or h.get("hint_py")


def show_en(h):
    return st.session_state.level == "learn" or h.get("hint_en")


def gain_for(ok, used_hint):
    ss = st.session_state
    if not ok:
        return 2
    base = 10 + min(ss.streak, 10)
    mult = 1.0 if used_hint else LEVELS[ss.level]["mult"]
    return int(round(base * mult))


def record(cat, key, item, ok, used_hint):
    ss = st.session_state
    ss.answered += 1
    c = ss.by_cat.setdefault(cat, [0, 0])
    c[1] += 1
    lv = ss.by_level.setdefault(ss.level, [0, 0])
    lv[1] += 1
    pure = ss.level == "exam" and not used_hint
    if pure:
        ss.pure[1] += 1
    if ok:
        ss.xp += gain_for(True, used_hint)
        ss.streak += 1
        ss.correct += 1
        c[0] += 1
        lv[0] += 1
        if pure:
            ss.pure[0] += 1
        ss.best_streak = max(ss.best_streak, ss.streak)
        if key:
            ss.mistakes.pop(key, None)
        if ss.streak in (5, 10, 15, 20, 30):
            st.balloons()
    else:
        ss.streak = 0
        ss.xp += 2
        if key and item:
            ss.mistakes[key] = item
    award_badges()


# --------------------------------------------------------------------------- question views
def mcq_view(q, py, en_on):
    t, sch = q["type"], q["school"]
    if t == "usage":
        word = re.search(r"（(.+?)）", q["stem"]).group(1)
        html = f"<div class='qtext'>{rich('以下哪一个句子是正确的？', py)}<br>{rich('词语：', py)}<span class='hl'>{rich(word, py)}</span></div>"
        if en_on:
            html += en_line(f"Which sentence uses <b>{word}</b> ({en(word, sch)}) correctly?")
    else:
        html = f"<div class='qtext'>{rich(q['stem'], py, hide_ul=(t == 'pinyin'))}</div>"
        if en_on:
            html += en_line(en(q["stem"], sch))
    opts = []
    for o in q["options"]:
        if t == "pinyin":
            opts.append(dict(zh=o, label=f"**{o}**", py=False, en=""))
        elif t == "hanzi":
            opts.append(dict(zh=o, label=btn_label(o, py), py=True, en=""))
        else:
            e = en(o, sch)
            opts.append(dict(zh=o, label=btn_label(o, py, e if en_on else None), py=True, en=e))

    right = q["options"][q["answer"]]
    if t == "pinyin":
        w = re.search(r"【(.+?)】", q["stem"]).group(1)
        expl = (f"<b>{w}</b> is read <b>{right}</b> — it means <i>“{en(w, sch)}”</i>.<br>"
                f"{rich(q['stem'], True)}{en_line(en(q['stem'], sch), True)}")
        speak = w
    elif t == "meaning":
        w = re.search(r"【(.+?)】", q["stem"]).group(1)
        expl = (f"「{rich(w)}」 means 「{rich(right)}」 — <i>{en(right, sch)}</i>.<br>"
                f"{rich(q['stem'], True)}{en_line(en(q['stem'], sch), True)}")
        speak = q["stem"].replace("【", "").replace("】", "")
    elif t == "usage":
        w = re.search(r"（(.+?)）", q["stem"]).group(1)
        expl = (f"The correct sentence 正确的句子：<br>{rich(right)}{en_line(en(right, sch), True)}"
                f"<div style='margin-top:6px'>Only this sentence uses <b>{w}</b> (<i>{en(w, sch)}</i>) the right way. "
                f"Compare the English of the other sentences above — they sound odd.</div>")
        speak = right
    else:
        full = fill(q["stem"], clean_opt(right))
        stem_en = en(q["stem"], sch)
        if t in ("connector", "sentence"):
            e_line = en_line(fill_en(stem_en, en(right, sch)), True)
        else:
            e_line = en_line(stem_en, True)
        expl = f"Complete sentence 完整的句子：<br>{rich(full)}{e_line}"
        if t == "word":
            expl += f"<div>「{rich(right)}」 = <i>{en(right, sch)}</i></div>"
        if t == "hanzi":
            expl = f"The correct character is 「{rich(clean_opt(right))}」.<br>" + expl
        if t == "connector":
            note = CONNECTOR_NOTES.get(right.split("……")[0])
            if note:
                expl += f"<div>📝 {rich(note[0])}<br>🇬🇧 {note[1]}</div>"
        speak = full.replace("【", "").replace("】", "")
    if q.get("note"):
        expl += f"<br><small>{q['note']} (The school's answer key says differently, but the passage needs this answer.)</small>"
    return dict(cat=t, school=sch, label=f"Q{q['n']}", html=html, options=opts, answer=q["answer"], expl=expl, speak=speak)


def cloze_view(ci, n, picks, py, en_on):
    c = CLOZE[ci]
    sch = c["school"]
    b = next(x for x in c["blanks"] if x["n"] == n)
    repl = {}
    for bb in c["blanks"]:
        k = bb["n"]
        right = bb["options"][bb["answer"]]
        if k < n:
            if k in picks and picks[k] != bb["answer"]:
                repl["{%d}" % k] = f"<span class='chip no'><s>{rich(bb['options'][picks[k]], py)}</s></span><span class='chip ok'>{rich(right, py)}</span>"
            else:
                repl["{%d}" % k] = f"<span class='chip ok'>{rich(right, py)}</span>"
        elif k == n:
            repl["{%d}" % k] = f"<span class='chip now'>Q{k} ❓</span>"
        else:
            repl["{%d}" % k] = f"<span class='chip todo'>Q{k}</span>"
    paras = []
    for p in c["passage"].split("\n"):
        h = f"<p style='text-indent:2em;margin:0 0 4px 0'>{rich(p, py, repl)}</p>"
        if en_on:
            h += f"<div class='en small' style='margin:0 0 12px 0'>🇬🇧 {en(p, sch)}</div>"
        paras.append(h)
    html = f"<div class='passage'>{''.join(paras)}</div>"
    opts = []
    for o in b["options"]:
        e = en(o, sch)
        opts.append(dict(zh=o, label=btn_label(o, py, e if en_on else None), py=True, en=e))
    right = b["options"][b["answer"]]
    sent = sentence_around(c, n)
    expl = f"Q{n} = 「{rich(right)}」 — <i>{en(right, sch)}</i><br>{rich(sent)}"
    if b.get("note"):
        expl += f"<br><small>{b['note']} (The school's answer key says differently, but the passage needs this answer.)</small>"
    return dict(cat="cloze", school=sch, label=f"Q{n}", html=html, options=opts, answer=b["answer"], expl=expl,
                speak=sent.replace("【", "").replace("】", ""))


def sentence_around(c, n):
    passage = c["passage"]
    tok = "{%d}" % n
    i = passage.index(tok)
    start = max(passage.rfind(ch, 0, i) for ch in "。！？\n") + 1
    ends = [e for e in (passage.find(ch, i) for ch in "。！？") if e != -1]
    end = (min(ends) + 1) if ends else len(passage)
    s = passage[start:end]
    for b in c["blanks"]:
        word = b["options"][b["answer"]]
        s = s.replace("{%d}" % b["n"], f"【{word}】" if b["n"] == n else word)
    return s.strip("”“ ")


WHO_COLORS = ["#FF8787", "#4DABF7", "#69DB7C", "#DA77F2"]


def dialog_view(di, n, picks, py, en_on):
    d = DIALOGUES[di]
    sch = d["school"]
    whos = []
    for l in d["lines"]:
        if l["who"] not in whos:
            whos.append(l["who"])
    bank = []
    for i, o in enumerate(d["options"]):
        row = f"<b>{i+1}</b>　{rich(o, py)}"
        if en_on:
            row += f" <span class='en small' style='display:inline'>— {en(o, sch)}</span>"
        bank.append(row)
    repl = {}
    for k, a in d["answers"].items():
        k = int(k)
        if k < n:
            if k in picks and picks[k] != a:
                chip = f"<span class='chip no'><s>{rich(d['options'][picks[k]], py)}</s></span><span class='chip ok'>{rich(d['options'][a], py)}</span>"
            else:
                chip = f"<span class='chip ok'>{rich(d['options'][a], py)}</span>"
        elif k == n:
            chip = f"<span class='chip now'>Q{k} ❓</span>"
        else:
            chip = f"<span class='chip todo'>Q{k}</span>"
        repl["{%d}" % k] = chip
    rows = []
    for l in d["lines"]:
        col = WHO_COLORS[whos.index(l["who"]) % len(WHO_COLORS)]
        say = rich(l["text"], py, repl)
        if en_on:
            say += en_line(en(l["text"], sch), True)
        rows.append(f"<div class='chat'><div class='who' style='background:{col}'>{rich(l['who'], py)}</div><div class='say'>{say}</div></div>")
    html = f"<div class='bank'>{'<br>'.join(bank)}</div><div style='margin-top:10px'>{''.join(rows)}</div>"
    opts = []
    for i, o in enumerate(d["options"]):
        e = en(o, sch)
        opts.append(dict(zh=o, label=btn_label(o, py, e if en_on else None, num=i + 1), py=True, en=e, num=i + 1))
    a = d["answers"][str(n)]
    line = next(l for l in d["lines"] if "{%d}" % n in l["text"])
    full = line["text"].replace("{%d}" % n, f"【{d['options'][a]}】")
    for k, aa in d["answers"].items():
        full = full.replace("{%s}" % k, d["options"][aa])
    line_en = en(line["text"], sch).replace("___", f"<b>{en(d['options'][a], sch)}</b>", 1)
    expl = f"Q{n} = <b>{a+1}</b> 「{rich(d['options'][a])}」<br>{rich(line['who'])}：{rich(full)}{en_line(line_en, True)}"
    return dict(cat="dialog", school=sch, label=f"Q{n}", html=html, options=opts, answer=a, expl=expl,
                speak=full.replace("【", "").replace("】", ""))


def view_for(item, picks, py, en_on):
    if item["kind"] == "mcq":
        return mcq_view(MCQ[item["id"]], py, en_on)
    if item["kind"] == "cloze":
        return cloze_view(item["ci"], item["n"], picks, py, en_on)
    return dialog_view(item["di"], item["n"], picks, py, en_on)


def item_key(item):
    if item["kind"] == "mcq":
        return item["id"]
    if item["kind"] == "cloze":
        return f"cloze-{item['ci']}-{item['n']}"
    return f"dialog-{item['di']}-{item['n']}"


def speak_button(text):
    safe = json.dumps(text)
    html = f"""
<button id="b" style="font-size:16px;border-radius:14px;border:2px solid #74C0FC;background:#E7F5FF;padding:6px 14px;cursor:pointer">
🔊 听一听 Listen</button>
<script>
document.getElementById('b').onclick = function() {{
  const u = new SpeechSynthesisUtterance({safe}); u.lang = 'zh-CN'; u.rate = 0.8;
  const v = speechSynthesis.getVoices().find(v => v.lang && v.lang.startsWith('zh'));
  if (v) u.voice = v; speechSynthesis.cancel(); speechSynthesis.speak(u);
}};
</script>"""
    if hasattr(st, "iframe"):
        st.iframe(html, height=46)
    else:
        components.html(html, height=46)


def level_switch(where):
    ss = st.session_state
    keys = list(LEVELS)
    choice = st.radio("Help level 帮助", keys, index=keys.index(ss.level), horizontal=True, key=f"lvl_{where}",
                      format_func=lambda k: f"{LEVELS[k]['icon']} {LEVELS[k]['zh']} {LEVELS[k]['en']}")
    if choice != ss.level:
        ss.level = choice
        st.rerun()


def hint_buttons(h):
    """Show 'tap for pinyin / English' buttons when the current level hides them."""
    ss = st.session_state
    need_py = not show_py(h)
    need_en = not show_en(h)
    if not (need_py or need_en):
        return
    cols = st.columns(3)
    if need_py and cols[0].button("👀 Show pinyin", key="hint_py"):
        h["hint_py"] = True
        h["used_hint"] = True
        st.rerun()
    if need_en and cols[1].button("🇬🇧 Show English", key="hint_en"):
        h["hint_en"] = True
        h["used_hint"] = True
        st.rerun()
    if ss.level == "exam":
        cols[2].caption("Hints remove the Exam ×2 bonus")
    else:
        cols[2].caption("English costs the ×1.5 bonus")


# --------------------------------------------------------------------------- quiz engine
def start_quiz(items, title, shuffle_opts=True):
    order = {}
    for it in items:
        if it["kind"] == "mcq" and shuffle_opts:
            perm = list(range(4))
            random.shuffle(perm)
            order[item_key(it)] = perm
    st.session_state.quiz = dict(items=items, i=0, title=title, picked=None, score=0, order=order,
                                 cloze_picks={}, dialog_picks={}, results=[], pure=[0, 0], h={})
    st.session_state.page = "quiz"


def page_quiz():
    ss = st.session_state
    qz = ss.quiz
    if not qz:
        ss.page = "home"
        st.rerun()
    items = qz["items"]
    if qz["i"] >= len(items):
        return quiz_summary()
    item = items[qz["i"]]
    h = qz["h"]
    answered = qz["picked"] is not None
    py = show_py(h) or answered
    en_on = show_en(h) or answered
    picks_all = qz["cloze_picks"] if item["kind"] == "cloze" else qz["dialog_picks"]
    pick_map = picks_all.get(item.get("ci", item.get("di")), {})
    v = view_for(item, pick_map, py, en_on)
    meta = CATS[v["cat"]]

    top = st.columns([3, 1])
    top[0].markdown(f"### {qz['title']}")
    if top[1].button("🏠 Home", key="back"):
        ss.page = "home"
        st.rerun()
    if not answered:
        level_switch("quiz")
    st.progress(qz["i"] / len(items),
                text=f"Question {qz['i']+1} / {len(items)}　·　Score {qz['score']}　·　🔥 Streak {ss.streak}")

    sch = SCHOOLS[v["school"]]
    tip = rich(meta["tip"], py) + (en_line(meta["tip_en"], True) if en_on else "")
    st.markdown(
        f"<div class='qcard' style='--c:{meta['color']}'><span class='qtag'>{meta['icon']} {meta['zh']} · {meta['en']}</span>"
        f"<span style='float:right;color:#999;font-size:.85rem'>{sch['en']} · {v['label']}</span>"
        f"<div style='color:#666;margin-bottom:6px;line-height:2.2rem'>{tip}</div>{v['html']}</div>",
        unsafe_allow_html=True)

    opts = v["options"]
    perm = qz["order"].get(item_key(item), list(range(len(opts))))

    if not answered:
        hint_buttons(h)
        cols = st.columns(2)
        for pos, oi in enumerate(perm):
            with cols[pos % 2]:
                if st.button(opts[oi]["label"], key=f"c{pos}_q", use_container_width=True):
                    ok = oi == v["answer"]
                    used = bool(h.get("used_hint"))
                    qz["picked"] = oi
                    qz["gain"] = gain_for(ok, used)
                    if ok:
                        qz["score"] += 1
                    qz["results"].append(ok)
                    if ss.level == "exam" and not used:
                        qz["pure"][1] += 1
                        qz["pure"][0] += ok
                    if item["kind"] in ("cloze", "dialog"):
                        picks_all.setdefault(item.get("ci", item.get("di")), {})[item["n"]] = oi
                    record(v["cat"], item_key(item), item, ok, used)
                    st.rerun()
    else:
        picked = qz["picked"]
        ok = picked == v["answer"]
        for oi in perm:
            o = opts[oi]
            num = f"{o['num']}　" if o.get("num") else ""
            zh_html = rich(o["zh"]) if o["py"] else f"<b>{o['zh']}</b>"
            body = f"{num}{zh_html}" + (f" <span class='en small' style='display:inline'>— {o['en']}</span>" if o["en"] else "")
            if oi == v["answer"]:
                st.markdown(f"<div class='res right'>✅ {body}</div>", unsafe_allow_html=True)
            elif oi == picked:
                st.markdown(f"<div class='res wrong'>❌ {body}</div>", unsafe_allow_html=True)
            elif not o.get("num"):
                st.markdown(f"<div class='res dim'>{body}</div>", unsafe_allow_html=True)
        if ok:
            zh, e = random.choice(CHEERS)
            st.markdown(f"<div class='feedback good'>🐼 <b>{rich(zh)}</b> {e} +{qz.get('gain', 10)} XP<br>{v['expl']}</div>",
                        unsafe_allow_html=True)
        else:
            zh, e = random.choice(COMFORT)
            st.markdown(f"<div class='feedback bad'>🐼 <b>{rich(zh)}</b> {e} Saved to your Mistake Book 📕<br>{v['expl']}</div>",
                        unsafe_allow_html=True)
        speak_button(v["speak"])
        if st.button("Next 下一题 ➜" if qz["i"] + 1 < len(items) else "See my score 看成绩 🏁", key="next",
                     use_container_width=True):
            qz["i"] += 1
            qz["picked"] = None
            qz["h"] = {}
            st.rerun()


def quiz_summary():
    ss = st.session_state
    qz = ss.quiz
    n = len(qz["items"])
    pct = qz["score"] / n if n else 0
    stars = 3 if pct >= .9 else 2 if pct >= .7 else 1 if pct >= .5 else 0
    msgs = [("再练练，你一定可以的！", "Practise a bit more — you can do it!"), ("不错哦，继续加油！", "Good job, keep going!"),
            ("很棒！差一点就满分了！", "Great! Almost full marks!"), ("太厉害了！华文小高手！", "Amazing! Chinese champion!")]
    pure = qz["pure"]
    pure_line = ""
    if pure[1]:
        pure_line = (f"<div style='margin-top:8px'>🧠 Chinese-only (Exam mode, no hints): <b>{pure[0]} / {pure[1]}</b></div>")
    elif ss.level != "exam":
        pure_line = ("<div style='margin-top:8px;color:#666'>Ready for a real test? Switch to 🔴 Exam mode "
                     "to check how much Chinese you understand without help.</div>")
    st.markdown(f"<div class='hero'><h1>{'⭐' * stars or '💪'}</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='qcard' style='--c:#FCC419;text-align:center'><div class='fun' style='font-size:2rem'>"
                f"{qz['title']} Done! 完成！</div><div style='font-size:1.4rem'>{qz['score']} / {n} correct ({pct:.0%})</div>"
                f"<div style='margin-top:8px;line-height:2.4rem'>{rich(msgs[stars][0])}<br>{msgs[stars][1]}</div>{pure_line}</div>",
                unsafe_allow_html=True)
    if pct == 1 and n >= 5:
        st.balloons()
        if "perfect" not in ss.badges:
            ss.badges.append("perfect")
            st.toast(f"New badge 新徽章：{BADGE_NAMES['perfect']}", icon="🏅")
    c1, c2 = st.columns(2)
    if c1.button("🔁 Try again 再来一次", key="start", use_container_width=True):
        items = qz["items"][:]
        if all(i["kind"] == "mcq" for i in items):
            random.shuffle(items)
        start_quiz(items, qz["title"])
        st.rerun()
    if c2.button("🏠 Home 主页", use_container_width=True):
        ss.page = "home"
        ss.quiz = None
        st.rerun()


# --------------------------------------------------------------------------- pool builders
def school_ok(sid):
    return sid in st.session_state.schools


def mcq_items(cat, k=None):
    pool = [{"kind": "mcq", "id": q["id"]} for q in DATA["mcq"] if q["type"] == cat and school_ok(q["school"])]
    random.shuffle(pool)
    return pool[:k] if k else pool


def cloze_items(ci):
    return [{"kind": "cloze", "ci": ci, "n": b["n"]} for b in CLOZE[ci]["blanks"]]


def dialog_items(di):
    return [{"kind": "dialog", "di": di, "n": int(n)} for n in sorted(DIALOGUES[di]["answers"])]


# --------------------------------------------------------------------------- pages
def sidebar():
    ss = st.session_state
    with st.sidebar:
        st.markdown("<div class='fun' style='font-size:1.6rem;text-align:center'>🐼 My progress</div>", unsafe_allow_html=True)
        ss.name = st.text_input("Your name 你的名字", value=ss.name, placeholder="Type your name")
        lv = LEVELS[ss.level]
        st.markdown(f"<div class='lvl'><b>{lv['icon']} {lv['zh']} {lv['en']}</b><br>{lv['desc']} · XP ×{lv['mult']:g}</div>",
                    unsafe_allow_html=True)
        lvl, title, into = level_info(ss.xp)
        st.markdown(f"<div style='text-align:center;font-size:1.1rem'>Lv.{lvl} <b>{title}</b></div>", unsafe_allow_html=True)
        st.progress(into / 100, text=f"{ss.xp} XP · {100-into} XP to next level")
        c = st.columns(3)
        acc = f"{ss.correct/ss.answered:.0%}" if ss.answered else "–"
        for col, (lab, val) in zip(c, [("Done", ss.answered), ("Correct", acc), ("Streak", ss.best_streak)]):
            col.markdown(f"<div class='stat'><b>{val}</b>{lab}</div>", unsafe_allow_html=True)
        p = ss.pure
        pure_txt = f"{p[0]} / {p[1]} ({p[0]/p[1]:.0%})" if p[1] else "not tried yet"
        st.markdown(f"<div class='lvl' style='margin-top:10px'>🧠 <b>Chinese-only score</b><br>"
                    f"<span style='font-size:.85rem;color:#666'>Exam mode, no hints</span><br><b>{pure_txt}</b></div>",
                    unsafe_allow_html=True)
        if ss.by_level:
            rows = " · ".join(f"{LEVELS[k]['icon']} {v[0]}/{v[1]}" for k, v in ss.by_level.items() if k in LEVELS)
            st.caption(f"By help level: {rows}")
        if ss.badges:
            st.markdown("**🏅 Badges**<br>" + "".join(f"<span class='badge'>{BADGE_NAMES.get(b, b)}</span>" for b in ss.badges),
                        unsafe_allow_html=True)
        st.divider()
        with st.expander("🏫 Choose school papers"):
            ss.schools = st.multiselect("Only practise these schools", list(SCHOOLS), default=ss.schools,
                                        format_func=lambda s: f"{SCHOOLS[s]['en']} {SCHOOLS[s]['zh']}") or list(SCHOOLS)
        with st.expander("💾 Save / load progress"):
            keep = {k: ss[k] for k in ("name", "level", "xp", "streak", "best_streak", "answered", "correct",
                                       "by_cat", "by_level", "pure", "mistakes", "badges")}
            st.download_button("Download my progress", json.dumps(keep, ensure_ascii=False),
                               file_name=f"p6-chinese-progress-{dt.date.today()}.json", use_container_width=True)
            up = st.file_uploader("Upload a progress file", type="json")
            if up is not None and st.button("Load progress", use_container_width=True):
                try:
                    for k, v in json.loads(up.read().decode("utf-8")).items():
                        ss[k] = v
                    st.success("Progress loaded!")
                    st.rerun()
                except Exception:
                    st.error("That file didn't work — please try again.")
        st.caption("Questions from the 2026 P6 Chinese Prelim papers (Paper 2) of 10 schools.")


def tile(col, key, icon, zh, en_text, sub, color):
    with col:
        st.markdown(
            f"<div class='tile' style='--c:{color}'><div class='ti'>{icon}</div><div class='tz'>{rich(zh)}</div>"
            f"<div class='te'>{en_text}</div><div class='ts'>{sub}</div></div>", unsafe_allow_html=True)
        return st.button("Start 开始 ▶", key=key, use_container_width=True)


def page_home():
    ss = st.session_state
    hello = f"{ss.name}, " if ss.name else ""
    st.markdown("<div class='hero'><h1>小六华文冲冲冲！</h1><p>P6 Chinese practice · 2026 Prelim papers</p></div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='bubble'>🐼 {rich('你好！我是熊猫老师。')}<br>Hi {hello}I'm Teacher Panda! "
                "Every Chinese word has <b>pinyin</b> on top and an <b>English</b> meaning to help you. "
                "When you feel ready, switch to <b>🔴 Exam</b> mode to test yourself with Chinese only — "
                "you earn <b>double XP</b> there!</div>", unsafe_allow_html=True)
    level_switch("home")

    c1, c2 = st.columns(2)
    if c1.button("🚀 Mixed challenge (10 questions)", key="start", use_container_width=True):
        pool = [{"kind": "mcq", "id": q["id"]} for q in DATA["mcq"] if school_ok(q["school"])]
        start_quiz(random.sample(pool, min(10, len(pool))), "🚀 Mixed challenge 综合挑战")
        st.rerun()
    n_mis = len(ss.mistakes)
    if c2.button(f"📕 Mistake book 错题本 ({n_mis})", use_container_width=True, disabled=n_mis == 0):
        start_quiz(list(ss.mistakes.values()), "📕 Mistake book 错题本")
        st.rerun()

    st.markdown("### 🎯 语文应用 · Language use")
    cats = ["pinyin", "hanzi", "word", "meaning", "connector", "sentence", "usage"]
    cols = st.columns(2)
    for i, cat in enumerate(cats):
        m = CATS[cat]
        n = len(mcq_items(cat))
        done = ss.by_cat.get(cat, [0, 0])
        stat = f"✅ {done[0]}/{done[1]} correct" if done[1] else f"{n} questions"
        if tile(cols[i % 2], f"go_{cat}", m["icon"], m["zh"], m["en"], stat, m["color"]):
            start_quiz(mcq_items(cat, 10), f"{m['icon']} {m['zh']} {m['en']}")
            st.rerun()

    st.markdown("### 📖 读一读，填一填 · Read and fill in")
    c1, c2 = st.columns(2)
    if tile(c1, "go_cloze", "📖", "短文填空", "Passage fill-in", "10 passages · 50 blanks", CATS["cloze"]["color"]):
        ss.page = "pick_cloze"
        st.rerun()
    if tile(c2, "go_dialog", "💬", "完成对话", "Complete the dialogue", "10 dialogues · 40 blanks", CATS["dialog"]["color"]):
        ss.page = "pick_dialog"
        st.rerun()

    st.markdown("### 🃏 词语加油站 · Word power")
    c1, c2, c3 = st.columns(3)
    if tile(c1, "go_flash", "🃏", "词语卡", "Flashcards", "pinyin · meaning · example", "#9775FA"):
        start_flash()
        st.rerun()
    if tile(c2, "go_words", "🌏", "词语大考验", "Word quiz: Chinese ↔ English", f"{len(word_pool())} words", "#20C997"):
        ss.page = "words"
        ss.wq = None
        st.rerun()
    if tile(c3, "go_paper", "🏫", "整份试卷", "Full paper", "one whole school paper", "#FF922B"):
        ss.page = "pick_paper"
        st.rerun()


def page_pick(kind):
    ss = st.session_state
    title = {"cloze": "📖 Pick a passage 选一篇短文", "dialog": "💬 Pick a dialogue 选一段对话",
             "paper": "🏫 Pick a school paper 选一份试卷"}[kind]
    st.markdown(f"## {title}")
    if st.button("🏠 Home", key="back"):
        ss.page = "home"
        st.rerun()
    src = CLOZE if kind == "cloze" else DIALOGUES if kind == "dialog" else [{"school": s} for s in SCHOOLS]
    cols = st.columns(2)
    for i, x in enumerate(src):
        s = SCHOOLS[x["school"]]
        if kind == "cloze":
            first = x["passage"].split("\n")[0]
            preview = en(first, x["school"])[:70] + "…"
        elif kind == "dialog":
            preview = en(x["lines"][0]["text"], x["school"])[:70] + "…"
        else:
            preview = "15 language questions + passage + dialogue"
        with cols[i % 2]:
            if st.button(f"**🏫 {s['en']} {s['zh']}**\n*{preview}*", key=f"c{i % 9}_p{i}", use_container_width=True):
                if kind == "cloze":
                    start_quiz(cloze_items(i), f"📖 Passage 短文填空 · {s['en']}")
                elif kind == "dialog":
                    start_quiz(dialog_items(i), f"💬 Dialogue 完成对话 · {s['en']}")
                else:
                    sid = x["school"]
                    items = [{"kind": "mcq", "id": f"{sid}-Q{n}"} for n in range(1, 16)]
                    ci = next(j for j, c in enumerate(CLOZE) if c["school"] == sid)
                    di = next(j for j, d in enumerate(DIALOGUES) if d["school"] == sid)
                    start_quiz(items + cloze_items(ci) + dialog_items(di), f"🏫 {s['en']} full paper", shuffle_opts=False)
                st.rerun()


# ---- flashcards
def flash_deck():
    seen, deck = {}, []
    for v in VOCAB:
        if not school_ok(v["school"]):
            continue
        w = v["word"]
        if w in seen:
            for k in ("meaning", "pinyin", "example"):
                if k in v and k not in seen[w]:
                    seen[w][k] = v[k]
            continue
        card = dict(v)
        seen[w] = card
        deck.append(card)
    random.shuffle(deck)
    return deck


def start_flash():
    st.session_state.flash = dict(deck=flash_deck(), i=0, flipped=False, known=0)
    st.session_state.page = "flash"


def page_flash():
    ss = st.session_state
    f = ss.flash
    top = st.columns([3, 1])
    top[0].markdown("## 🃏 Flashcards 词语卡")
    if top[1].button("🏠 Home", key="back"):
        ss.page = "home"
        st.rerun()
    deck = f["deck"]
    if f["i"] >= len(deck):
        st.markdown(f"<div class='bubble'>🐼 All done! You knew <b>{f['known']}</b> of {len(deck)} words.</div>", unsafe_allow_html=True)
        if st.button("🔁 Go again", key="start", use_container_width=True):
            start_flash()
            st.rerun()
        return
    card = deck[f["i"]]
    w, sch = card["word"], card["school"]
    st.progress(f["i"] / len(deck), text=f"Card {f['i']+1} / {len(deck)} · Known {f['known']}")
    front_py = ss.level == "learn"
    if f["flipped"]:
        back = f"<div class='m'>🔤 <b>{plain(w)}</b></div>"
        back += f"<div class='m'>🇬🇧 <b>{en(w, sch)}</b></div>"
        if card.get("meaning"):
            back += f"<div class='m'>💡 {rich(card['meaning'])}</div>"
        if card.get("example"):
            ex = card["example"].replace(w, f"【{w}】", 1)
            back += f"<div class='m' style='font-size:1.05rem;color:#555'>📝 {rich(ex)}{en_line(en(card['example']), True)}</div>"
        word_html = rich(w)
    else:
        back = ("<div class='m' style='color:#888'>Think first: how do you say it? What does it mean? Then flip the card 👇</div>")
        word_html = rich(w, front_py)
    st.markdown(f"<div class='flash'><div class='w'>{word_html}</div>{back}</div>", unsafe_allow_html=True)
    speak_button(w)
    if not f["flipped"]:
        if st.button("🔄 Flip the card 翻开", key="next", use_container_width=True):
            f["flipped"] = True
            st.rerun()
    else:
        c1, c2 = st.columns(2)
        if c1.button("😊 I knew it! 我会了", key="c1_known", use_container_width=True):
            f["known"] += 1
            ss.xp += 3
            f["i"] += 1
            f["flipped"] = False
            st.rerun()
        if c2.button("🤔 Practise again 再练练", key="c0_again", use_container_width=True):
            deck.append(card)
            f["i"] += 1
            f["flipped"] = False
            st.rerun()


# ---- word quiz (Chinese <-> English), built from every word in the papers that has an English meaning
def word_pool():
    words = {}
    for q in DATA["mcq"]:
        if not school_ok(q["school"]):
            continue
        cands = []
        if q["type"] in ("word",):
            cands += q["options"]
        m = re.search(r"【(.+?)】", q["stem"])
        if m:
            cands.append(m.group(1))
        if q["type"] == "usage":
            cands.append(re.search(r"（(.+?)）", q["stem"]).group(1))
        for c in cands:
            e = en(c, q["school"])
            if e and 2 <= len(c) <= 4 and all(HAN.match(ch) for ch in c):
                words.setdefault(c, (e, q["school"]))
    for c in CLOZE:
        if not school_ok(c["school"]):
            continue
        for b in c["blanks"]:
            for o in b["options"]:
                e = en(o, c["school"])
                if e and 2 <= len(o) <= 4 and all(HAN.match(ch) for ch in o):
                    words.setdefault(o, (e, c["school"]))
    for v in VOCAB:
        if v["src"] == "def" and school_ok(v["school"]):
            e = en(v["word"], v["school"])
            if e:
                words.setdefault(v["word"], (e, v["school"]))
    return words


def new_word_round(direction):
    pool = word_pool()
    ws = list(pool)
    qs = []
    for w in random.sample(ws, min(10, len(ws))):
        e = pool[w][0]
        others = [x for x in ws if x != w and pool[x][0] != e]
        choices = random.sample(others, 3) + [w]
        random.shuffle(choices)
        qs.append(dict(word=w, choices=choices))
    return dict(dir=direction, qs=qs, i=0, picked=None, score=0, h={}, pure=[0, 0])


def page_words():
    ss = st.session_state
    top = st.columns([3, 1])
    top[0].markdown("## 🌏 Word quiz 词语大考验")
    if top[1].button("🏠 Home", key="back"):
        ss.page = "home"
        st.rerun()
    pool = word_pool()
    if ss.wq is None:
        st.markdown("<div class='bubble'>🐼 Choose a game:<br>"
                    "<b>🇨🇳 → 🇬🇧</b> See a Chinese word, pick its English meaning.<br>"
                    "<b>🇬🇧 → 🇨🇳</b> See the English, pick the Chinese word.</div>", unsafe_allow_html=True)
        level_switch("words")
        c1, c2 = st.columns(2)
        if c1.button("🇨🇳 → 🇬🇧\nChinese to English", key="c2_zh2en", use_container_width=True):
            ss.wq = new_word_round("zh2en")
            st.rerun()
        if c2.button("🇬🇧 → 🇨🇳\nEnglish to Chinese", key="c5_en2zh", use_container_width=True):
            ss.wq = new_word_round("en2zh")
            st.rerun()
        return
    m = ss.wq
    if m["i"] >= len(m["qs"]):
        extra = f"<div>🧠 Chinese-only: {m['pure'][0]} / {m['pure'][1]}</div>" if m["pure"][1] else ""
        st.markdown(f"<div class='qcard' style='--c:#20C997;text-align:center'><div class='fun' style='font-size:2rem'>Round done! 完成！</div>"
                    f"<div style='font-size:1.4rem'>{m['score']} / {len(m['qs'])} correct</div>{extra}</div>", unsafe_allow_html=True)
        if m["score"] == len(m["qs"]):
            st.balloons()
        c1, c2 = st.columns(2)
        if c1.button("🔁 Play again", key="start", use_container_width=True):
            ss.wq = new_word_round(m["dir"])
            st.rerun()
        if c2.button("↔️ Switch game", use_container_width=True):
            ss.wq = None
            st.rerun()
        return
    q = m["qs"][m["i"]]
    h = m["h"]
    w = q["word"]
    answered = m["picked"] is not None
    py = show_py(h) or answered
    st.progress(m["i"] / len(m["qs"]), text=f"Question {m['i']+1} / {len(m['qs'])} · Score {m['score']} · 🔥 {ss.streak}")
    if m["dir"] == "zh2en":
        prompt = (f"<span class='qtag'>🇨🇳 → 🇬🇧 What does this word mean?</span>"
                  f"<div class='qtext' style='font-size:2.6rem;line-height:4rem;text-align:center'>{rich(w, py)}</div>")
    else:
        prompt = (f"<span class='qtag'>🇬🇧 → 🇨🇳 Which Chinese word means…</span>"
                  f"<div class='qtext' style='text-align:center'>“{pool[w][0]}”</div>")
    st.markdown(f"<div class='qcard' style='--c:#20C997'>{prompt}</div>", unsafe_allow_html=True)
    if not answered:
        if m["dir"] == "zh2en" and not show_py(h):
            if st.button("👀 Show pinyin", key="hint_py"):
                h["hint_py"] = True
                h["used_hint"] = True
                st.rerun()
        if m["dir"] == "en2zh" and not show_py(h):
            if st.button("👀 Show pinyin on the choices", key="hint_py"):
                h["hint_py"] = True
                h["used_hint"] = True
                st.rerun()
        cols = st.columns(2)
        for i, c in enumerate(q["choices"]):
            label = f"**{pool[c][0]}**" if m["dir"] == "zh2en" else btn_label(c, py)
            with cols[i % 2]:
                if st.button(label, key=f"c{i}_w", use_container_width=True):
                    ok = c == w
                    used = bool(h.get("used_hint"))
                    m["picked"] = c
                    m["gain"] = gain_for(ok, used)
                    m["score"] += ok
                    if ss.level == "exam" and not used:
                        m["pure"][1] += 1
                        m["pure"][0] += ok
                    record("vocab", None, None, ok, used)
                    st.rerun()
    else:
        for c in q["choices"]:
            cls = "right" if c == w else "wrong" if c == m["picked"] else "dim"
            mark = "✅ " if c == w else "❌ " if c == m["picked"] else ""
            st.markdown(f"<div class='res {cls}'>{mark}{rich(c)} <span class='en small' style='display:inline'>— {pool[c][0]}</span></div>",
                        unsafe_allow_html=True)
        good = m["picked"] == w
        zh, e = random.choice(CHEERS if good else COMFORT)
        gain = f" +{m.get('gain', 10)} XP" if good else ""
        st.markdown(f"<div class='feedback {'good' if good else 'bad'}'>🐼 <b>{rich(zh)}</b> {e}{gain}<br>"
                    f"「{rich(w)}」 = <i>{pool[w][0]}</i></div>", unsafe_allow_html=True)
        speak_button(w)
        if st.button("Next 下一题 ➜", key="next", use_container_width=True):
            m["i"] += 1
            m["picked"] = None
            m["h"] = {}
            st.rerun()


# --------------------------------------------------------------------------- main
css()
init_state()
sidebar()
page = st.session_state.page
if page == "home":
    page_home()
elif page == "quiz":
    page_quiz()
elif page == "pick_cloze":
    page_pick("cloze")
elif page == "pick_dialog":
    page_pick("dialog")
elif page == "pick_paper":
    page_pick("paper")
elif page == "flash":
    page_flash()
elif page == "words":
    page_words()
else:
    st.session_state.page = "home"
    st.rerun()
