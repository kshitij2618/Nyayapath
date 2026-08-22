import streamlit as st
from utils.i18n import t
from utils.state import go_to
from services.api_client import analyze_problem

MAX_CHARS = 2000


def render():
    lang = st.session_state.lang

    st.markdown(f"### {t('input_heading', lang)}")
    st.caption(t("input_subheading", lang))

    text = st.text_area(
        label=t("input_heading", lang),
        value=st.session_state.problem_text,
        placeholder=t("input_placeholder", lang),
        height=160,
        max_chars=MAX_CHARS,
        label_visibility="collapsed",
        key="problem_text_input",
    )

    st.caption(f"{len(text)} / {MAX_CHARS}")

    disabled = len(text.strip()) == 0
    if st.button(t("input_button", lang), type="primary", disabled=disabled, use_container_width=False):
        st.session_state.problem_text = text.strip()
        with st.spinner(t("analyzing", lang)):
            st.session_state.analysis = analyze_problem(st.session_state.problem_text, lang)
        go_to("advice")
