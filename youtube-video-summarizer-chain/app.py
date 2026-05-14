import streamlit as st
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TubeLearn",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Instrument+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #12110f !important;
    color: #e8e0d0 !important;
    font-family: 'Instrument Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 40% at 10% 0%, rgba(255,160,50,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 50% 35% at 90% 100%, rgba(230,100,60,0.06) 0%, transparent 55%),
        #12110f !important;
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

.block-container {
    max-width: 900px !important;
    padding: 2.5rem 2rem 6rem !important;
    margin: 0 auto !important;
}

/* ── Hero ── */
.hero { padding: 3.5rem 0 2rem; text-align: center; }
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: rgba(255,160,50,0.7);
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.6rem, 5.5vw, 4rem);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #f0e8d8;
    margin-bottom: 0.7rem;
}
.hero-title span {
    background: linear-gradient(120deg, #ffa032, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: rgba(232,224,208,0.38);
    letter-spacing: 0.05em;
    margin-bottom: 2.8rem;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    box-shadow: 0 2px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
    margin-bottom: 2rem;
}

[data-testid="stTextInput"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: rgba(255,160,50,0.65) !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #f0e8d8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(255,160,50,0.5) !important;
    box-shadow: 0 0 0 3px rgba(255,160,50,0.1) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: rgba(232,224,208,0.2) !important; }

/* ── Primary Button ── */
[data-testid="stButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #ff9a20 0%, #ff5722 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.8rem 2rem !important;
    margin-top: 0.9rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 22px rgba(255,100,30,0.35) !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(255,100,30,0.5) !important;
}

/* ── Processing steps ── */
.proc-wrap { margin: 1.5rem 0; }
.proc-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(255,160,50,0.5);
    margin-bottom: 1rem;
}
.proc-step {
    display: flex; align-items: center; gap: 0.85rem;
    padding: 0.7rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.4rem;
    border: 1px solid rgba(255,255,255,0.04);
    background: rgba(255,255,255,0.015);
    transition: all 0.3s;
}
.proc-step.active {
    border-color: rgba(255,160,50,0.35);
    background: rgba(255,160,50,0.07);
    box-shadow: 0 0 18px rgba(255,160,50,0.1);
}
.proc-step.done {
    border-color: rgba(74,222,128,0.25);
    background: rgba(74,222,128,0.04);
}
.proc-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: rgba(255,255,255,0.12); flex-shrink: 0;
}
.proc-step.active .proc-dot { background: #ffa032; animation: blink 1.2s ease-in-out infinite; }
.proc-step.done .proc-dot { background: #4ade80; }
@keyframes blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(255,160,50,0.5); }
    50% { opacity: 0.5; box-shadow: 0 0 0 5px rgba(255,160,50,0); }
}
.proc-text { font-size: 0.83rem; color: rgba(232,224,208,0.45); flex: 1; }
.proc-step.active .proc-text { color: #e8e0d0; }
.proc-step.done .proc-text { color: rgba(232,224,208,0.6); }
.proc-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; }
.proc-step.done .proc-badge { color: #4ade80; }
.proc-step.active .proc-badge { color: #ffa032; }

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    margin-bottom: 1.8rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: rgba(232,224,208,0.45) !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(255,160,50,0.14) !important;
    color: #ffa032 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* ── Summary ── */
.summary-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    line-height: 1.8;
    font-size: 0.93rem;
    color: rgba(232,224,208,0.82);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* ── Notes ── */
.notes-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.8rem 2rem;
}
.note-block {
    border-left: 2px solid rgba(255,160,50,0.4);
    padding: 0.7rem 0 0.7rem 1.4rem;
    margin-bottom: 1rem;
}
.note-block h4 {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 500;
    color: #f0e8d8; margin-bottom: 0.35rem;
}
.note-block p { font-size: 0.86rem; color: rgba(232,224,208,0.65); line-height: 1.7; margin: 0 0 0.2rem; }

/* ── Quiz ── */
.quiz-question {
    font-family: 'Playfair Display', serif;
    font-size: 1.12rem; font-weight: 500;
    color: #f0e8d8; line-height: 1.5;
    padding: 1.5rem 1.8rem;
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1.2rem;
}
.quiz-counter {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.15em;
    color: rgba(255,160,50,0.6);
    margin-bottom: 1rem;
}
.quiz-opt {
    display: flex; align-items: center; gap: 0.9rem;
    padding: 0.85rem 1.2rem;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.025);
    margin-bottom: 0.55rem;
    font-size: 0.88rem;
    color: rgba(232,224,208,0.7);
    transition: all 0.2s;
}
.quiz-opt.correct { border-color: rgba(74,222,128,0.5); background: rgba(74,222,128,0.08); color: #f0e8d8; }
.quiz-opt.wrong   { border-color: rgba(239,68,68,0.5);  background: rgba(239,68,68,0.08);  color: #f0e8d8; }
.quiz-opt-letter {
    width: 26px; height: 26px; border-radius: 6px;
    background: rgba(255,255,255,0.07);
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; flex-shrink: 0;
}
.score-banner {
    text-align: center;
    padding: 2.5rem 2rem;
    background: rgba(255,160,50,0.06);
    border: 1px solid rgba(255,160,50,0.2);
    border-radius: 16px;
    margin-bottom: 2rem;
}
.score-big {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem; font-weight: 700;
    color: #ffa032; line-height: 1;
}
.score-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.2em;
    color: rgba(232,224,208,0.45); margin-top: 0.5rem;
    text-transform: uppercase;
}

/* ── Flashcards ── */
.fc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
}
.fc-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    transition: border-color 0.25s, transform 0.2s, box-shadow 0.2s;
}
.fc-card:hover {
    border-color: rgba(255,160,50,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.fc-front {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: rgba(255,160,50,0.7);
    margin-bottom: 0.6rem;
}
.fc-term {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 500;
    color: #f0e8d8; margin-bottom: 0.7rem; line-height: 1.35;
}
.fc-divider { height: 1px; background: rgba(255,255,255,0.07); margin: 0.7rem 0; }
.fc-def { font-size: 0.82rem; color: rgba(232,224,208,0.6); line-height: 1.65; }

/* ── Misc ── */
.divider { height: 1px; background: rgba(255,255,255,0.05); margin: 2rem 0; }
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.22em;
    text-transform: uppercase; color: rgba(255,160,50,0.5);
    margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 0.7rem;
}
.section-label::after { content: ''; flex:1; height:1px; background:rgba(255,255,255,0.05); }
.err-card {
    background: rgba(239,68,68,0.07);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #fca5a5;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_quiz(raw: str) -> list:
    questions = []
    blocks = re.split(r'\n(?=Q\d+[\.\)])', raw.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        q_text = re.sub(r'^Q\d+[\.\)]\s*', '', lines[0])
        options, answer = [], None
        seen_letters = set()
        for line in lines[1:]:
            am = re.match(r'^[Aa]nswer\s*[:\-]\s*([A-D])', line, re.I)
            if am:
                answer = am.group(1).upper()
                continue
            m = re.match(r'^([A-D])[\.\)]\s*(.+)', line, re.I)
            if m:
                letter = m.group(1).upper()
                if letter in seen_letters:
                    continue
                seen_letters.add(letter)
                options.append({"letter": letter, "text": m.group(2)})
        if q_text and options:
            questions.append({"question": q_text, "options": options, "answer": answer})
    return questions


def parse_flashcards(raw: str) -> list:
    cards = []
    blocks = re.split(r'\n(?=Term\s*:)', raw.strip(), flags=re.I)
    for block in blocks:
        tm = re.search(r'Term\s*:\s*(.+)', block, re.I)
        dm = re.search(r'Definition\s*:\s*(.+?)(?=\nTerm|\Z)', block, re.I | re.S)
        if tm and dm:
            cards.append({"term": tm.group(1).strip(), "definition": dm.group(1).strip()})
    return cards


def parse_notes(raw: str) -> list:
    sections, current_title, current_points = [], None, []
    for line in raw.splitlines():
        h = re.match(r'^#+\s+(.+)', line)
        if h:
            if current_title:
                sections.append({"title": current_title, "points": current_points})
            current_title = h.group(1).strip()
            current_points = []
        elif re.match(r'^[-*•]\s+', line):
            current_points.append(re.sub(r'^[-*•]\s+', '', line).strip())
        elif line.strip() and current_title:
            current_points.append(line.strip())
    if current_title:
        sections.append({"title": current_title, "points": current_points})
    if not sections and raw.strip():
        sections.append({"title": "Key Notes", "points": [l.strip() for l in raw.splitlines() if l.strip()]})
    return sections


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("result", None), ("quiz_idx", 0),
                     ("quiz_answers", {}), ("quiz_submitted", False)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">▶ AI-Powered Learning</div>
    <div class="hero-title">Tube<span>Learn</span></div>
    <div class="hero-sub">paste a url → summary · notes · quiz · flashcards</div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=…", label_visibility="visible")
go  = st.button("Analyse Video →")
st.markdown('</div>', unsafe_allow_html=True)


# ── Pipeline renderer ─────────────────────────────────────────────────────────
STEPS = [
    "Downloading & transcribing video",
    "Building vector store & retriever",
    "Running 4 parallel AI chains",
    "Finalising results",
]

def render_proc(active: int, done_upto: int) -> str:
    html = '<div class="proc-wrap"><div class="proc-label">Processing pipeline</div>'
    for i, label in enumerate(STEPS):
        if i < done_upto:
            cls, badge = "done", "✓ done"
        elif i == active:
            cls, badge = "active", "● running"
        else:
            cls, badge = "", "○ queued"
        html += f"""
        <div class="proc-step {cls}">
            <div class="proc-dot"></div>
            <div class="proc-text">{label}</div>
            <div class="proc-badge">{badge}</div>
        </div>"""
    return html + '</div>'


# ── Run ───────────────────────────────────────────────────────────────────────
if go:
    if not url.strip():
        st.markdown('<div class="err-card">⚠ Please paste a YouTube URL first.</div>', unsafe_allow_html=True)
    else:
        st.session_state.result = None
        st.session_state.quiz_idx = 0
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False

        proc_slot = st.empty()
        err_slot  = st.empty()
        try:
            from main import main as run_pipeline

            proc_slot.markdown(render_proc(0, 0), unsafe_allow_html=True)
            proc_slot.markdown(render_proc(1, 1), unsafe_allow_html=True)
            proc_slot.markdown(render_proc(2, 2), unsafe_allow_html=True)
            result = run_pipeline(url.strip())
            proc_slot.markdown(render_proc(3, 4), unsafe_allow_html=True)
            st.session_state.result = result

        except Exception as e:
            proc_slot.empty()
            err_slot.markdown(f'<div class="err-card">⚠ Error: {e}</div>', unsafe_allow_html=True)


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    tab_summary, tab_notes, tab_quiz, tab_flash = st.tabs(
        ["📋  Summary", "📝  Notes", "🧠  Quiz", "🃏  Flashcards"]
    )

    # ── Summary ──────────────────────────────────────────────────────────────
    with tab_summary:
        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="summary-card">{result.get("summary","No summary available.")}</div>',
            unsafe_allow_html=True,
        )

    # ── Notes ────────────────────────────────────────────────────────────────
    with tab_notes:
        st.markdown('<div class="section-label">Structured Notes</div>', unsafe_allow_html=True)
        sections = parse_notes(result.get("notes", ""))
        if sections:
            st.markdown('<div class="notes-wrap">', unsafe_allow_html=True)
            for sec in sections:
                pts = "".join(f"<p>• {p}</p>" for p in sec["points"])
                st.markdown(
                    f'<div class="note-block"><h4>{sec["title"]}</h4>{pts}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="summary-card">{result.get("notes","")}</div>',
                unsafe_allow_html=True,
            )

    # ── Quiz ─────────────────────────────────────────────────────────────────
    with tab_quiz:
        st.markdown('<div class="section-label">Test your knowledge</div>', unsafe_allow_html=True)
        questions = parse_quiz(result.get("quiz", ""))

        if not questions:
            st.markdown(
                f'<div class="summary-card">{result.get("quiz","No quiz generated.")}</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.quiz_submitted:
            # ── Score screen ──────────────────────────────────────────────────
            correct = sum(
                1 for i, q in enumerate(questions)
                if st.session_state.quiz_answers.get(i) == q.get("answer")
            )
            total = len(questions)
            pct = int(correct / total * 100) if total else 0
            st.markdown(f"""
            <div class="score-banner">
                <div class="score-big">{pct}%</div>
                <div class="score-label">{correct} of {total} correct</div>
            </div>""", unsafe_allow_html=True)

            for i, q in enumerate(questions):
                user_ans = st.session_state.quiz_answers.get(i)
                st.markdown(f'<div class="quiz-question">Q{i+1}. {q["question"]}</div>', unsafe_allow_html=True)
                for opt in q["options"]:
                    if opt["letter"] == q.get("answer"):
                        cls = "correct"
                    elif opt["letter"] == user_ans and user_ans != q.get("answer"):
                        cls = "wrong"
                    else:
                        cls = ""
                    st.markdown(f"""
                    <div class="quiz-opt {cls}">
                        <span class="quiz-opt-letter">{opt['letter']}</span>
                        {opt['text']}
                    </div>""", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            if st.button("↺  Retake Quiz"):
                st.session_state.quiz_idx = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
        else:
            # ── Active question ───────────────────────────────────────────────
            idx = st.session_state.quiz_idx
            q   = questions[idx]

            st.markdown(f'<div class="quiz-counter">Question {idx+1} / {len(questions)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="quiz-question">{q["question"]}</div>', unsafe_allow_html=True)

            for opt_i, opt in enumerate(q["options"]):
                selected = st.session_state.quiz_answers.get(idx)
                is_selected = selected == opt["letter"]
                btn_label = f"**{opt['letter']})**  {opt['text']}" if is_selected else f"{opt['letter']})  {opt['text']}"
                if st.button(btn_label, key=f"opt_{idx}_{opt_i}"):
                    st.session_state.quiz_answers[idx] = opt["letter"]
                    st.rerun()

            chosen = st.session_state.quiz_answers.get(idx)
            if chosen:
                st.markdown(
                    f"<p style='font-family:JetBrains Mono,monospace;font-size:0.75rem;"
                    f"color:rgba(255,160,50,0.7);margin-top:0.4rem'>Selected: {chosen}</p>",
                    unsafe_allow_html=True,
                )

            col_prev, col_dots, col_next = st.columns([1, 4, 1])
            with col_prev:
                if idx > 0 and st.button("← Prev"):
                    st.session_state.quiz_idx -= 1
                    st.rerun()
            with col_dots:
                dots = "".join(
                    f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;'
                    f'margin:0 3px;background:{"#ffa032" if i == idx else "rgba(255,255,255,0.12)"}"></span>'
                    for i in range(len(questions))
                )
                st.markdown(
                    f'<div style="text-align:center;padding-top:0.6rem">{dots}</div>',
                    unsafe_allow_html=True,
                )
            with col_next:
                if idx < len(questions) - 1:
                    if st.button("Next →"):
                        st.session_state.quiz_idx += 1
                        st.rerun()
                else:
                    if st.button("Submit ✓"):
                        st.session_state.quiz_submitted = True
                        st.rerun()

    # ── Flashcards ───────────────────────────────────────────────────────────
    with tab_flash:
        st.markdown('<div class="section-label">Flashcards</div>', unsafe_allow_html=True)
        cards = parse_flashcards(result.get("flashcards", ""))

        if not cards:
            st.markdown(
                f'<div class="summary-card">{result.get("flashcards","No flashcards generated.")}</div>',
                unsafe_allow_html=True,
            )
        else:
            grid = '<div class="fc-grid">'
            for card in cards:
                grid += f"""
                <div class="fc-card">
                    <div class="fc-front">Term</div>
                    <div class="fc-term">{card['term']}</div>
                    <div class="fc-divider"></div>
                    <div class="fc-def">{card['definition']}</div>
                </div>"""
            grid += '</div>'
            st.markdown(grid, unsafe_allow_html=True)