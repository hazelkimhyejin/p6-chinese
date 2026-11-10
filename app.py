"""
小六华文冲冲冲！ — P6 Chinese practice app
Questions come from 10 school 2026 P6 Chinese Preliminary Examination papers (Paper 2).
Run locally:  streamlit run app.py
"""
import json
import random
import re
import datetime as dt
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="小六华文冲冲冲！", page_icon="🐼", layout="centered",
                   initial_sidebar_state="auto")

DATA = json.loads((Path(__file__).parent / "data" / "questions.json").read_text(encoding="utf-8"))
SCHOOLS = {s["id"]: s for s in DATA["schools"]}
MCQ = {q["id"]: q for q in DATA["mcq"]}
CLOZE = DATA["cloze"]
DIALOGUES = DATA["dialogues"]
VOCAB = DATA["vocab"]

# --------------------------------------------------------------------------- look & feel
CATS = {
    "pinyin":    dict(icon="🔤", zh="拼音小达人", en="Hanyu Pinyin", color="#FF6B6B", tip="选出画线词语的汉语拼音"),
    "hanzi":     dict(icon="✍️", zh="汉字侦探",   en="Correct character", color="#FFA94D", tip="选出正确的字"),
    "word":      dict(icon="📚", zh="词语百宝箱", en="Choose the word", color="#FFD43B", tip="选出最适当的词语"),
    "meaning":   dict(icon="💡", zh="词义解码",   en="Word meanings", color="#69DB7C", tip="画线词语是什么意思？"),
    "connector": dict(icon="🔗", zh="关联词魔法", en="Connectors (grammar)", color="#38D9A9", tip="选出正确的关联词"),
    "sentence":  dict(icon="🧩", zh="句子拼图",   en="Complete the sentence", color="#4DABF7", tip="选出最适当的句子"),
    "usage":     dict(icon="⚖️", zh="用词小法官", en="Correct usage", color="#748FFC", tip="哪一个句子是正确的？"),
    "cloze":     dict(icon="📖", zh="短文填空",   en="Passage fill-in-the-blanks", color="#DA77F2", tip="根据上下文选出适当的词语"),
    "dialog":    dict(icon="💬", zh="完成对话",   en="Complete the dialogue", color="#F783AC", tip="从表中选出适当的短语或短句"),
}
CHEERS = ["太棒了！", "真厉害！", "答对啦！", "好聪明！", "继续加油！", "你是华文小高手！", "完全正确！", "漂亮！"]
COMFORT = ["没关系，再接再厉！", "别灰心，下一题一定行！", "错了也是学习哦！", "记住它，下次就会了！"]

