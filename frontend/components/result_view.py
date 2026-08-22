import streamlit as st
from utils.i18n import t
from utils.state import go_to, reset_all
from services.api_client import get_final_result


def _ensure_result_loaded():
    """Fetch the final result once and cache it — avoid re-calling the
    backend/mock on every Streamlit rerun (e.g. when the user just
    scrolls or expands something)."""
    if st.session_state.final_result is None:
        lang = st.session_state.lang
        with st.spinner(t("analyzing", lang)):
            st.session_state.final_result = get_final_result(
                st.session_state.problem_text,
                st.session_state.analysis,
                st.session_state.answers,
                st.session_state.extra_info,
                lang,
            )


def render():
    lang = st.session_state.lang
    _ensure_result_loaded()
    result = st.session_state.final_result

    st.markdown(f"## {t('result_heading', lang)}")
    st.divider()

    # --- WHAT WE UNDERSTAND (always shown) -------------------------------
    with st.container(border=True):
        st.markdown(f"**{t('sec_understand', lang)}**")
        st.markdown(f"##### {result['understand']['title']}")
        st.write(result["understand"]["detail"])

    # --- RELEVANT LAWS / RULES (conditional — only if any were found) ----
    if result.get("laws"):
        with st.container(border=True):
            st.markdown(f"**⚖ {t('sec_laws', lang)}**")
            for law in result["laws"]:
                st.markdown(f"**{law['name']}**")
                st.write(law["explanation"])
                st.caption(law["application"])
                if law.get("source_url"):
                    st.link_button(t("official_source", lang), law["source_url"])

    # --- WHAT YOU SHOULD DO (always shown) --------------------------------
    with st.container(border=True):
        st.markdown(f"**🧭 {t('sec_actions', lang)}**")
        for i, action in enumerate(result["actions"], start=1):
            st.write(f"{i}. {action}")

    # --- EVIDENCE (conditional) -------------------------------------------
    if result.get("evidence"):
        with st.container(border=True):
            st.markdown(f"**📁 {t('sec_evidence', lang)}**")
            for item in result["evidence"]:
                st.checkbox(item, key=f"evidence_{item}", value=False)

    # --- ESCALATION (conditional) ------------------------------------------
    if result.get("escalation"):
        with st.container(border=True):
            st.markdown(f"**{t('sec_escalation', lang)}**")
            st.write(result["escalation"])

    # --- DOCUMENT (conditional — only when a draft is applicable) --------
    doc = result.get("document") or {}
    if doc.get("available"):
        with st.container(border=True):
            st.markdown(f"**📝 {t('sec_document', lang)}**")
            st.write(doc["reason"])
            if st.button(t("view_draft", lang), type="primary"):
                go_to("draft")

    # --- SOURCES (conditional) ---------------------------------------------
    if result.get("sources"):
        with st.container(border=True):
            st.markdown(f"**🔗 {t('sec_sources', lang)}**")
            for src in result["sources"]:
                st.link_button(src["label"], src["url"])

    st.divider()
    if st.button(t("start_over", lang)):
        reset_all()
