import streamlit as st
from utils.i18n import t
from utils.state import go_to
from services.api_client import generate_draft


def _ensure_draft_loaded():
    if st.session_state.draft is None:
        lang = st.session_state.lang
        with st.spinner(t("analyzing", lang)):
            st.session_state.draft = generate_draft(
                st.session_state.final_result,
                st.session_state.answers,
                lang,
            )
        st.session_state.draft_edited_text = st.session_state.draft["body"]


def render():
    lang = st.session_state.lang
    _ensure_draft_loaded()
    draft = st.session_state.draft

    st.markdown(f"## {t('draft_heading', lang)}")
    st.divider()
    st.markdown(f"##### {draft['title']}")

    # MVP scope note (from the spec): Edit + Copy matter more than a rich
    # document editor. A plain editable text_area covers both cheaply.
    edited = st.text_area(
        label=t("draft_heading", lang),
        value=st.session_state.draft_edited_text,
        height=380,
        label_visibility="collapsed",
        key="draft_text_area",
    )
    st.session_state.draft_edited_text = edited

    st.warning(f"⚠ {t('draft_warning', lang)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        # True "copy to clipboard" needs a JS component; st.code gives users
        # a built-in copy icon for free as a fast MVP stand-in.
        with st.popover(t("copy", lang), use_container_width=True):
            st.code(edited, language=None)
    with col2:
        st.download_button(
            label=t("download", lang),
            data=edited.encode("utf-8"),
            file_name="nyayapath_draft.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption("PDF export: swap for the ReportLab-generated file from /generate-draft once ready.")
    with col3:
        if st.button(t("back", lang), use_container_width=True):
            go_to("result")
