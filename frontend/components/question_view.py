import streamlit as st
from utils.i18n import t
from utils.state import go_to
from services.api_client import get_followup_questions


def render():
    lang = st.session_state.lang

    st.markdown(f"## {t('questions_heading', lang)}")
    st.caption(t("questions_subheading", lang))
    st.divider()

    questions = get_followup_questions(st.session_state.analysis, lang)
    # Spec rule: at least 3 relevant questions, but never pad with filler ones.
    assert len(questions) >= 3, "Backend must return at least 3 relevant follow-up questions."

    for i, q in enumerate(questions, start=1):
        st.markdown(f"**Question {i}**")
        st.write(q["text"])
        answer = st.text_input(
            label=q["text"],
            value=st.session_state.answers.get(q["id"], ""),
            key=f"answer_{q['id']}",
            label_visibility="collapsed",
        )
        st.session_state.answers[q["id"]] = answer
        st.write("")

    if st.button(t("continue", lang), type="primary"):
        go_to("anything_else")
