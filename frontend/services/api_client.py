"""
Single integration point between the Streamlit frontend and Member 1's
FastAPI backend.

The frontend should import functions from this file only.

Backend endpoints:
    POST /analyze
    POST /final-result
    POST /generate-draft

Backend URL:
    http://localhost:8000
"""

import os
import time
import requests


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

USE_MOCK = False

BACKEND_URL = os.environ.get(
    "NYAYAPATH_BACKEND_URL",
    "http://localhost:8000"
)

REQUEST_TIMEOUT = 15


# --------------------------------------------------------------------------
# HTTP helper
# --------------------------------------------------------------------------

def _post(path: str, payload: dict) -> dict:
    """
    Send a POST request to Member 1's FastAPI backend.
    """
    response = requests.post(
        f"{BACKEND_URL}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------------------------------
# Mock category detection
# --------------------------------------------------------------------------

def _mock_detect_category(text: str) -> str:
    text = text.lower()

    if any(
        word in text
        for word in [
            "deposit",
            "landlord",
            "rent",
            "tenant",
            "eviction",
            "किराया",
            "मकान मालिक",
        ]
    ):
        return "tenant_deposit"

    if any(
        word in text
        for word in [
            "rti",
            "information",
            "right to information",
            "सूचना का अधिकार",
        ]
    ):
        return "rti"

    return "generic_civic"


# --------------------------------------------------------------------------
# Normalize analysis returned by backend
# --------------------------------------------------------------------------

def _normalize_analysis(data: dict, problem_text: str) -> dict:
    """
    Convert Member 1's backend response into the fields expected by
    the Streamlit frontend.
    """

    legal_support = data.get("legal_support") or []

    laws_preview = ""

    if legal_support:
        laws_preview = "\n\n".join(
            str(item)
            for item in legal_support
        )

    return {
        **data,

        # Fields expected by advice_view.py
        "summary": (
            f"This appears to be a "
            f"{data.get('category', 'legal')} issue "
            f"concerning "
            f"{data.get('intent', 'the matter described')}."
        ),

        "laws_found": bool(legal_support),

        "laws_preview": laws_preview,

        "initial_advice": data.get(
            "initial_advice",
            "Please provide more information for a more accurate analysis."
        ),
    }


# --------------------------------------------------------------------------
# 1. Initial analysis
# Landing screen -> advice screen
# --------------------------------------------------------------------------

def analyze_problem(
    problem_text: str,
    lang: str = "en"
) -> dict:

    payload = {
        "message": problem_text,
        "language": lang,
        "answers": {},
        "anything_else": "",
        "skip_follow_up": False,
    }

    # ----------------------------------------------------------------------
    # REAL BACKEND
    # ----------------------------------------------------------------------

    if not USE_MOCK:
        try:
            data = _post(
                "/analyze",
                payload
            )

            return _normalize_analysis(
                data,
                problem_text
            )

        except requests.RequestException as error:
            print(f"Backend /analyze failed: {error}")

            # Fall back to mock so the frontend does not crash.
            pass

    # ----------------------------------------------------------------------
    # MOCK BACKEND
    # ----------------------------------------------------------------------

    time.sleep(0.6)

    category = _mock_detect_category(problem_text)

    if category == "tenant_deposit":

        return {
            "category": "tenant_deposit",
            "intent": "obtain refund of security deposit",
            "language": lang,

            "summary": (
                "This appears to be a tenant/security deposit issue "
                "concerning recovery of a security deposit."
            ),

            "laws_found": True,

            "laws_preview": (
                "State tenancy and rent-control rules may regulate "
                "the return and lawful deduction of security deposits."
            ),

            "initial_advice": (
                "Please check your tenancy agreement and keep proof "
                "of the security deposit payment. You should make a "
                "written request to the landlord for the return of "
                "the deposit and keep records of all communication."
            ),

            "legal_support": [
                {
                    "name": "State Tenancy / Rent Control Rules",
                    "explanation": (
                        "Tenancy laws may regulate security deposits "
                        "and deductions made by landlords."
                    ),
                }
            ],
        }

    if category == "rti":

        return {
            "category": "rti",
            "intent": "obtain information under the RTI Act",
            "language": lang,

            "summary": (
                "This appears to be an RTI issue concerning "
                "obtaining information from a public authority."
            ),

            "laws_found": True,

            "laws_preview": (
                "The Right to Information Act, 2005 provides a "
                "framework for citizens to request information "
                "from public authorities."
            ),

            "initial_advice": (
                "You may consider submitting a clear RTI application "
                "to the appropriate Public Information Officer (PIO). "
                "Keep a copy of the application and proof of submission."
            ),

            "legal_support": [
                {
                    "name": "Right to Information Act, 2005",
                    "explanation": (
                        "The Act provides citizens a statutory mechanism "
                        "to seek information from public authorities."
                    ),
                }
            ],
        }

    return {
        "category": "generic_civic",
        "intent": "resolve a civic issue",
        "language": lang,

        "summary": (
            "This appears to be a general civic issue "
            "requiring further information."
        ),

        "laws_found": False,

        "laws_preview": "",

        "initial_advice": (
            "Please provide more information about the issue, "
            "including the location, people or authorities involved, "
            "and when the issue occurred."
        ),

        "legal_support": [],
    }


# --------------------------------------------------------------------------
# 2. Follow-up questions
# question_view.py
# --------------------------------------------------------------------------

def get_followup_questions(
    analysis: dict,
    lang: str = "en"
) -> list:

    category = analysis.get(
        "category",
        "generic_civic"
    )

    question_bank = {

        "tenant_deposit": [

            {
                "id": "move_out_date",
                "text": "When did you move out?"
            },

            {
                "id": "property_location",
                "text": (
                    "Where is the property located "
                    "(city/state)?"
                )
            },

            {
                "id": "agreement_mentions_deposit",
                "text": (
                    "Does your tenancy agreement mention "
                    "the security deposit?"
                )
            },

            {
                "id": "deposit_amount",
                "text": "How much was the security deposit?"
            },
        ],

        "rti": [

            {
                "id": "authority",
                "text": (
                    "Which government department or authority "
                    "does this concern?"
                )
            },

            {
                "id": "info_sought",
                "text": (
                    "What specific information are you requesting?"
                )
            },

            {
                "id": "prior_request",
                "text": (
                    "Have you already made any request or complaint "
                    "about this?"
                )
            },
        ],

        "generic_civic": [

            {
                "id": "location",
                "text": (
                    "Where is this issue taking place "
                    "(city/state)?"
                )
            },

            {
                "id": "parties_involved",
                "text": (
                    "Who else is involved "
                    "(person, company, or authority)?"
                )
            },

            {
                "id": "timeline",
                "text": (
                    "When did this issue start?"
                )
            },
        ],
    }

    return question_bank.get(
        category,
        question_bank["generic_civic"]
    )


# --------------------------------------------------------------------------
# 3. Final structured result
# result_view.py
# --------------------------------------------------------------------------
def get_final_result(
    problem_text: str,
    analysis: dict,
    answers: dict,
    extra_info: str,
    lang: str = "en",
) -> dict:

    if not USE_MOCK:

        try:

            # --------------------------------------------------
            # Build payload expected by backend
            # --------------------------------------------------

            payload = {
                "category": analysis.get(
                    "category",
                    "",
                ),

                "intent": analysis.get(
                    "intent",
                    "",
                ),

                "message": problem_text,

                "language": analysis.get(
                    "language",
                    lang,
                ),

                "answers": answers or {},

                "initial_advice": analysis.get(
                    "initial_advice",
                    "",
                ),

                "missing_information": analysis.get(
                    "missing_information",
                    [],
                ),
            }

            # --------------------------------------------------
            # Add optional information to message
            # --------------------------------------------------

            if extra_info:
                payload["message"] = (
                    problem_text
                    + "\n\nAdditional information:\n"
                    + extra_info
                )

            print("\n========== SENDING FINAL RESULT ==========")
            print(payload)
            print("==========================================")

            return _post(
                "/final-result",
                payload,
            )

        except requests.RequestException as error:

            print(
                f"Backend /final-result failed: {error}"
            )

            raise

    # ----------------------------------------------------------
    # MOCK RESULT
    # ----------------------------------------------------------

    time.sleep(0.8)

    category = analysis.get(
        "category",
        "generic_civic",
    )

    # ----------------------------------------------------------
    # TENANT DEPOSIT
    # ----------------------------------------------------------

    if category == "tenant_deposit":

        return {
            "category": "tenant_deposit",

            "understand": {
                "title": "Tenant / Security Deposit Issue",

                "detail": (
                    f"You moved out on "
                    f"{answers.get('move_out_date', 'the reported date')} "
                    "and your security deposit has not been returned."
                ),
            },

            "laws": [],

            "actions": [
                "Gather your tenancy agreement and deposit payment proof.",
                "Keep written records of communication with the landlord.",
                "Send a formal written request for refund.",
            ],

            "evidence": [
                "Tenancy agreement",
                "Deposit payment proof",
                "Move-out proof",
                "Communication with landlord",
            ],

            "escalation": (
                "If the landlord does not respond, consider "
                "approaching the appropriate local authority."
            ),

            "document": {
                "available": True,
                "reason": (
                    "A formal notice may be appropriate."
                ),
                "doc_type": "deposit_refund_notice",
            },

            "sources": [],
        }

    # ----------------------------------------------------------
    # RTI
    # ----------------------------------------------------------

    if category == "rti":

        return {
            "category": "rti",

            "understand": {
                "title": "Right to Information Request",

                "detail": (
                    "You want to obtain information from "
                    "a public authority."
                ),
            },

            "laws": [],

            "actions": [
                "Identify the relevant Public Information Officer.",
                "Prepare a clear RTI application.",
                "Submit the application through the appropriate channel.",
            ],

            "evidence": [],

            "escalation": (
                "If the RTI request is not answered appropriately, "
                "you may consider the applicable appeal process."
            ),

            "document": {
                "available": True,
                "reason": "An RTI application draft may be appropriate.",
                "doc_type": "rti_application",
            },

            "sources": [],
        }

    # ----------------------------------------------------------
    # GENERIC
    # ----------------------------------------------------------

    return {
        "category": "generic_civic",

        "understand": {
            "title": "Civic Issue",
            "detail": problem_text[:200],
        },

        "laws": [],

        "actions": [
            "Identify the authority responsible for the issue.",
            "File a complaint through the appropriate grievance portal.",
            "Keep the complaint reference number.",
        ],

        "evidence": [],

        "escalation": None,

        "document": {
            "available": False,
            "reason": None,
            "doc_type": None,
        },

        "sources": [],
    }


# --------------------------------------------------------------------------
# 4. Generate draft document
# draft_view.py
# --------------------------------------------------------------------------

# def generate_draft(
#     final_result: dict,
#     answers: dict,
#     lang: str = "en"
# ) -> dict:

#     # ----------------------------------------------------------------------
#     # REAL BACKEND
#     # ----------------------------------------------------------------------

#     if not USE_MOCK:

#         try:

#             return _post(
#                 "/generate-draft",
#                 {
#                     "final_result": final_result,
#                     "answers": answers,
#                     "lang": lang,
#                 }
#             )

#         except requests.RequestException as error:

#             print(
#                 f"Backend /generate-draft failed: {error}"
#             )

#             # Fall back to mock.
#             pass

#     # ----------------------------------------------------------------------
#     # MOCK DRAFT
#     # ----------------------------------------------------------------------

#     time.sleep(0.6)

#     doc_type = (
#         final_result.get("document") or {}
#     ).get("doc_type")

#     # ----------------------------------------------------------------------
#     # SECURITY DEPOSIT NOTICE
#     # ----------------------------------------------------------------------

#     if doc_type == "deposit_refund_notice":

#         title = "NOTICE REGARDING SECURITY DEPOSIT REFUND"

#         body = (
#             "To,\n"
#             "[Landlord Name]\n"
#             "[Landlord Address]\n\n"

#             "Subject: Request for refund of security deposit\n\n"

#             "Dear [Landlord Name],\n\n"

#             f"I vacated the above-mentioned rented premises on "
#             f"{answers.get('move_out_date', '[move-out date]')}. "

#             f"As per our tenancy agreement, a security deposit of "
#             f"{answers.get('deposit_amount', '[amount]')} was paid "
#             "at the commencement of the tenancy. "

#             "To date, this deposit has not been refunded despite "
#             "the property being vacated in good condition.\n\n"

#             "I request that the deposit be refunded within 15 days "
#             "of this notice, failing which I will be compelled to "
#             "escalate this matter to the appropriate rent authority "
#             "or consumer forum.\n\n"

#             "Sincerely,\n"
#             "[Your Name]\n"
#             "[Your Contact Information]"
#         )

#     # ----------------------------------------------------------------------
#     # RTI APPLICATION
#     # ----------------------------------------------------------------------

#     elif doc_type == "rti_application":

#         title = (
#             "APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005"
#         )

#         body = (
#             "To,\n"
#             "The Public Information Officer,\n"
#             f"{answers.get('authority', '[Department Name]')}\n\n"

#             "Subject: Request for information under the RTI Act, 2005\n\n"

#             "Sir/Madam,\n\n"

#             f"I would like to request the following information: "
#             f"{answers.get('info_sought', '[details of information sought]')}\n\n"

#             "I am enclosing the prescribed application fee. "
#             "Kindly provide the requested information within the "
#             "statutory period of 30 days.\n\n"

#             "Sincerely,\n"
#             "[Your Name]\n"
#             "[Your Address]\n"
#             "[Your Contact Information]"
#         )

#     # ----------------------------------------------------------------------
#     # NO DOCUMENT
#     # ----------------------------------------------------------------------

#     else:

#         title = "DRAFT DOCUMENT"

#         body = (
#             "No document template is applicable "
#             "for this category."
#         )

#     return {
#         "title": title,
#         "body": body,
#     }

# def generate_draft(
#     category: str,
#     information: dict,
#     lang: str = "en",
# ) -> dict:

#     if not USE_MOCK:

#         try:

#             payload = {
#                 "category": str(
#                     category or ""
#                 ).strip(),

#                 "information": (
#                     information
#                     if isinstance(
#                         information,
#                         dict,
#                     )
#                     else {}
#                 ),

#                 "language": lang,
#             }

#             # --------------------------------------------------
#             # DEBUG
#             # --------------------------------------------------

#             print(
#                 "\n========== SENDING GENERATE DRAFT =========="
#             )

#             print(payload)

#             print(
#                 "============================================\n"
#             )

#             # --------------------------------------------------
#             # Backend request
#             # --------------------------------------------------

#             response = _post(
#                 "/generate-draft",
#                 payload,
#             )

#             print(
#                 "\n========== GENERATE DRAFT RESPONSE =========="
#             )

#             print(response)

#             print(
#                 "============================================\n"
#             )

#             return response

#         except requests.HTTPError as error:

#             print(
#                 "\n========== GENERATE DRAFT HTTP ERROR =========="
#             )

#             print(
#                 "status =",
#                 error.response.status_code
#                 if error.response is not None
#                 else "unknown",
#             )

#             print(
#                 "response =",
#                 error.response.text
#                 if error.response is not None
#                 else str(error),
#             )

#             print(
#                 "===============================================\n"
#             )

#             raise

#         except requests.RequestException as error:

#             print(
#                 f"Backend /generate-draft failed: {error}"
#             )

#             raise

#     # ----------------------------------------------------------
#     # MOCK
#     # ----------------------------------------------------------

#     return {
#         "title": "Generated Legal Draft",

#         "content": (
#             "This is a temporary mock draft. "
#             "Connect the backend to generate the actual document."
#         ),

#         "language": lang,
#     }

def generate_draft(
    final_result: dict,
    answers: dict,
    lang: str = "en",
) -> dict:

    category = ""

    if isinstance(
        final_result,
        dict,
    ):

        category = final_result.get(
            "category",
            "",
        )

    # ----------------------------------------------------------
    # Build information for the draft
    # ----------------------------------------------------------

    information = {

        "category": category,

        "intent": (
            final_result.get(
                "intent",
                "",
            )
            if isinstance(
                final_result,
                dict,
            )
            else ""
        ),

        "message": (
            final_result.get(
                "message",
                "",
            )
            if isinstance(
                final_result,
                dict,
            )
            else ""
        ),

        "initial_advice": (
            final_result.get(
                "initial_advice",
                "",
            )
            if isinstance(
                final_result,
                dict,
            )
            else ""
        ),

        "answers": (
            answers
            if isinstance(
                answers,
                dict,
            )
            else {}
        ),

        "legal_support": (
            final_result.get(
                "legal_support",
                [],
            )
            if isinstance(
                final_result,
                dict,
            )
            else []
        ),

        "documents": (
            final_result.get(
                "documents",
                [],
            )
            if isinstance(
                final_result,
                dict,
            )
            else []
        ),

        "evidence": (
            final_result.get(
                "evidence",
                [],
            )
            if isinstance(
                final_result,
                dict,
            )
            else []
        ),

        "action_plan": (
            final_result.get(
                "action_plan",
                [],
            )
            if isinstance(
                final_result,
                dict,
            )
            else []
        ),

        "escalation": (
            final_result.get(
                "escalation",
                {},
            )
            if isinstance(
                final_result,
                dict,
            )
            else {}
        ),

        "sources": (
            final_result.get(
                "sources",
                [],
            )
            if isinstance(
                final_result,
                dict,
            )
            else []
        ),
    }

    # ----------------------------------------------------------
    # Validation before sending
    # ----------------------------------------------------------

    if not category:

        raise ValueError(
            "Cannot generate draft: category is missing "
            "from the final result."
        )

    payload = {

        "category": category,

        "information": information,

        "language": lang,
    }

    print()
    print("========== SENDING GENERATE DRAFT ==========")
    print(payload)
    print("=============================================")

    try:

        response = _post(
            "/generate-draft",
            payload,
        )

        if not isinstance(
            response,
            dict,
        ):

            raise ValueError(
                "Backend returned an invalid draft response."
            )

        # ------------------------------------------------------
        # Normalize content/body difference
        # ------------------------------------------------------

        if "content" not in response:

            response["content"] = response.get(
                "body",
                "",
            )

        if "title" not in response:

            response["title"] = "NyayaPath Draft"

        if "language" not in response:

            response["language"] = lang

        return response

    except requests.RequestException as error:

        print(
            f"Backend /generate-draft failed: {error}"
        )

        raise