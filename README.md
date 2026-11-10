# 🐼 小六华文冲冲冲！ P6 Chinese Practice

A colourful, game-style Streamlit app for Primary 6 Chinese practice with instant feedback —
built for a child who is stronger in English: **every Chinese character has Hanyu Pinyin above it,
and every question, option, passage and dialogue has an English translation.**
Every question comes from the **2026 P6 Chinese Preliminary Examination (Paper 2)** of ten schools:
ACS (Junior), Ai Tong, Catholic High, Henry Park, Methodist Girls', Nan Hua, Nanyang,
Raffles Girls', Red Swastika and St. Nicholas Girls'.

## What's inside

| Mode | Questions |
|---|---|
| 🔤 拼音小达人 Hanyu Pinyin | 20 |
| ✍️ 汉字侦探 Correct character | 20 |
| 📚 词语百宝箱 Choose the word | 20 |
| 💡 词义解码 Word meanings | 20 |
| 🔗 关联词魔法 Connectors (grammar, with notes) | 20 |
| 🧩 句子拼图 Complete the sentence | 20 |
| ⚖️ 用词小法官 Correct usage | 30 |
| 📖 短文填空 Passage cloze | 10 passages / 50 blanks |
| 💬 完成对话 Complete the dialogue | 10 dialogues / 40 blanks |
| 🃏 词语卡 Flashcards | 60 words |
| 🌏 词语大考验 Word quiz (Chinese → English, English → Chinese) | ~230 words |
| 🏫 整份试卷 Full paper by school · 🚀 Mixed challenge · 📕 Mistake book | — |

## Three help levels

| Level | What the child sees | XP |
|---|---|---|
| 🟢 学习 Learn | Pinyin on every character + English everywhere | ×1 |
| 🟡 练习 Practice | Pinyin shown, English only when tapped | ×1.5 |
| 🔴 考试 Exam | Chinese only, like the real paper (pinyin/English can be tapped, but then the bonus is lost) | ×2 |

The sidebar keeps a separate **🧠 Chinese-only score** (Exam mode with no hints), so you can see how much
Chinese your child really understands on their own. After every answer, the full sentence is shown with pinyin and English
whatever the level, so each question is also a mini lesson.

Fun bits: XP and levels, streak bonuses, badges, balloons, a panda coach, 🔊 read-aloud
(browser speech), wrong answers go to the 错题本 automatically, and progress can be
downloaded/uploaded as a file (Streamlit Cloud doesn't keep data between visits).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (GitHub + Streamlit Community Cloud)

1. Create a new GitHub repository (e.g. `p6-chinese-app`) and upload everything in this folder
   (or `git init && git add . && git commit -m "P6 Chinese app" && git push`).
2. Go to <https://share.streamlit.io>, sign in with GitHub, click **Create app**.
3. Pick the repository, branch `main`, main file `app.py`, then **Deploy**.
4. Share the `*.streamlit.app` link with your child.

## Editing / adding questions

The questions live in `tools/source/<School>.txt`, English translations in `tools/source/en/<School>.txt` (one line per question, human-readable)
and the answer keys in `tools/keys.txt`. After editing, rebuild the app data:

```bash
python tools/build_data.py
```

Line format:

```
Q5|word|句子，空格用 ___ 表示。|选项1;选项2;选项3;选项4
Q1|pinyin|画线词语用【】标出。|...
Q17|力量;精神;意义;耐心|!2      ← "!2" overrides the school's key (used where the key was wrong)
CLOZE|短文……{16}……{17}……          (\n = new paragraph)
DOPT|对话选项1;选项2;...
L|说话人|对话内容 {26}
V|词语|意思
```

English files are `N|English` lines in the order printed by `python tools/needed_en.py <School>`.
Pinyin is generated automatically (`pinyin_util.py`, using `pypinyin`); fixes for tricky readings
such as 地/得/都/还 are in `PHRASE_FIX` and the rules there.

Types: `pinyin`, `hanzi`, `word`, `meaning`, `connector`, `sentence`, `usage`.

### Note on answer keys
Henry Park's printed key gives Q17 = 4 (耐心) and Q18 = 4 (然后). The passage reads
"上课时更有__，做事情也更专心了" and "__，我还参加了学校的羽毛球队", so the app uses
2 (精神) and 2 (此外) and shows a note explaining this.
