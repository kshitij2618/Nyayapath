import streamlit as st
from utils.i18n import t
from utils.state import go_to


def render():
    lang = st.session_state.lang

    st.markdown(f"## {t('anything_else_heading', lang)}")
    st.caption(t("anything_else_subheading", lang))
    st.divider()

    extra = st.text_area(
        label=t("anything_else_heading", lang),
        value=st.session_state.extra_info,
        height=140,
        label_visibility="collapsed",
        key="extra_info_input",
    )
    st.session_state.extra_info = extra  # optional — empty is fine, no validation

    if st.button(t("continue_final", lang), type="primary"):
        go_to("result")
