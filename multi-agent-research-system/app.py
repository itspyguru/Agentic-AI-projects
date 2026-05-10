import streamlit as st
import time
from agents import build_research_agent, build_reading_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchAI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #080810 !important;
    color: #e8e6f0 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(99,60,255,0.18) 0%, transparent 65%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(255,80,180,0.10) 0%, transparent 60%),
        #080810 !important;
    min-height: 100vh;
}

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container {
    max-width: 860px !important;
    padding: 3rem 2rem 6rem !important;
    margin: 0 auto;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 4rem 0 2.5rem;
}
.hero-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #a78bfa;
    background: rgba(99,60,255,0.12);
    border: 1px solid rgba(99,60,255,0.3);
    border-radius: 100px;
    padding: 0.3em 1.1em;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
}
.hero-title {
    font-size: clamp(2.8rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #fff 30%, #a78bfa 70%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-weight: 300;
    font-size: 0.9rem;
    color: rgba(232,230,240,0.45);
    letter-spacing: 0.04em;
    margin-bottom: 3rem;
}

/* ── Input card ── */
.input-wrapper {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    backdrop-filter: blur(12px);
    margin-bottom: 2rem;
    box-shadow: 0 0 0 1px rgba(99,60,255,0.06), 0 24px 60px rgba(0,0,0,0.5);
}

/* Override streamlit text input */
[data-testid="stTextInput"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: rgba(167,139,250,0.8) !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,60,255,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,60,255,0.12) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: rgba(232,230,240,0.22) !important;
}

