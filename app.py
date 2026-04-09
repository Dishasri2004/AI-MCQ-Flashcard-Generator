from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.generator import build_learning_content
from src.pdf_utils import PDFExtractionError, extract_text_from_uploaded_pdfs
from src.performance import PerformanceStore

st.set_page_config(
    page_title="AI Quiz & Flashcard Generator",
    page_icon="📘",
    layout="wide",
)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

:root {
    --bg-1: #f8fbff;
    --bg-2: #eef5fb;
    --ink: #11243a;
    --ink-soft: #3b4e65;
    --accent: #0e7490;
    --accent-2: #f59e0b;
    --card: #ffffff;
    --border: #d9e4ef;
}

html, body, [class*="css"], .stApp, p, li, label, span, div {
    font-family: 'Outfit', sans-serif;
    color: var(--ink);
}

.stApp {
    background:
        radial-gradient(circle at 12% 14%, rgba(14, 116, 144, 0.16) 0, transparent 36%),
        radial-gradient(circle at 90% 8%, rgba(245, 158, 11, 0.18) 0, transparent 34%),
        linear-gradient(135deg, var(--bg-1), var(--bg-2));
}

.block-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.15rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 10px 28px rgba(17, 36, 58, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.block-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(17, 36, 58, 0.14);
}

.hero {
    background: linear-gradient(130deg, #155e75 0%, #0e7490 45%, #d97706 100%);
    border-radius: 20px;
    padding: 1.6rem;
    color: #ffffff;
    margin-bottom: 1.1rem;
    box-shadow: 0 16px 34px rgba(14, 30, 37, 0.24);
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    margin: 0;
    font-size: 2rem;
}

.hero p {
    margin: 0.4rem 0 0;
    opacity: 0.96;
}

.section-kicker {
    display: inline-block;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #155e75;
    background: #e6f3f7;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    margin-bottom: 0.45rem;
}

.metric-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.8rem;
}

.concept-pill {
    display: inline-block;
    margin: 0.2rem 0.3rem 0.2rem 0;
    padding: 0.35rem 0.55rem;
    border-radius: 999px;
    background: #ecfeff;
    border: 1px solid #bae6fd;
    color: #0c4a6e;
    font-size: 0.86rem;
    font-weight: 600;
}

.question-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-left: 6px solid #0e7490;
    border-radius: 14px;
    padding: 0.8rem 0.9rem;
    margin-bottom: 0.7rem;
}

.question-title {
    color: #0f172a;
    font-weight: 700;
    line-height: 1.45;
}

.flashcard-front {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 14px;
    padding: 1rem;
    color: #0f172a;
}

.flashcard-back {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 14px;
    padding: 1rem;
    color: #1f2937;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

.stButton button,
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #0e7490, #0369a1);
    color: #ffffff;
    border: 0;
    border-radius: 10px;
    padding: 0.54rem 0.9rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.2s ease;
}

.stButton button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    filter: brightness(1.03);
    box-shadow: 0 8px 18px rgba(3, 105, 161, 0.28);
}

.stButton button:focus,
div[data-testid="stFormSubmitButton"] button:focus {
    outline: 3px solid rgba(14, 116, 144, 0.35);
    outline-offset: 2px;
}

div[data-baseweb="radio"] label {
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 0.42rem 0.6rem;
    margin-bottom: 0.35rem;
    background: #ffffff;
    transition: background-color 0.18s ease, border-color 0.18s ease;
}

div[data-baseweb="radio"] label:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
}

div[data-baseweb="radio"] label:has(input:checked) {
    background: #e0f2fe;
    border-color: #0284c7;
    box-shadow: 0 0 0 1px #0284c7 inset;
}

div[data-baseweb="slider"] [role="slider"] {
    background: #0369a1;
}

div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #0e7490, #f59e0b) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

