"""
Single integration point between the Streamlit frontend and Member 1's
FastAPI backend.

HOW TO USE THIS FILE
---------------------
1. While the backend doesn't exist yet (or is down), leave USE_MOCK = True.
   Every function below returns realistic, structured mock data so you can
   build and demo every screen independently.

2. Once Member 1's endpoints are live, set USE_MOCK = False (or export
   NYAYAPATH_USE_MOCK=0) and point BACKEND_URL at the real server. The
   function *signatures* are already what result_view.py / draft_view.py
   etc. expect, so no component code should need to change — only this file.

3. Each function still falls back to mock data if the real request fails,
   so a flaky backend during the demo doesn't crash the UI. Remove the
   try/except fallback once the backend is stable, if you'd rather fail
   loudly during testing.

EXPECTED BACKEND CONTRACT (confirm exact field names with Member 1)
---------------------------------------------------------------------
POST /analyze            {problem_text, lang} -> analysis dict (see mock below)
POST /followup            {problem_text, analysis, answers, extra_info, lang} -> analysis dict (refined)
POST /final-result        {problem_text, analysis, answers, extra_info, lang} -> final_result dict
POST /generate-draft      {final_result, lang} -> draft dict
"""

import os
import time
import requests

USE_MOCK = os.environ.get("NYAYAPATH_USE_MOCK", "1") == "1"
BACKEND_URL = os.environ.get("NYAYAPATH_BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 15  # seconds; local LLM inference can be slow


# --------------------------------------------------------------------------
# Category detection used ONLY by the mock layer, to fake something that
# looks like Gemma's classification. Delete this once the real backend
# is wired in — classification is Member 1's job, not the frontend's.
# --------------------------------------------------------------------------
def _mock_detect_category(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["deposit", "landlord", "rent", "tenant", "eviction", "किराया", "मकान मालिक"]):
        return "tenant_deposit"
    if any(w in text for w in ["rti", "information", "right to information", "सूचना का अधिकार"]):
        return "rti"
    return "generic_civic"


def _post(path: str, payload: dict) -> dict:
    resp = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# 1. Initial analysis (landing screen -> advice screen)
# --------------------------------------------------------------------------
def analyze_problem(problem_text: str, lang: str = "en") -> dict:
    if not USE_MOCK:
        try:
            return _post("/analyze", {"problem_text": problem_text, "lang": lang})
        except requests.RequestException:
            pass  # fall through to mock

    time.sleep(0.6)  # simulate inference latency for a realistic loading state
    category = _mock_detect_category(problem_text)

    mocks = {
        "tenant_deposit": {
            "category": "tenant_deposit",
            "category_label": "Landlord–Tenant Security Deposit Issue",
            "summary": "This appears to be a landlord–tenant security deposit issue.",
            "laws_found": True,
            "laws_preview": "There may be state-level rent control / tenancy rules relevant to the return of a security deposit. Exact applicability depends on your location, tenancy agreement and circumstances.",
            "initial_advice": "Check your tenancy agreement and keep records of your deposit payment and communication with the landlord.",
            "needs_more_info": True,
        },
        "rti": {
            "category": "rti",
            "category_label": "Right to Information (RTI) Request",
            "summary": "This appears to be a request for information from a government department.",
            "laws_found": True,
            "laws_preview": "The Right to Information Act, 2005 allows citizens to formally request information from public authorities within a defined timeframe.",
            "initial_advice": "Identify the specific public authority and the exact information you want — vague RTI requests are more likely to be rejected.",
            "needs_more_info": True,
        },
        "generic_civic": {
            "category": "generic_civic",
            "category_label": "Civic Issue",
            "summary": "We understand you're facing a civic issue, but need a little more detail to identify the right process.",
            "laws_found": False,
            "laws_preview": None,
            "initial_advice": "A few follow-up questions will help us narrow this down accurately.",
            "needs_more_info": True,
        },
    }
    return mocks[category]


# --------------------------------------------------------------------------
# 2. Follow-up questions (question_view.py)
#    Real backend should return >=3 relevant questions; mock mirrors that rule.
# --------------------------------------------------------------------------
def get_followup_questions(analysis: dict, lang: str = "en") -> list:
    category = analysis.get("category", "generic_civic")

    question_bank = {
        "tenant_deposit": [
            {"id": "move_out_date", "text": "When did you move out?"},
            {"id": "property_location", "text": "Where is the property located (city/state)?"},
            {"id": "agreement_mentions_deposit", "text": "Does your tenancy agreement mention the security deposit?"},
            {"id": "deposit_amount", "text": "How much was the security deposit?"},
        ],
        "rti": [
            {"id": "authority", "text": "Which government department or authority does this concern?"},
            {"id": "info_sought", "text": "What specific information are you requesting?"},
            {"id": "prior_request", "text": "Have you already made any request or complaint about this?"},
        ],
        "generic_civic": [
            {"id": "location", "text": "Where is this issue taking place (city/state)?"},
            {"id": "parties_involved", "text": "Who else is involved (person, company, or authority)?"},
            {"id": "timeline", "text": "When did this issue start?"},
        ],
    }
    return question_bank.get(category, question_bank["generic_civic"])


# --------------------------------------------------------------------------
# 3. Final structured result (result_view.py)
#    NOTE how sections are conditional — this is the core UX rule from the
#    layout spec: don't always render every card, only what's relevant.
# --------------------------------------------------------------------------
def get_final_result(problem_text: str, analysis: dict, answers: dict, extra_info: str, lang: str = "en") -> dict:
    if not USE_MOCK:
        try:
            return _post("/final-result", {
                "problem_text": problem_text,
                "analysis": analysis,
                "answers": answers,
                "extra_info": extra_info,
                "lang": lang,
            })
        except requests.RequestException:
            pass

    time.sleep(0.8)
    category = analysis.get("category", "generic_civic")

    if category == "tenant_deposit":
        return {
            "category": "tenant_deposit",
            "understand": {
                "title": "Tenant / Security Deposit Issue",
                "detail": f"You moved out on {answers.get('move_out_date', 'the reported date')} "
                          f"and your security deposit has not been returned.",
            },
            "laws": [{
                "name": "State Rent Control / Tenancy Rules — Security Deposit Return",
                "explanation": "Landlords are generally required to return the security deposit within a defined period after the tenant vacates, minus lawful deductions.",
                "application": "Based on what you've shared, your landlord may be past the permitted window to withhold your deposit without justification.",
                "source_url": "https://doorstep.delhi.gov.in/",
            }],
            "actions": [
                "Gather your tenancy agreement and deposit payment proof.",
                "Keep written records of all communication with the landlord.",
                "Send a formal written request for refund, with a clear deadline.",
                "Escalate to the rent authority or consumer forum if unresolved.",
            ],
            "evidence": ["Tenancy agreement", "Deposit payment proof", "Move-out proof / photos", "Communication with landlord"],
            "escalation": "If the landlord does not respond within 15 days of your written notice, you may approach the local Rent Authority or file a consumer complaint.",
            "document": {
                "available": True,
                "reason": "A formal notice may be appropriate in this situation.",
                "doc_type": "deposit_refund_notice",
            },
            "sources": [
                {"label": "State Tenancy / Rent Control Rules", "url": "https://doorstep.delhi.gov.in/"},
                {"label": "Consumer Grievance Portal", "url": "https://consumerhelpline.gov.in/"},
            ],
        }

    if category == "rti":
        return {
            "category": "rti",
            "understand": {
                "title": "Right to Information Request",
                "detail": f"You want information from {answers.get('authority', 'the relevant department')} "
                          f"regarding: {answers.get('info_sought', 'the matter described')}.",
            },
            "laws": [{
                "name": "Right to Information Act, 2005",
                "explanation": "Gives citizens the right to request information from public authorities, who must respond within 30 days (48 hours for life/liberty matters).",
                "application": "Your request appears to qualify as a standard RTI application to the relevant Public Information Officer (PIO).",
                "source_url": "https://rti.gov.in/",
            }],
            "actions": [
                "Identify the correct Public Information Officer (PIO) for the department.",
                "Draft a clear, specific RTI application (avoid vague requests).",
                "Pay the prescribed application fee (fee-exempt for BPL applicants).",
                "Track the 30-day response window.",
            ],
            "evidence": ["Any prior correspondence", "Proof of identity (if required by the authority)"],
            "escalation": "If no response is received within 30 days, or the response is unsatisfactory, you may file a First Appeal with the Appellate Authority.",
            "document": {
                "available": True,
                "reason": "An RTI application draft is appropriate here.",
                "doc_type": "rti_application",
            },
            "sources": [
                {"label": "RTI Online Portal", "url": "https://rti.gov.in/"},
            ],
        }

    # generic_civic — deliberately thinner result, no document section
    return {
        "category": "generic_civic",
        "understand": {
            "title": "Civic Issue",
            "detail": problem_text[:200],
        },
        "laws": [],
        "actions": [
            "Identify the specific local authority responsible for this issue.",
            "File a complaint through your municipal grievance portal if one exists.",
            "Keep a record of your complaint reference number.",
        ],
        "evidence": [],
        "escalation": None,
        "document": {"available": False, "reason": None, "doc_type": None},
        "sources": [],
    }


# --------------------------------------------------------------------------
# 4. Generated draft document (draft_view.py)
# --------------------------------------------------------------------------
def generate_draft(final_result: dict, answers: dict, lang: str = "en") -> dict:
    if not USE_MOCK:
        try:
            return _post("/generate-draft", {"final_result": final_result, "lang": lang})
        except requests.RequestException:
            pass

    time.sleep(0.6)
    doc_type = (final_result.get("document") or {}).get("doc_type")

    if doc_type == "deposit_refund_notice":
        title = "NOTICE REGARDING SECURITY DEPOSIT REFUND"
        body = (
            "To,\n[Landlord Name]\n[Landlord Address]\n\n"
            "Subject: Request for refund of security deposit\n\n"
            "Dear [Landlord Name],\n\n"
            f"I vacated the above-mentioned rented premises on {answers.get('move_out_date', '[move-out date]')}. "
            f"As per our tenancy agreement, a security deposit of {answers.get('deposit_amount', '[amount]')} was paid at the "
            "commencement of the tenancy. To date, this deposit has not been refunded despite the property being "
            "vacated in good condition.\n\n"
            "I request that the deposit be refunded within 15 days of this notice, failing which I will be compelled "
            "to escalate this matter to the appropriate rent authority or consumer forum.\n\n"
            "Sincerely,\n[Your Name]\n[Your Contact Information]"
        )
    elif doc_type == "rti_application":
        title = "APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005"
        body = (
            f"To,\nThe Public Information Officer,\n{answers.get('authority', '[Department Name]')}\n\n"
            "Subject: Request for information under the RTI Act, 2005\n\n"
            "Sir/Madam,\n\n"
            f"I would like to request the following information: {answers.get('info_sought', '[details of information sought]')}\n\n"
            "I am enclosing the prescribed application fee. Kindly provide the requested information within the "
            "statutory period of 30 days.\n\n"
            "Sincerely,\n[Your Name]\n[Your Address]\n[Your Contact Information]"
        )
    else:
        title = "DRAFT DOCUMENT"
        body = "No document template is applicable for this category."

    return {"title": title, "body": body}
