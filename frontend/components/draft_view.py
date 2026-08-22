
import streamlit as st

from utils.i18n import t
from utils.state import go_to
from services.api_client import generate_draft


def _ensure_draft_loaded():

    if st.session_state.draft is None:

        lang = st.session_state.lang

        with st.spinner(
            t("analyzing", lang)
        ):

            draft = generate_draft(

                st.session_state.final_result,

                st.session_state.answers,

                lang,
            )

        # ------------------------------------------------------
        # Validate backend response
        # ------------------------------------------------------

        if not isinstance(
            draft,
            dict,
        ):

            raise ValueError(
                "Backend returned an invalid draft."
            )

        title = draft.get(
            "title",
            "NyayaPath Draft",
        )

        content = draft.get(
            "content",
            draft.get(
                "body",
                "",
            ),
        )

        if not content:

            raise ValueError(
                "The generated draft is empty."
            )

        # ------------------------------------------------------
        # Store normalized draft
        # ------------------------------------------------------

        st.session_state.draft = {

            "title": title,

            "content": content,

            "language": draft.get(
                "language",
                lang,
            ),
        }

        st.session_state.draft_edited_text = content


def render():

    lang = st.session_state.lang

    try:

        _ensure_draft_loaded()

    except Exception as error:

        st.error(
            f"Unable to generate draft: {error}"
        )

        if st.button(
            t("back", lang)
        ):

            go_to(
                "result"
            )

        return

    draft = st.session_state.draft

    # ----------------------------------------------------------
    # Header
    # ----------------------------------------------------------

    st.markdown(
        f"## {t('draft_heading', lang)}"
    )

    st.divider()

    title = draft.get(
        "title",
        "NyayaPath Draft",
    )

    st.markdown(
        f"##### {title}"
    )

    # ----------------------------------------------------------
    # Editable draft
    # ----------------------------------------------------------

    edited = st.text_area(

        label=t(
            "draft_heading",
            lang,
        ),

        value=st.session_state.draft_edited_text,

        height=380,

        label_visibility="collapsed",

        key="draft_text_area",
    )

    st.session_state.draft_edited_text = edited

    # ----------------------------------------------------------
    # Warning
    # ----------------------------------------------------------

    st.warning(
        f"⚠ {t('draft_warning', lang)}"
    )

    # ----------------------------------------------------------
    # Actions
    # ----------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    # ----------------------------------------------------------
    # Copy
    # ----------------------------------------------------------

    with col1:

        with st.popover(
            t("copy", lang),
            use_container_width=True,
        ):

            st.code(
                edited,
                language=None,
            )

    # ----------------------------------------------------------
    # Download
    # ----------------------------------------------------------

    with col2:

        st.download_button(

            label=t(
                "download",
                lang,
            ),

            data=edited.encode(
                "utf-8"
            ),

            file_name=(
                "nyayapath_draft.txt"
            ),

            mime="text/plain",

            use_container_width=True,
        )

    # ----------------------------------------------------------
    # Back
    # ----------------------------------------------------------

    with col3:

        if st.button(
            t("back", lang),
            use_container_width=True,
        ):

            go_to(
                "result"
            )

# import streamlit as st
# from utils.i18n import t
# from utils.state import go_to
# from services.api_client import generate_draft


# def _ensure_draft_loaded():
#     if st.session_state.draft is None:
#         lang = st.session_state.lang
#         with st.spinner(t("analyzing", lang)):
#             st.session_state.draft = generate_draft(
#                 st.session_state.final_result,
#                 st.session_state.answers,
#                 lang,
#             )
#         st.session_state.draft_edited_text = st.session_state.draft["body"]


# def render():
#     lang = st.session_state.lang
#     _ensure_draft_loaded()
#     draft = st.session_state.draft

#     st.markdown(f"## {t('draft_heading', lang)}")
#     st.divider()
#     st.markdown(f"##### {draft['title']}")

#     # MVP scope note (from the spec): Edit + Copy matter more than a rich
#     # document editor. A plain editable text_area covers both cheaply.
#     edited = st.text_area(
#         label=t("draft_heading", lang),
#         value=st.session_state.draft_edited_text,
#         height=380,
#         label_visibility="collapsed",
#         key="draft_text_area",
#     )
#     st.session_state.draft_edited_text = edited

#     st.warning(f"⚠ {t('draft_warning', lang)}")

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         # True "copy to clipboard" needs a JS component; st.code gives users
#         # a built-in copy icon for free as a fast MVP stand-in.
#         with st.popover(t("copy", lang), use_container_width=True):
#             st.code(edited, language=None)
#     with col2:
#         st.download_button(
#             label=t("download", lang),
#             data=edited.encode("utf-8"),
#             file_name="nyayapath_draft.txt",
#             mime="text/plain",
#             use_container_width=True,
#         )
#         st.caption("PDF export: swap for the ReportLab-generated file from /generate-draft once ready.")
#     with col3:
#         if st.button(t("back", lang), use_container_width=True):
#             go_to("result")