# Grammar notes for connectors — shown as feedback
CONNECTOR_NOTES = {
    "只要": "只要……就……：条件关系（有了这个条件，就会有这个结果）",
    "只有": "只有……才……：条件关系（唯一的条件，缺了不行）",
    "虽然": "虽然……但是……：转折关系（前后意思相反）",
    "尽管": "尽管……还是……：转折关系（不管前面的情况怎样，结果不变）",
    "就算": "就算……也……：假设让步（即使有这种情况，结果也不变）",
    "即使": "即使……也……：假设让步（即使有这种情况，结果也不变）",
    "如果": "如果……就……：假设关系（假设出现某情况，会有某结果）",
    "要是": "要是……就……：假设关系（＝如果……就……）",
    "不管": "不管……都/还是/仍然……：条件关系（在任何情况下结果都一样）",
    "无论": "无论……都……：条件关系（在任何情况下结果都一样）",
    "不仅": "不仅……而且/也……：递进关系（后面比前面更进一层）",
    "不但": "不但……而且……：递进关系；不但不……反而……：表示结果与预期相反",
    "除了": "除了……还/也……：补充关系（在……之外，还有……）",
    "因为": "因为……所以……：因果关系",
    "由于": "由于……因此/所以……：因果关系",
    "不是": "不是……而是……：否定前面，肯定后面；不是……就是……：两者必有其一",
    "一边": "一边……一边……：并列关系（同时做两件事）",
    "首先": "首先……然后……：顺承关系（先后顺序）",
    "反正": "反正……不如……：既然情况已经这样，就选择后者",
    "除非": "除非……不然……：唯一条件（只有这样做，否则……）",
    "凡是": "凡是……都/就……：所有符合条件的都……",
    "与其": "与其……不如……：选择关系（比较后选择后者）",
    "简直": "简直：强调“完全、差不多就是”，带夸张语气",
    "明明": "明明：表示事实很清楚（后面常有转折）",
    "竟然": "竟然：表示出乎意料",
    "大约": "大约：表示估计的数量或时间",
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
.hero { text-align:center; padding: 6px 0 2px 0; }
.hero h1 { font-size: 2.6rem; margin: 0; background: linear-gradient(90deg,#FF6B6B,#FFA94D,#FCC419,#51CF66,#339AF0,#CC5DE8);
  -webkit-background-clip:text; background-clip:text; color: transparent; }
.hero p { color:#555; margin:0; }
.bubble { background:#fff; border:3px solid #FFD43B; border-radius:22px; padding:12px 18px; margin:8px 0 14px 0;
  box-shadow: 0 4px 0 #FCC419; font-size:1.05rem; }
.qcard { background:#fff; border-radius:22px; padding:20px 22px; margin:6px 0 14px 0;
  box-shadow: 0 6px 0 rgba(0,0,0,.08), 0 10px 24px rgba(0,0,0,.06); border-top: 10px solid var(--c); }
.qtag { display:inline-block; background: var(--c); color:#fff; border-radius:999px; padding:2px 12px; font-size:.85rem; margin-bottom:8px; }
.qtext { font-size:1.45rem; line-height:2.2rem; color:#222; }
.qtext u, .hl { text-decoration: none; border-bottom: 4px solid #FF6B6B; padding: 0 2px; font-weight:700; }
.blank { display:inline-block; min-width:70px; border-bottom:3px dashed #868E96; text-align:center; color:#868E96; }
.passage { font-size:1.2rem; line-height:2.3rem; background:#fff; border-radius:18px; padding:16px 20px;
  box-shadow: inset 0 0 0 3px #F3D9FA; white-space: pre-wrap; }
.chip { display:inline-block; border-radius:10px; padding:0 8px; margin:0 2px; font-weight:700; }
.chip.ok { background:#D3F9D8; color:#2B8A3E; } .chip.no { background:#FFE3E3; color:#C92A2A; }
.chip.now { background:#FFF3BF; color:#E67700; border:2px solid #FCC419; animation: pulse 1.2s infinite; }
.chip.todo { background:#F1F3F5; color:#868E96; }
@keyframes pulse { 0%{transform:scale(1)} 50%{transform:scale(1.08)} 100%{transform:scale(1)} }
.chat { display:flex; gap:10px; margin:8px 0; align-items:flex-start; }
.chat .who { min-width:62px; font-weight:700; color:#fff; border-radius:12px; padding:4px 8px; text-align:center; font-size:.95rem; }
.chat .say { background:#fff; border-radius:16px; padding:8px 14px; font-size:1.12rem; line-height:2rem; box-shadow:0 2px 0 rgba(0,0,0,.07); }
.bank { background:#FFF9DB; border:2px dashed #FCC419; border-radius:16px; padding:10px 16px; font-size:1.02rem; line-height:1.9rem; }
.res { border-radius:16px; padding:12px 16px; margin:6px 0; font-size:1.15rem; border:3px solid transparent; background:#fff; }
.res.right { border-color:#40C057; background:#EBFBEE; } .res.wrong { border-color:#FA5252; background:#FFF5F5; }
.res.dim { opacity:.55; }
.feedback { border-radius:18px; padding:14px 18px; margin:10px 0; font-size:1.1rem; line-height:2rem; }
.feedback.good { background: linear-gradient(135deg,#D3F9D8,#C3FAE8); border:3px solid #51CF66; }
.feedback.bad { background: linear-gradient(135deg,#FFE3E3,#FFF0F6); border:3px solid #FF8787; }
.stat { background:#fff; border-radius:16px; padding:8px; text-align:center; box-shadow:0 3px 0 rgba(0,0,0,.08); }
.stat b { font-size:1.5rem; display:block; font-family:'ZCOOL KuaiLe',cursive; }
.flash { background: linear-gradient(135deg,#E5DBFF,#D0EBFF); border-radius:26px; padding:34px 20px; text-align:center;
  box-shadow:0 8px 0 #B197FC; margin: 10px 0 16px 0; }
.flash .w { font-size:3.4rem; font-family:'ZCOOL KuaiLe',cursive; color:#5F3DC4; }
.flash .m { font-size:1.25rem; color:#333; margin-top:8px; }
.badge { display:inline-block; background:#fff; border-radius:14px; padding:6px 10px; margin:4px; box-shadow:0 2px 0 rgba(0,0,0,.1); }
div.stButton > button { border-radius:16px; font-size:1.12rem; padding:.55rem 1rem; border:3px solid #E9ECEF;
  box-shadow:0 4px 0 #DEE2E6; transition: transform .05s; width:100%; white-space: normal; }
div.stButton > button p { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }
.tile { background: linear-gradient(160deg, #fff 0%, #fff 55%, color-mix(in srgb, var(--c) 22%, #fff) 100%);
  border-radius: 22px 22px 8px 8px; padding: 14px 12px 10px 12px; text-align:center; border: 3px solid var(--c);
  box-shadow: 0 5px 0 var(--c); margin-bottom: 8px; }
.tile .ti { font-size: 2.3rem; line-height: 2.8rem; }
.tile .tz { font-family:'ZCOOL KuaiLe',cursive; font-size: 1.45rem; color:#222; }
.tile .te { font-size: .82rem; color:#777; }
.tile .ts { display:inline-block; margin-top:6px; font-size:.82rem; background: var(--c); color:#fff; border-radius:999px; padding:1px 10px; }
[class*="st-key-go_"] button { background: #fff; font-weight:700; padding:.3rem .8rem; margin-bottom: 14px; }
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


# --------------------------------------------------------------------------- state
def init_state():
    ss = st.session_state
    ss.setdefault("page", "home")
    ss.setdefault("name", "")
    ss.setdefault("xp", 0)
    ss.setdefault("streak", 0)
    ss.setdefault("best_streak", 0)
    ss.setdefault("answered", 0)
    ss.setdefault("correct", 0)
    ss.setdefault("by_cat", {})          # cat -> [correct, total]
    ss.setdefault("mistakes", {})        # item-key -> item
    ss.setdefault("badges", [])
    ss.setdefault("quiz", None)
    ss.setdefault("flash", None)
    ss.setdefault("schools", list(SCHOOLS))


def level_info(xp):
    lvl = xp // 100 + 1
    titles = ["华文小芽 🌱", "华文小苗 🌿", "华文小树 🌳", "华文小勇士 🛡️", "华文小侠 🥋", "华文状元 🏆", "华文大师 🐉"]
    return lvl, titles[min(lvl - 1, len(titles) - 1)], xp % 100


def award_badges():
    ss = st.session_state
    rules = [
        ("first", "🌟 第一题答对", ss.correct >= 1),
        ("s5", "🔥 连对5题", ss.best_streak >= 5),
        ("s10", "⚡ 连对10题", ss.best_streak >= 10),
        ("s20", "🚀 连对20题", ss.best_streak >= 20),
        ("c50", "🎖️ 答对50题", ss.correct >= 50),
        ("c150", "👑 答对150题", ss.correct >= 150),
        ("all", "🌈 九大题型都试过", len(ss.by_cat) >= len(CATS)),
    ]
    for key, label, ok in rules:
        if ok and key not in ss.badges:
            ss.badges.append(key)
            st.toast(f"获得新徽章：{label}", icon="🏅")
    return {k: l for k, l, _ in rules}


# --------------------------------------------------------------------------- question rendering
def fill_blanks(stem, answer_text, cls="hl"):
    parts = answer_text.split("……")
    out = stem
    for p in parts:
        out = out.replace("___", f"<span class='{cls}'>{p}</span>", 1)
    return out


def clean_opt(o):
    return re.sub(r"（.*?）", "", o)


def mcq_view(q):
    stem_html = q["stem"].replace("___", "<span class='blank'>？</span>")
    stem_html = re.sub(r"【(.+?)】", r"<u>\1</u>", stem_html)
    if q["type"] == "usage":
        word = re.search(r"（(.+?)）", q["stem"]).group(1)
        stem_html = f"以下哪一个句子是正确的？<br>词语：<span class='hl'>{word}</span>"
    right = q["options"][q["answer"]]
    if q["type"] == "pinyin":
        w = re.search(r"【(.+?)】", q["stem"]).group(1)
        expl = f"<b>{w}</b> 读作 <b>{right}</b>。<br>{q['stem'].replace('【','').replace('】','')}"
        speak = w
    elif q["type"] == "meaning":
        w = re.search(r"【(.+?)】", q["stem"]).group(1)
        expl = f"「<b>{w}</b>」的意思是：<b>{right}</b>。"
        speak = q["stem"].replace("【", "").replace("】", "")
    elif q["type"] == "usage":
        expl = f"正确的句子是：<br><span class='hl'>{right}</span><br>其他句子的「{re.search(r'（(.+?)）', q['stem']).group(1)}」用错了地方。"
        speak = right
    else:
        full = fill_blanks(q["stem"], clean_opt(right))
        expl = f"完整的句子：<br>{full}"
        speak = re.sub("<.*?>", "", full)
        if q["type"] == "connector":
            first = right.split("……")[0]
            if first in CONNECTOR_NOTES:
                expl += f"<br>📝 {CONNECTOR_NOTES[first]}"
        if q["type"] == "hanzi":
            expl = f"正确的字是「<b>{clean_opt(right)}</b>」。<br>" + expl
    if q.get("note"):
        expl += f"<br><small>{q['note']}</small>"
    return dict(cat=q["type"], school=q["school"], label=f"Q{q['n']}", html=f"<div class='qtext'>{stem_html}</div>",
                options=q["options"], answer=q["answer"], expl=expl, speak=speak)


def render_cloze_passage(c, upto_n, picks):
    """Show the passage: earlier blanks filled (green/red), current blank highlighted, later blanks grey."""
    text = c["passage"]
    for b in c["blanks"]:
        n = b["n"]
        tok = "{%d}" % n
        if n < upto_n:
            ok = picks.get(n) == b["answer"]
            right = b["options"][b["answer"]]
            chip = f"<span class='chip ok'>{right}</span>" if ok else \
                   f"<span class='chip no'><s>{b['options'][picks[n]]}</s></span><span class='chip ok'>{right}</span>" \
                   if n in picks else f"<span class='chip ok'>{right}</span>"
        elif n == upto_n:
            chip = f"<span class='chip now'>Q{n} ❓</span>"
        else:
            chip = f"<span class='chip todo'>Q{n}</span>"
        text = text.replace(tok, chip)
    paras = "".join(f"<p style='text-indent:2em;margin:0 0 6px 0'>{p}</p>" for p in text.split("\n"))
    return f"<div class='passage'>{paras}</div>"


def cloze_view(ci, n, picks):
    c = CLOZE[ci]
    b = next(x for x in c["blanks"] if x["n"] == n)
    right = b["options"][b["answer"]]
    sent = sentence_around(c["passage"], n, right, c)
    expl = f"Q{n} 应该填「<b>{right}</b>」。<br>{sent}"
    if b.get("note"):
        expl += f"<br><small>{b['note']}</small>"
    return dict(cat="cloze", school=c["school"], label=f"Q{n}", html=render_cloze_passage(c, n, picks),
                options=b["options"], answer=b["answer"], expl=expl, speak=re.sub("<.*?>", "", sent))


def sentence_around(passage, n, word, c):
    tok = "{%d}" % n
    i = passage.index(tok)
    start = max(passage.rfind(ch, 0, i) for ch in "。！？\n") + 1
    ends = [passage.find(ch, i) for ch in "。！？"]
    end = min(e for e in ends if e != -1) + 1 if any(e != -1 for e in ends) else len(passage)
    s = passage[start:end].replace(tok, f"<span class='hl'>{word}</span>")
    for b in c["blanks"]:
        s = s.replace("{%d}" % b["n"], b["options"][b["answer"]])
    return s.strip("”“ ")


WHO_COLORS = ["#FF8787", "#4DABF7", "#69DB7C", "#DA77F2"]


def dialog_view(di, n, picks):
    d = DIALOGUES[di]
    whos = []
    for l in d["lines"]:
        if l["who"] not in whos:
            whos.append(l["who"])
    bank = "<br>".join(f"<b>{i+1}</b>　{o}" for i, o in enumerate(d["options"]))
    rows = []
    for l in d["lines"]:
        t = l["text"]
        for k, a in d["answers"].items():
            tok = "{%s}" % k
            if tok not in t:
                continue
            k = int(k)
            if k < n:
                ok = picks.get(k) == a
                chip = f"<span class='chip ok'>{d['options'][a]}</span>" if ok or k not in picks else \
                       f"<span class='chip no'><s>{d['options'][picks[k]]}</s></span><span class='chip ok'>{d['options'][a]}</span>"
            elif k == n:
                chip = f"<span class='chip now'>Q{k} ❓</span>"
            else:
                chip = f"<span class='chip todo'>Q{k}</span>"
            t = t.replace(tok, chip)
        col = WHO_COLORS[whos.index(l["who"]) % len(WHO_COLORS)]
        rows.append(f"<div class='chat'><div class='who' style='background:{col}'>{l['who']}</div><div class='say'>{t}</div></div>")
    html = f"<div class='bank'>{bank}</div><div style='margin-top:10px'>{''.join(rows)}</div>"
    a = d["answers"][str(n)]
    line = next(l for l in d["lines"] if "{%d}" % n in l["text"])
    full = line["text"].replace("{%d}" % n, f"<span class='hl'>{d['options'][a]}</span>")
    for k, aa in d["answers"].items():
        full = full.replace("{%s}" % k, d["options"][aa])
    expl = f"Q{n} 应该选 <b>{a+1}</b>：「{d['options'][a]}」<br>{line['who']}：{full}"
    return dict(cat="dialog", school=d["school"], label=f"Q{n}", html=html, options=d["options"],
                answer=a, expl=expl, speak=re.sub("<.*?>", "", full), numbered=True)


def view_for(item, picks):
    if item["kind"] == "mcq":
        return mcq_view(MCQ[item["id"]])
    if item["kind"] == "cloze":
        return cloze_view(item["ci"], item["n"], picks)
    return dialog_view(item["di"], item["n"], picks)


def item_key(item):
    if item["kind"] == "mcq":
        return item["id"]
    if item["kind"] == "cloze":
        return f"cloze-{item['ci']}-{item['n']}"
    return f"dialog-{item['di']}-{item['n']}"


def speak_button(text, key):
    safe = json.dumps(text)
    html = f"""
<button id="b" style="font-size:16px;border-radius:14px;border:2px solid #74C0FC;background:#E7F5FF;padding:6px 14px;cursor:pointer">
🔊 听一听</button>
<script>
document.getElementById('b').onclick = function() {{
  const u = new SpeechSynthesisUtterance({safe}); u.lang = 'zh-CN'; u.rate = 0.85;
  const v = speechSynthesis.getVoices().find(v => v.lang && v.lang.startsWith('zh'));
  if (v) u.voice = v; speechSynthesis.cancel(); speechSynthesis.speak(u);
}};
</script>"""
    if hasattr(st, "iframe"):
        st.iframe(html, height=46)
    else:
        components.html(html, height=46)


# --------------------------------------------------------------------------- quiz engine
def start_quiz(items, title, shuffle_opts=True):
    order = {}
    for it in items:
        if it["kind"] == "mcq" and shuffle_opts:
            perm = list(range(4))
            random.shuffle(perm)
            order[item_key(it)] = perm
    st.session_state.quiz = dict(items=items, i=0, title=title, picked=None, score=0, order=order,
                                 cloze_picks={}, dialog_picks={}, results=[])
    st.session_state.page = "quiz"


def record(view, item, ok):
    ss = st.session_state
    ss.answered += 1
    c = ss.by_cat.setdefault(view["cat"], [0, 0])
    c[1] += 1
    k = item_key(item)
    if ok:
        ss.correct += 1
        c[0] += 1
        ss.streak += 1
        ss.best_streak = max(ss.best_streak, ss.streak)
        gain = 10 + min(ss.streak, 10)
        ss.xp += gain
        ss.mistakes.pop(k, None)
        if ss.streak in (5, 10, 15, 20, 30):
            st.balloons()
    else:
        ss.streak = 0
        ss.xp += 2
        ss.mistakes[k] = item
    award_badges()


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
    picks = qz["cloze_picks"] if item["kind"] == "cloze" else qz["dialog_picks"]
    pick_map = picks.get(item.get("ci", item.get("di")), {})
    v = view_for(item, pick_map)
    meta = CATS[v["cat"]]

    top = st.columns([3, 1])
    top[0].markdown(f"### {qz['title']}")
    if top[1].button("🏠 返回", key="back"):
        ss.page = "home"
        st.rerun()
    st.progress(qz["i"] / len(items), text=f"第 {qz['i']+1} / {len(items)} 题　·　得分 {qz['score']}　·　🔥 连对 {ss.streak}")

    sch = SCHOOLS[v["school"]]
    st.markdown(
        f"<div class='qcard' style='--c:{meta['color']}'><span class='qtag'>{meta['icon']} {meta['zh']}</span>"
        f"<span style='float:right;color:#999;font-size:.85rem'>{sch['zh']} · {v['label']}</span>"
        f"<div style='color:#666;margin-bottom:6px'>{meta['tip']}</div>{v['html']}</div>",
        unsafe_allow_html=True)

    opts = v["options"]
    perm = qz["order"].get(item_key(item), list(range(len(opts))))
    numbered = v.get("numbered")

    if qz["picked"] is None:
        ncol = 2 if len(opts) <= 4 or numbered else 2
        cols = st.columns(ncol)
        for pos, oi in enumerate(perm):
            label = f"{oi+1}　{opts[oi]}" if numbered else opts[oi]
            with cols[pos % ncol]:
                if st.button(label, key=f"c{pos}_q", use_container_width=True):
                    qz["picked"] = oi
                    ok = oi == v["answer"]
                    if ok:
                        qz["score"] += 1
                    qz["results"].append(ok)
                    if item["kind"] in ("cloze", "dialog"):
                        picks.setdefault(item.get("ci", item.get("di")), {})[item["n"]] = oi
                    record(v, item, ok)
                    st.rerun()
    else:
        picked = qz["picked"]
        ok = picked == v["answer"]
        for oi in perm:
            label = f"{oi+1}　{opts[oi]}" if numbered else opts[oi]
            if oi == v["answer"]:
                st.markdown(f"<div class='res right'>✅ {label}</div>", unsafe_allow_html=True)
            elif oi == picked:
                st.markdown(f"<div class='res wrong'>❌ {label}</div>", unsafe_allow_html=True)
            elif not numbered:
                st.markdown(f"<div class='res dim'>{label}</div>", unsafe_allow_html=True)
        if ok:
            st.markdown(f"<div class='feedback good'>🐼 <b>{random.choice(CHEERS)}</b> +{10 + min(ss.streak, 10)} XP<br>{v['expl']}</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback bad'>🐼 <b>{random.choice(COMFORT)}</b> 这题已放进错题本 📕<br>{v['expl']}</div>",
                        unsafe_allow_html=True)
        speak_button(v["speak"], key=f"sp{qz['i']}")
        if st.button("下一题 ➜" if qz["i"] + 1 < len(items) else "看成绩 🏁", key="next", use_container_width=True):
            qz["i"] += 1
            qz["picked"] = None
            st.rerun()


def quiz_summary():
    ss = st.session_state
    qz = ss.quiz
    n = len(qz["items"])
    pct = qz["score"] / n if n else 0
    stars = 3 if pct >= .9 else 2 if pct >= .7 else 1 if pct >= .5 else 0
    st.markdown(f"<div class='hero'><h1>{'⭐' * stars or '💪'}</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='qcard' style='--c:#FCC419;text-align:center'><div class='fun' style='font-size:2rem'>"
                f"{qz['title']} 完成！</div><div style='font-size:1.4rem'>答对 <b>{qz['score']}</b> / {n} 题（{pct:.0%}）</div>"
                f"<div style='margin-top:8px'>{['再练练，你一定可以的！','不错哦，继续加油！','很棒！差一点就满分了！','太厉害了！华文小高手！'][stars]}</div></div>",
                unsafe_allow_html=True)
    if pct == 1 and n >= 5:
        st.balloons()
        if "perfect" not in ss.badges:
            ss.badges.append("perfect")
            st.toast("获得新徽章：💯 满分通关", icon="🏅")
    c1, c2 = st.columns(2)
    if c1.button("🔁 再来一次", key="start", use_container_width=True):
        items = qz["items"][:]
        if all(i["kind"] == "mcq" for i in items):
            random.shuffle(items)
        start_quiz(items, qz["title"])
        st.rerun()
    if c2.button("🏠 回到主页", use_container_width=True):
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
        st.markdown("<div class='fun' style='font-size:1.6rem;text-align:center'>🐼 我的成绩</div>", unsafe_allow_html=True)
        ss.name = st.text_input("你的名字", value=ss.name, placeholder="写下你的名字")
        lvl, title, into = level_info(ss.xp)
        st.markdown(f"<div style='text-align:center;font-size:1.1rem'>Lv.{lvl} <b>{title}</b></div>", unsafe_allow_html=True)
        st.progress(into / 100, text=f"{ss.xp} XP · 再 {100-into} XP 升级")
        c = st.columns(3)
        acc = f"{ss.correct/ss.answered:.0%}" if ss.answered else "–"
        for col, (lab, val) in zip(c, [("答题", ss.answered), ("正确率", acc), ("最高连对", ss.best_streak)]):
            col.markdown(f"<div class='stat'><b>{val}</b>{lab}</div>", unsafe_allow_html=True)
        names = award_badges()
        if ss.badges:
            names["perfect"] = "💯 满分通关"
            st.markdown("**🏅 徽章**<br>" + "".join(f"<span class='badge'>{names.get(b, b)}</span>" for b in ss.badges),
                        unsafe_allow_html=True)
        st.divider()
        with st.expander("🏫 选择学校试卷"):
            ss.schools = st.multiselect("只练这些学校的题目", list(SCHOOLS), default=ss.schools,
                                        format_func=lambda s: SCHOOLS[s]["zh"]) or list(SCHOOLS)
        with st.expander("💾 保存 / 读取进度"):
            keep = {k: ss[k] for k in ("name", "xp", "streak", "best_streak", "answered", "correct", "by_cat", "mistakes", "badges")}
            st.download_button("下载我的进度", json.dumps(keep, ensure_ascii=False),
                               file_name=f"p6-chinese-progress-{dt.date.today()}.json", use_container_width=True)
            up = st.file_uploader("上传进度文件", type="json")
            if up is not None and st.button("读取进度", use_container_width=True):
                try:
                    for k, v in json.loads(up.read().decode("utf-8")).items():
                        ss[k] = v
                    st.success("进度已读取！")
                    st.rerun()
                except Exception:
                    st.error("文件不正确，请再试一次。")
        st.caption("题目来自 2026 年十所小学的小六华文预考试卷（试卷二）。")


def page_home():
    ss = st.session_state
    hello = f"{ss.name}，" if ss.name else ""
    st.markdown("<div class='hero'><h1>小六华文冲冲冲！</h1><p>P6 Chinese practice · 2026 Prelim papers</p></div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='bubble'>🐼 {hello}你好！我是熊猫老师。今天想练什么？每答对一题就能得到 XP，连续答对还有加分哦！</div>",
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("🚀 综合挑战（10题）", key="start", use_container_width=True):
        pool = [{"kind": "mcq", "id": q["id"]} for q in DATA["mcq"] if school_ok(q["school"])]
        start_quiz(random.sample(pool, min(10, len(pool))), "🚀 综合挑战")
        st.rerun()
    n_mis = len(ss.mistakes)
    if c2.button(f"📕 错题本（{n_mis}）", use_container_width=True, disabled=n_mis == 0):
        items = list(ss.mistakes.values())
        start_quiz(items, "📕 错题再练")
        st.rerun()

    st.markdown("### 🎯 语文应用")
    cats = ["pinyin", "hanzi", "word", "meaning", "connector", "sentence", "usage"]
    cols = st.columns(2)
    for i, cat in enumerate(cats):
        m = CATS[cat]
        n = len(mcq_items(cat))
        done = ss.by_cat.get(cat, [0, 0])
        stat = f"✅ {done[0]}/{done[1]} 答对" if done[1] else f"共 {n} 题"
        if tile(cols[i % 2], f"go_{cat}", m["icon"], m["zh"], m["en"], stat, m["color"]):
            start_quiz(mcq_items(cat, 10), f"{m['icon']} {m['zh']}")
            st.rerun()

    st.markdown("### 📖 读一读，填一填")
    c1, c2 = st.columns(2)
    if tile(c1, "go_cloze", "📖", "短文填空", "Passage fill-in", "10 篇短文 · 50 个空格", CATS["cloze"]["color"]):
        ss.page = "pick_cloze"
        st.rerun()
    if tile(c2, "go_dialog", "💬", "完成对话", "Complete the dialogue", "10 段对话 · 40 个空格", CATS["dialog"]["color"]):
        ss.page = "pick_dialog"
        st.rerun()

    st.markdown("### 🃏 词语加油站")
    c1, c2, c3 = st.columns(3)
    if tile(c1, "go_flash", "🃏", "词语卡", "Flashcards", "读音 · 词义 · 例句", "#9775FA"):
        start_flash()
        st.rerun()
    if tile(c2, "go_match", "🎯", "词义配对", "Match meanings", "看意思，选词语", "#20C997"):
        ss.page = "match"
        ss.match = None
        st.rerun()
    if tile(c3, "go_paper", "🏫", "整份试卷", "Full paper", "按学校做一整份", "#FF922B"):
        ss.page = "pick_paper"
        st.rerun()


def tile(col, key, icon, zh, en, sub, color):
    with col:
        st.markdown(
            f"<div class='tile' style='--c:{color}'><div class='ti'>{icon}</div><div class='tz'>{zh}</div>"
            f"<div class='te'>{en}</div><div class='ts'>{sub}</div></div>", unsafe_allow_html=True)
        return st.button("开始 ▶", key=key, use_container_width=True)


def page_pick(kind):
    ss = st.session_state
    title = "📖 选一篇短文" if kind == "cloze" else "💬 选一段对话" if kind == "dialog" else "🏫 选一份试卷"
    st.markdown(f"## {title}")
    if st.button("🏠 返回", key="back"):
        ss.page = "home"
        st.rerun()
    src = CLOZE if kind == "cloze" else DIALOGUES if kind == "dialog" else [{"school": s} for s in SCHOOLS]
    cols = st.columns(2)
    for i, x in enumerate(src):
        s = SCHOOLS[x["school"]]
        if kind == "cloze":
            preview = re.sub(r"\{\d+\}", "＿", x["passage"])[:22] + "……"
        elif kind == "dialog":
            preview = re.sub(r"\{\d+\}", "＿", x["lines"][0]["text"])[:22] + "……"
        else:
            preview = "15题语文应用 + 短文填空 + 完成对话"
        with cols[i % 2]:
            if st.button(f"🏫 {s['zh']}：{preview}", key=f"c{i % 9}_p{i}", use_container_width=True):
                if kind == "cloze":
                    start_quiz(cloze_items(i), f"📖 短文填空 · {s['zh']}")
                elif kind == "dialog":
                    start_quiz(dialog_items(i), f"💬 完成对话 · {s['zh']}")
                else:
                    sid = x["school"]
                    items = [{"kind": "mcq", "id": f"{sid}-Q{n}"} for n in range(1, 16)]
                    ci = next(j for j, c in enumerate(CLOZE) if c["school"] == sid)
                    di = next(j for j, d in enumerate(DIALOGUES) if d["school"] == sid)
                    start_quiz(items + cloze_items(ci) + dialog_items(di), f"🏫 {s['zh']} 整份练习", shuffle_opts=False)
                st.rerun()


# ---- flashcards
def flash_deck():
    seen, deck = set(), []
    for v in VOCAB:
        if not school_ok(v["school"]):
            continue
        w = v["word"]
        if w in seen:
            for d in deck:
                if d["word"] == w:
                    d.update({k: v[k] for k in ("meaning", "pinyin", "example") if k in v and k not in d})
            continue
        seen.add(w)
        deck.append(dict(v))
    random.shuffle(deck)
    return deck


def start_flash():
    st.session_state.flash = dict(deck=flash_deck(), i=0, flipped=False, known=0)
    st.session_state.page = "flash"


def page_flash():
    ss = st.session_state
    f = ss.flash
    top = st.columns([3, 1])
    top[0].markdown("## 🃏 词语卡")
    if top[1].button("🏠 返回", key="back"):
        ss.page = "home"
        st.rerun()
    deck = f["deck"]
    if f["i"] >= len(deck):
        st.markdown(f"<div class='bubble'>🐼 全部看完啦！你认得 <b>{f['known']}</b> / {len(deck)} 个词语。</div>", unsafe_allow_html=True)
        if st.button("🔁 再来一轮", key="start", use_container_width=True):
            start_flash()
            st.rerun()
        return
    card = deck[f["i"]]
    st.progress(f["i"] / len(deck), text=f"第 {f['i']+1} / {len(deck)} 张 · 认得 {f['known']}")
    back = ""
    if f["flipped"]:
        if card.get("pinyin"):
            back += f"<div class='m'>🔤 {card['pinyin']}</div>"
        if card.get("meaning"):
            back += f"<div class='m'>💡 {card['meaning']}</div>"
        if card.get("example"):
            ex = card["example"].replace(card["word"], f"<span class='hl'>{card['word']}</span>")
            back += f"<div class='m' style='font-size:1.05rem;color:#555'>📝 {ex}</div>"
    else:
        back = "<div class='m' style='color:#888'>先想一想：怎么读？什么意思？然后翻开看看 👇</div>"
    st.markdown(f"<div class='flash'><div class='w'>{card['word']}</div>{back}</div>", unsafe_allow_html=True)
    speak_button(card["word"], key=f"fs{f['i']}")
    if not f["flipped"]:
        if st.button("🔄 翻开卡片", key="next", use_container_width=True):
            f["flipped"] = True
            st.rerun()
    else:
        c1, c2 = st.columns(2)
        if c1.button("😊 我会了", key="c1_known", use_container_width=True):
            f["known"] += 1
            ss.xp += 3
            f["i"] += 1
            f["flipped"] = False
            st.rerun()
        if c2.button("🤔 再练练", key="c0_again", use_container_width=True):
            deck.append(card)
            f["i"] += 1
            f["flipped"] = False
            st.rerun()


# ---- meaning match (generated from vocab with meanings)
def page_match():
    ss = st.session_state
    top = st.columns([3, 1])
    top[0].markdown("## 🎯 词义配对")
    if top[1].button("🏠 返回", key="back"):
        ss.page = "home"
        st.rerun()
    pool = {}
    for v in VOCAB:
        if v.get("meaning") and school_ok(v["school"]):
            pool.setdefault(v["word"], v["meaning"])
    words = list(pool)
    if ss.get("match") is None:
        qs = random.sample(words, min(10, len(words)))
        ss.match = dict(qs=[(w, random.sample([w] + random.sample([x for x in words if x != w], 3), 4)) for w in qs],
                        i=0, picked=None, score=0)
    m = ss.match
    if m["i"] >= len(m["qs"]):
        st.markdown(f"<div class='qcard' style='--c:#FCC419;text-align:center'><div class='fun' style='font-size:2rem'>配对完成！</div>"
                    f"<div style='font-size:1.4rem'>答对 {m['score']} / {len(m['qs'])}</div></div>", unsafe_allow_html=True)
        if m["score"] == len(m["qs"]):
            st.balloons()
        if st.button("🔁 再来一组", key="start", use_container_width=True):
            ss.match = None
            st.rerun()
        return
    w, choices = m["qs"][m["i"]]
    st.progress(m["i"] / len(m["qs"]), text=f"第 {m['i']+1} / {len(m['qs'])} 题 · 得分 {m['score']}")
    st.markdown(f"<div class='qcard' style='--c:#20C997'><span class='qtag'>🎯 哪个词语是这个意思？</span>"
                f"<div class='qtext'>「{pool[w]}」</div></div>", unsafe_allow_html=True)
    if m["picked"] is None:
        cols = st.columns(2)
        for i, c in enumerate(choices):
            with cols[i % 2]:
                if st.button(c, key=f"c{i}_m", use_container_width=True):
                    m["picked"] = c
                    ok = c == w
                    m["score"] += ok
                    ss.answered += 1
                    if ok:
                        ss.correct += 1
                        ss.streak += 1
                        ss.best_streak = max(ss.best_streak, ss.streak)
                        ss.xp += 10
                    else:
                        ss.streak = 0
                    st.rerun()
    else:
        for c in choices:
            cls = "right" if c == w else "wrong" if c == m["picked"] else "dim"
            st.markdown(f"<div class='res {cls}'>{'✅ ' if c == w else '❌ ' if c == m['picked'] else ''}{c}</div>", unsafe_allow_html=True)
        good = m["picked"] == w
        st.markdown(f"<div class='feedback {'good' if good else 'bad'}'>🐼 <b>{random.choice(CHEERS if good else COMFORT)}</b>"
                    f"<br>「<b>{w}</b>」：{pool[w]}</div>", unsafe_allow_html=True)
        if st.button("下一题 ➜", key="next", use_container_width=True):
            m["i"] += 1
            m["picked"] = None
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
elif page == "match":
    page_match()
