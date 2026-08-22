import streamlit as st
from utils.i18n import t
from utils.state import go_to


def render():
    lang = st.session_state.lang
    analysis = st.session_state.analysis

    st.markdown(f"## {t('advice_heading', lang)}")
    st.divider()

    st.markdown(f"**{t('what_we_understand', lang)}**")
    st.write(analysis["summary"])

    st.divider()
    st.markdown(f"**{t('relevant_support', lang)}**")
    if analysis.get("laws_found"):
        st.write(analysis["laws_preview"])
        with st.expander(t("view_rules", lang)):
            st.write(analysis["laws_preview"])
    else:
        # Rule from the spec: never fabricate a law if none can be confidently identified.
        st.info(t("no_law_found", lang))

    st.divider()
    st.markdown(f"**{t('initial_advice', lang)}**")
    st.write(analysis["initial_advice"])

    st.divider()
    st.write(t("more_info_prompt", lang))

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("yes_more_info", lang), use_container_width=True):
            go_to("questions")
    with col2:
        if st.button(t("continue", lang), type="primary", use_container_width=True):
            go_to("result")
