import streamlit as st

from utils.state import init_state
from utils.i18n import t
from utils.theme import inject_theme, render_header, render_stepper
from components import (
    input_form,
    advice_view,
    question_view,
    anything_else_view,
    result_view,
    draft_view,
)

st.set_page_config(page_title="NyayaPath", page_icon="⚖", layout="centered")
init_state()
inject_theme()
lang = st.session_state.lang


# ---------------------------------------------------------------------------
# HEADER — deliberately minimal in *content* per the spec (no login/profile/
# etc.), but visually distinct: a gradient letterhead-style banner plus the
# real product pipeline as a progress stepper.
# ---------------------------------------------------------------------------
render_header(t("app_title", lang), t("app_subtitle", lang))

_, lang_col = st.columns([3, 1])
with lang_col:
    selected_lang = st.selectbox(
        "Language",
        options=["en", "hi"],
        format_func=lambda code: "English" if code == "en" else "हिंदी",
        index=["en", "hi"].index(st.session_state.lang),
        label_visibility="collapsed",
    )
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

render_stepper(st.session_state.stage)


# ---------------------------------------------------------------------------
# STAGE ROUTER — mirrors the flow diagram exactly:
# input -> advice -> [questions -> anything_else] -> result -> draft
# ---------------------------------------------------------------------------
STAGE_RENDERERS = {
    "input": input_form.render,
    "advice": advice_view.render,
    "questions": question_view.render,
    "anything_else": anything_else_view.render,
    "result": result_view.render,
    "draft": draft_view.render,
}

STAGE_RENDERERS[st.session_state.stage]()


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
st.divider()
st.caption(f"**{t('app_title', lang)}** — {t('footer_tag', lang)}")
st.caption("Sources · About · GitHub")