/* ── Button ── */
[data-testid="stButton"] button {
    width: 100%;
    background: linear-gradient(135deg, #6b3cff 0%, #a855f7 55%, #ec4899 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 24px rgba(107,60,255,0.35) !important;
    margin-top: 1rem !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(107,60,255,0.5) !important;
}
[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
}

/* ── Pipeline steps ── */
.pipeline-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(167,139,250,0.6);
    margin: 2.5rem 0 1.2rem;
}
.step-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.2rem;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
    transition: all 0.3s ease;
}
.step-row.active {
    border-color: rgba(99,60,255,0.4);
    background: rgba(99,60,255,0.08);
    box-shadow: 0 0 20px rgba(99,60,255,0.12);
}
.step-row.done {
    border-color: rgba(52,211,153,0.3);
    background: rgba(52,211,153,0.05);
}
.step-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    background: rgba(255,255,255,0.05);
}
.step-row.active .step-icon {
    background: rgba(99,60,255,0.25);
    animation: pulse 1.5s infinite;
}
.step-row.done .step-icon {
    background: rgba(52,211,153,0.15);
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99,60,255,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(99,60,255,0); }
}
.step-label {
    font-size: 0.88rem;
    font-weight: 600;
    color: rgba(232,230,240,0.55);
    flex: 1;
}
.step-row.active .step-label { color: #e8e6f0; }
.step-row.done .step-label { color: rgba(232,230,240,0.75); }
.step-status {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
}
.step-row.active .step-status { color: #a78bfa; }
.step-row.done .step-status { color: #34d399; }

/* ── Result cards ── */
.result-section { margin-top: 2.5rem; }
.result-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(167,139,250,0.6);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.result-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}
.result-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.75;
    color: rgba(232,230,240,0.78);
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.result-card.report {
    font-family: 'Syne', sans-serif;
    font-size: 0.92rem;
    border-color: rgba(99,60,255,0.18);
    box-shadow: 0 0 40px rgba(99,60,255,0.08), 0 8px 32px rgba(0,0,0,0.3);
}
.result-card.feedback {
    border-color: rgba(244,114,182,0.18);
    box-shadow: 0 0 40px rgba(244,114,182,0.06), 0 8px 32px rgba(0,0,0,0.3);
}

/* ── Error ── */
.err-card {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    color: #fca5a5;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    margin-top: 1.5rem;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 2.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">◈ Multi-Agent Intelligence</div>
    <div class="hero-title">ResearchAI</div>
    <div class="hero-sub">search → scrape → write → critique · powered by autonomous agents</div>
</div>
""", unsafe_allow_html=True)

# ── Input card ────────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. The impact of quantum computing on cryptography…",
    key="topic_input",
    label_visibility="visible",
)
run = st.button("Generate Report →", key="run_btn")
st.markdown('</div>', unsafe_allow_html=True)

# ── Pipeline ──────────────────────────────────────────────────────────────────
STEPS = [
    ("🔍", "Research Agent", "Crawling the web for relevant data"),
    ("📄", "Reading Agent", "Scraping the best source for depth"),
    ("✍️", "Writer Agent", "Composing the research report"),
    ("🧠", "Critic Agent", "Reviewing and providing feedback"),
]

def render_steps(active: int, done_up_to: int):
    html = '<div class="pipeline-header">Pipeline Progress</div>'
    for i, (icon, label, desc) in enumerate(STEPS):
        if i < done_up_to:
            cls, status = "done", "✓ complete"
        elif i == active:
            cls, status = "active", "● running"
        else:
            cls, status = "", "○ queued"
        html += f"""
        <div class="step-row {cls}">
            <div class="step-icon">{icon}</div>
            <div>
                <div class="step-label">{label}</div>
                <div style="font-size:0.72rem;color:rgba(232,230,240,0.35);font-family:'DM Mono',monospace;margin-top:2px">{desc}</div>
            </div>
            <div class="step-status">{status}</div>
        </div>"""
    return html

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.markdown('<div class="err-card">⚠ Please enter a research topic before generating.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        pipeline_slot = st.empty()
        result_slot   = st.empty()

        try:
            state = {}

            # Step 0 – Research
            pipeline_slot.markdown(render_steps(0, 0), unsafe_allow_html=True)
            research_agent = build_research_agent()
            research_result = research_agent.invoke({
                "messages": [
                    ("user",
                     f"Conduct research on the following topic and provide key findings:\n\n{topic}\n\n"
                     "Focus on gathering relevant information, data, and insights that will help in "
                     "understanding the topic comprehensively. Provide a summary of the key findings "
                     "that can be used for deeper analysis.")
                ]
            })
            state["research_findings"] = research_result["messages"][-1].content

            # Step 1 – Reading
            pipeline_slot.markdown(render_steps(1, 1), unsafe_allow_html=True)
            reader_agent = build_reading_agent()
            reader_result = reader_agent.invoke({
                "messages": [
                    ("user",
                     f"Based on the following search results about the '{topic}' "
                     f"pick the most relevant URL and scrape it for deeper content.\n\n"
                     f"Search Results : {state['research_findings']}")
                ]
            })
            state["scraped_content"] = reader_result["messages"][-1].content

            result_combined = (
                f"SEARCH RESULT:\n{state['research_findings']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )

            # Step 2 – Writer
            pipeline_slot.markdown(render_steps(2, 2), unsafe_allow_html=True)
            writer_report = writer_chain.invoke({"topic": topic, "research": result_combined})
            state["report"] = writer_report

            # Step 3 – Critic
            pipeline_slot.markdown(render_steps(3, 3), unsafe_allow_html=True)
            critic_report = critic_chain.invoke({"topic": topic, "report": state["report"]})
            state["feedback"] = critic_report

            # All done
            pipeline_slot.markdown(render_steps(-1, 4), unsafe_allow_html=True)

            # Results
            result_slot.markdown(f"""
<div class="result-section">
    <div class="result-label">✍ Final Report</div>
    <div class="result-card report">{state["report"]}</div>

    <div style="margin-top:2rem"></div>

    <div class="result-label">🧠 Critic Feedback</div>
    <div class="result-card feedback">{state["feedback"]}</div>
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            pipeline_slot.empty()
            result_slot.markdown(
                f'<div class="err-card">⚠ Pipeline error: {e}</div>',
                unsafe_allow_html=True,
            )