@media (max-width: 900px) {
    .hero h1 {
        font-size: 1.45rem;
    }

    .block-card {
        padding: 1rem;
    }
}
</style>
"""


def initialize_session_state() -> None:
    defaults = {
        "source_text": "",
        "mcqs": [],
        "flashcards": [],
        "concepts": [],
        "quiz_submitted": False,
        "quiz_score": 0,
        "flashcard_index": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>AI Quiz & Flashcard Generator</h1>
            <p>Upload study PDFs, auto-generate smart practice sets, and monitor your learning progress.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_and_generation() -> None:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-kicker">Build Content</span>', unsafe_allow_html=True)
    st.subheader("1) Upload PDFs & Generate Learning Content")

    files = st.file_uploader(
        "Upload one or more PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        question_count = st.slider("MCQ count", 5, 25, 10)
    with col2:
        flashcard_count = st.slider("Flashcard count", 5, 40, 15)

    if st.button("Generate Content", type="primary", use_container_width=True):
        if not files:
            st.warning("Please upload at least one PDF first.")
        else:
            with st.spinner("Reading documents and generating personalized learning sets..."):
                try:
                    text = extract_text_from_uploaded_pdfs(files)
                    mcqs, flashcards, concepts = build_learning_content(
                        text,
                        max_questions=question_count,
                        max_cards=flashcard_count,
                    )

                    st.session_state.source_text = text
                    st.session_state.mcqs = [q.to_dict() for q in mcqs]
                    st.session_state.flashcards = [c.to_dict() for c in flashcards]
                    st.session_state.concepts = concepts
                    st.session_state.quiz_submitted = False
                    st.session_state.flashcard_index = 0

                    st.success(
                        f"Generated {len(mcqs)} MCQs and {len(flashcards)} flashcards from your PDFs."
                    )
                except PDFExtractionError as exc:
                    st.error(str(exc))

    if st.session_state.concepts:
        st.markdown("#### Detected Key Concepts")
        concept_html = "".join(
            f'<span class="concept-pill">{c}</span>' for c in st.session_state.concepts[:20]
        )
        st.markdown(f"<div>{concept_html}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_quiz_tab(store: PerformanceStore) -> None:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-kicker">Practice Quiz</span>', unsafe_allow_html=True)
    st.subheader("2) Quiz Practice")

    if not st.session_state.mcqs:
        st.info("Generate learning content first to start quiz practice.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    with st.form("quiz_form"):
        responses = {}
        for idx, q in enumerate(st.session_state.mcqs, start=1):
            st.markdown(
                f'<div class="question-card"><div class="question-title">Q{idx}. {q["question"]}</div></div>',
                unsafe_allow_html=True,
            )
            responses[idx] = st.radio(
                label=f"Select answer for question {idx}",
                options=q["options"],
                key=f"q_{idx}",
                label_visibility="collapsed",
            )

        submitted = st.form_submit_button("Submit Quiz", type="primary")

    if submitted:
        score = 0
        for idx, q in enumerate(st.session_state.mcqs, start=1):
            if responses[idx] == q["correct_answer"]:
                score += 1

        total = len(st.session_state.mcqs)
        accuracy = (score / total) * 100 if total else 0
        st.session_state.quiz_submitted = True
        st.session_state.quiz_score = score

        store.add_attempt(score=score, total=total)

        st.success(f"Your score: {score}/{total} ({accuracy:.1f}%)")

        st.markdown("### Answer Review")
        for idx, q in enumerate(st.session_state.mcqs, start=1):
            selected = responses[idx]
            correct = q["correct_answer"]
            if selected == correct:
                st.markdown(f"Q{idx}: Correct")
            else:
                st.markdown(f"Q{idx}: Incorrect | Your answer: {selected} | Correct: {correct}")
            st.caption(q["explanation"])

    st.markdown("</div>", unsafe_allow_html=True)


def render_flashcard_tab() -> None:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-kicker">Active Recall</span>', unsafe_allow_html=True)
    st.subheader("3) Flashcard Review")

    if not st.session_state.flashcards:
        st.info("Generate learning content first to review flashcards.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    total = len(st.session_state.flashcards)
    idx = st.session_state.flashcard_index % total
    card = st.session_state.flashcards[idx]

    st.progress((idx + 1) / total)
    st.markdown(f"**Card {idx + 1} of {total}**")

    st.markdown(
        f'<div class="flashcard-front"><h4>Front</h4><p>{card["front"]}</p></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Reveal answer", expanded=False):
        st.markdown(
            f'<div class="flashcard-back"><h4>Back</h4><p>{card["back"]}</p></div>',
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", use_container_width=True):
            st.session_state.flashcard_index = (idx - 1) % total
            st.rerun()
    with col2:
        if st.button("Next", use_container_width=True):
            st.session_state.flashcard_index = (idx + 1) % total
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_performance_tab(store: PerformanceStore) -> None:
    st.markdown('<div class="block-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-kicker">Learning Analytics</span>', unsafe_allow_html=True)
    st.subheader("4) Performance Dashboard")

    summary = store.get_summary()
    attempts = store.get_attempts()

    c1, c2, c3 = st.columns(3)
    c1.metric("Quizzes Taken", summary["quizzes_taken"])
    c2.metric("Average Accuracy", f"{summary['avg_accuracy']}%")
    c3.metric("Best Accuracy", f"{summary['best_accuracy']}%")

    if attempts:
        df = pd.DataFrame(attempts)
        df["attempt_no"] = range(1, len(df) + 1)

        fig = px.line(
            df,
            x="attempt_no",
            y="accuracy",
            markers=True,
            title="Accuracy Trend by Quiz Attempt",
            labels={"attempt_no": "Attempt", "accuracy": "Accuracy (%)"},
        )
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df[["timestamp", "score", "total", "accuracy"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No attempts recorded yet. Submit a quiz to see analytics.")

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_session_state()
    store = PerformanceStore()

    render_header()

    with st.container(border=False):
        a, b, c = st.columns(3)
        a.markdown('<div class="metric-card"><strong>PDF to Practice</strong><br>Smart extraction and concept mapping.</div>', unsafe_allow_html=True)
        b.markdown('<div class="metric-card"><strong>Quiz + Flashcards</strong><br>Mixed retrieval pathways for better retention.</div>', unsafe_allow_html=True)
        c.markdown('<div class="metric-card"><strong>Track Progress</strong><br>Attempt history with accuracy trends.</div>', unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigate",
        [
            "Upload & Generate",
            "Quiz Practice",
            "Flashcards",
            "Performance",
        ],
    )

    if page == "Upload & Generate":
        render_upload_and_generation()
    elif page == "Quiz Practice":
        render_quiz_tab(store)
    elif page == "Flashcards":
        render_flashcard_tab()
    else:
        render_performance_tab(store)


if __name__ == "__main__":
    main()
