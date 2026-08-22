import streamlit as st

from utils.i18n import t
from utils.state import go_to, reset_all
from services.api_client import get_final_result


# ============================================================
# LOAD FINAL RESULT
# ============================================================

def _ensure_result_loaded():

    if st.session_state.final_result is None:

        lang = st.session_state.lang

        with st.spinner(
            t("analyzing", lang)
        ):

            st.session_state.final_result = get_final_result(
                st.session_state.problem_text,
                st.session_state.analysis,
                st.session_state.answers,
                st.session_state.extra_info,
                lang,
            )


# ============================================================
# RENDER RESULT
# ============================================================

def render():

    lang = st.session_state.lang

    _ensure_result_loaded()

    result = st.session_state.final_result

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not isinstance(result, dict):

        st.error(
            "The backend returned an invalid result."
        )

        return

    # --------------------------------------------------------
    # BACKEND ERROR CHECK
    # --------------------------------------------------------

    if result.get("success") is False:

        st.error(
            result.get(
                "detail",
                "Unable to generate the final result."
            )
        )

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        f"## {t('result_heading', lang)}"
    )

    st.divider()

    # ========================================================
    # WHAT WE UNDERSTAND
    # ========================================================

    with st.container(border=True):

        st.markdown(
            f"**{t('sec_understand', lang)}**"
        )

        category = result.get(
            "category",
            "General civic issue",
        )

        intent = result.get(
            "intent",
            "",
        )

        initial_advice = result.get(
            "initial_advice",
            "",
        )

        st.markdown(
            f"##### {category}"
        )

        if intent:

            st.caption(
                f"Intent: {intent}"
            )

        if initial_advice:

            st.write(
                initial_advice
            )

    # ========================================================
    # SUPPORTED / WORKFLOW
    # ========================================================

    workflow = result.get(
        "workflow"
    )

    supported = result.get(
        "supported",
        True,
    )

    if workflow or not supported:

        with st.container(border=True):

            if workflow:

                st.markdown(
                    f"**Workflow:** {workflow}"
                )

            if not supported:

                st.warning(
                    "This issue is not currently supported "
                    "by a dedicated NyayaPath workflow."
                )

    # ========================================================
    # LEGAL SUPPORT
    # ========================================================

    legal_support = result.get(
        "legal_support",
        [],
    )

    if legal_support:

        with st.container(border=True):

            st.markdown(
                f"**⚖ {t('sec_laws', lang)}**"
            )

            for law in legal_support:

                if not isinstance(
                    law,
                    dict,
                ):
                    continue

                title = law.get(
                    "title",
                    "Legal support",
                )

                description = law.get(
                    "description",
                    "",
                )

                law_type = law.get(
                    "type"
                )

                url = law.get(
                    "url"
                )

                st.markdown(
                    f"**{title}**"
                )

                if description:

                    st.write(
                        description
                    )

                if law_type:

                    st.caption(
                        f"Type: {law_type}"
                    )

                if law.get(
                    "verify_before_use",
                    True,
                ):

                    st.caption(
                        "Please verify the current applicable "
                        "law before relying on it."
                    )

                if url:

                    st.link_button(
                        t(
                            "official_source",
                            lang,
                        ),
                        url,
                    )

    # ========================================================
    # WHAT YOU SHOULD DO
    # ========================================================

    action_plan = result.get(
        "action_plan",
        [],
    )

    if action_plan:

        with st.container(border=True):

            st.markdown(
                f"**🧭 {t('sec_actions', lang)}**"
            )

            for i, action in enumerate(
                action_plan,
                start=1,
            ):

                st.write(
                    f"{i}. {action}"
                )

    # ========================================================
    # DOCUMENTS
    # ========================================================

    documents = result.get(
        "documents",
        [],
    )

    if documents:

        with st.container(border=True):

            st.markdown(
                "📄 **Documents you may need**"
            )

            for document in documents:

                if not isinstance(
                    document,
                    dict,
                ):
                    continue

                name = document.get(
                    "name",
                    "Document",
                )

                required = document.get(
                    "required",
                    False,
                )

                if required:

                    st.write(
                        f"☑ {name} — Required"
                    )

                else:

                    st.write(
                        f"☐ {name}"
                    )

    # ========================================================
    # EVIDENCE
    # ========================================================

    evidence = result.get(
        "evidence",
        [],
    )

    if evidence:

        with st.container(border=True):

            st.markdown(
                f"**📁 {t('sec_evidence', lang)}**"
            )

            for i, item in enumerate(
                evidence
            ):

                st.checkbox(
                    item,
                    key=f"evidence_{i}",
                )

    # ========================================================
    # ESCALATION
    # ========================================================

    escalation = result.get(
        "escalation"
    )

    if escalation:

        with st.container(border=True):

            st.markdown(
                f"**{t('sec_escalation', lang)}**"
            )

            if isinstance(
                escalation,
                dict,
            ):

                appropriate = escalation.get(
                    "appropriate",
                    False,
                )

                reason = escalation.get(
                    "reason",
                    "",
                )

                authorities = escalation.get(
                    "authorities",
                    [],
                )

                if reason:

                    if appropriate:

                        st.write(
                            reason
                        )

                    else:

                        st.write(
                            reason
                        )

                if authorities:

                    st.markdown(
                        "**Relevant authority:**"
                    )

                    for authority in authorities:

                        if not isinstance(
                            authority,
                            dict,
                        ):
                            continue

                        name = authority.get(
                            "name",
                            "Authority",
                        )

                        role = authority.get(
                            "role"
                        )

                        jurisdiction = authority.get(
                            "jurisdiction"
                        )

                        st.markdown(
                            f"**{name}**"
                        )

                        if role:

                            st.caption(
                                role
                            )

                        if jurisdiction:

                            st.caption(
                                f"Jurisdiction: "
                                f"{jurisdiction}"
                            )

            else:

                # Backwards compatibility
                st.write(
                    escalation
                )

    # ========================================================
    # FINAL RECOMMENDATION
    # ========================================================

    final_recommendation = result.get(
        "final_recommendation"
    )

    if final_recommendation:

        with st.container(border=True):

            st.markdown(
                "**📌 Final recommendation**"
            )

            if isinstance(
                final_recommendation,
                dict,
            ):

                workflow_name = final_recommendation.get(
                    "workflow_name"
                )

                if workflow_name:

                    st.markdown(
                        f"**{workflow_name}**"
                    )

                recommendation_advice = (
                    final_recommendation.get(
                        "action_plan",
                        [],
                    )
                )

                if recommendation_advice:

                    for i, action in enumerate(
                        recommendation_advice,
                        start=1,
                    ):

                        st.write(
                            f"{i}. {action}"
                        )

                recommendation_documents = (
                    final_recommendation.get(
                        "documents",
                        [],
                    )
                )

                if recommendation_documents:

                    st.markdown(
                        "**Documents:**"
                    )

                    for document in recommendation_documents:

                        if isinstance(
                            document,
                            dict,
                        ):

                            name = document.get(
                                "name",
                                "Document",
                            )

                            st.write(
                                f"• {name}"
                            )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    disclaimer = result.get(
        "disclaimer"
    )

    if disclaimer:

        with st.container(border=True):

            st.caption(
                f"⚠️ {disclaimer}"
            )

    # ========================================================
    # SOURCES
    # ========================================================

    sources = result.get(
        "sources",
        [],
    )

    if sources:

        with st.container(border=True):

            st.markdown(
                f"**🔗 {t('sec_sources', lang)}**"
            )

            for source in sources:

                if not isinstance(
                    source,
                    dict,
                ):
                    continue

                title = source.get(
                    "title",
                    "Source",
                )

                description = source.get(
                    "description",
                    "",
                )

                url = source.get(
                    "url"
                )

                if description:

                    st.write(
                        description
                    )

                if url:

                    st.link_button(
                        title,
                        url,
                    )

                else:

                    st.write(
                        title
                    )

    # ========================================================
    # DOCUMENT / DRAFT
    # ========================================================

    # IMPORTANT:
    # Only show the draft button when the backend actually
    # indicates that a workflow/document can produce a draft.
    #
    # For now, documents merely means documents are required.
    # Therefore we use workflow as the signal that the workflow
    # can potentially generate a draft.

    draft_workflow = workflow

    if draft_workflow:

        with st.container(border=True):

            st.markdown(
                "📝 **Generate a document**"
            )

            st.write(
                "A formal document may be generated "
                "for this workflow."
            )

            if st.button(
                "View / Generate Draft",
                type="primary",
            ):

                go_to(
                    "draft"
                )

    # ========================================================
    # START OVER
    # ========================================================

    st.divider()

    if st.button(
        t(
            "start_over",
            lang,
        )
    ):

        reset_all()