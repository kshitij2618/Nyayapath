from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# ANALYZE REQUEST
# ============================================================

class AnalyzeRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
    )

    language: str = "en"

    answers: Dict[str, Any] = Field(
        default_factory=dict
    )

    anything_else: Optional[str] = None

    skip_follow_up: bool = False


# ============================================================
# FOLLOW-UP QUESTION
# ============================================================

class FollowUpQuestion(BaseModel):

    id: str

    text: str

    why_asked: Optional[str] = None

    field_type: str = "text"

    required: bool = False


# ============================================================
# LEGAL SUPPORT
# ============================================================

class LegalSupport(BaseModel):

    title: str

    description: Optional[str] = None

    type: Optional[str] = None

    url: Optional[str] = None

    verify_before_use: bool = True


# ============================================================
# DOCUMENT
# ============================================================

class DocumentRequirement(BaseModel):

    id: str

    name: str

    required: bool = False


# ============================================================
# AUTHORITY
# ============================================================

class AuthorityInfo(BaseModel):

    id: str

    name: str

    role: Optional[str] = None

    jurisdiction: Optional[str] = None


# ============================================================
# ESCALATION
# ============================================================

class EscalationInfo(BaseModel):

    appropriate: bool = False

    reason: Optional[str] = None

    authorities: List[AuthorityInfo] = Field(
        default_factory=list
    )


# ============================================================
# FINAL RECOMMENDATION
# ============================================================

class FinalRecommendation(BaseModel):

    workflow: Optional[str] = None

    workflow_name: Optional[str] = None

    legal_support: List[LegalSupport] = Field(
        default_factory=list
    )

    documents: List[DocumentRequirement] = Field(
        default_factory=list
    )

    authorities: List[AuthorityInfo] = Field(
        default_factory=list
    )

    action_plan: List[str] = Field(
        default_factory=list
    )

    evidence: List[str] = Field(
        default_factory=list
    )

    escalation: EscalationInfo = Field(
        default_factory=EscalationInfo
    )

    disclaimer: Optional[str] = None


# ============================================================
# ANALYZE RESPONSE
# ============================================================

class AnalyzeResponse(BaseModel):

    category: str

    intent: str

    language: str

    initial_advice: str = ""

    missing_information: List[str] = Field(
        default_factory=list
    )

    needs_more_information: bool = False

    can_skip_follow_up: bool = True

    skipped_follow_up: bool = False

    follow_up_questions: List[FollowUpQuestion] = Field(
        default_factory=list
    )

    workflow: Optional[str] = None

    supported: bool = True

    legal_support: List[LegalSupport] = Field(
        default_factory=list
    )

    documents: List[DocumentRequirement] = Field(
        default_factory=list
    )

    evidence: List[str] = Field(
        default_factory=list
    )

    action_plan: List[str] = Field(
        default_factory=list
    )

    escalation: EscalationInfo = Field(
        default_factory=EscalationInfo
    )

    sources: List[LegalSupport] = Field(
        default_factory=list
    )

    disclaimer: Optional[str] = None

    final_recommendation: FinalRecommendation = Field(
        default_factory=FinalRecommendation
    )


# ============================================================
# GENERATE DRAFT REQUEST
#
# ============================================================
# GENERATE DRAFT REQUEST
# ============================================================

class DraftRequest(BaseModel):

    category: str = Field(
        ...,
        min_length=1,
    )

    information: Dict[str, Any] = Field(
        default_factory=dict,
    )

    language: str = "en"


# ============================================================
# GENERATE DRAFT RESPONSE
# ============================================================

class DraftResponse(BaseModel):

    title: str

    content: str

    language: str


# from typing import Any, Dict, List, Optional

# from pydantic import BaseModel, Field


# # ============================================================
# # ANALYZE REQUEST
# # ============================================================

# class AnalyzeRequest(BaseModel):
#     message: str = Field(..., min_length=1)
#     language: str = "en"

#     answers: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     anything_else: Optional[str] = None

#     skip_follow_up: bool = False


# # ============================================================
# # FOLLOW-UP QUESTION
# # ============================================================

# class FollowUpQuestion(BaseModel):
#     id: str
#     text: str
#     why_asked: Optional[str] = None
#     field_type: str = "text"
#     required: bool = False


# # ============================================================
# # LEGAL SUPPORT
# # ============================================================

# class LegalSupport(BaseModel):
#     title: str

#     description: Optional[str] = None

#     type: Optional[str] = None

#     url: Optional[str] = None

#     verify_before_use: bool = True


# # ============================================================
# # DOCUMENT
# # ============================================================

# class DocumentRequirement(BaseModel):
#     id: str

#     name: str

#     required: bool = False

#     type: Optional[str] = None

#     applicable_when: Optional[Any] = None


# # ============================================================
# # AUTHORITY
# # ============================================================

# class AuthorityInfo(BaseModel):
#     id: str

#     name: str

#     role: Optional[str] = None

#     jurisdiction: Optional[str] = None


# # ============================================================
# # ESCALATION
# # ============================================================

# class EscalationInfo(BaseModel):
#     appropriate: bool = False

#     reason: Optional[str] = None

#     authorities: List[AuthorityInfo] = Field(
#         default_factory=list
#     )

#     steps: List[Dict[str, Any]] = Field(
#         default_factory=list
#     )


# # ============================================================
# # EVIDENCE
# # ============================================================

# class EvidenceItem(BaseModel):
#     id: str

#     name: str

#     description: Optional[str] = None

#     required: bool = False

#     type: Optional[str] = None

#     applicable_when: Optional[Any] = None


# # ============================================================
# # FINAL RECOMMENDATION
# # ============================================================

# class FinalRecommendation(BaseModel):
#     workflow: Optional[str] = None

#     workflow_name: Optional[str] = None

#     legal_support: List[LegalSupport] = Field(
#         default_factory=list
#     )

#     documents: List[DocumentRequirement] = Field(
#         default_factory=list
#     )

#     authorities: List[AuthorityInfo] = Field(
#         default_factory=list
#     )

#     action_plan: List[str] = Field(
#         default_factory=list
#     )

#     evidence: List[EvidenceItem] = Field(
#         default_factory=list
#     )

#     escalation: EscalationInfo = Field(
#         default_factory=EscalationInfo
#     )

#     sources: List[LegalSupport] = Field(
#         default_factory=list
#     )

#     disclaimer: Optional[str] = None


# # ============================================================
# # ANALYZE RESPONSE
# # ============================================================

# class AnalyzeResponse(BaseModel):

#     # --------------------------------------------------------
#     # Classification
#     # --------------------------------------------------------

#     category: str

#     intent: str

#     language: str

#     initial_advice: str = ""

#     missing_information: List[str] = Field(
#         default_factory=list
#     )

#     # --------------------------------------------------------
#     # Follow-up
#     # --------------------------------------------------------

#     needs_more_information: bool = False

#     can_skip_follow_up: bool = True

#     skipped_follow_up: bool = False

#     follow_up_questions: List[FollowUpQuestion] = Field(
#         default_factory=list
#     )

#     # --------------------------------------------------------
#     # Workflow
#     # --------------------------------------------------------

#     workflow: Optional[str] = None

#     supported: bool = True

#     # --------------------------------------------------------
#     # Legal / workflow result
#     # --------------------------------------------------------

#     legal_support: List[LegalSupport] = Field(
#         default_factory=list
#     )

#     documents: List[DocumentRequirement] = Field(
#         default_factory=list
#     )

#     evidence: List[EvidenceItem] = Field(
#         default_factory=list
#     )

#     action_plan: List[str] = Field(
#         default_factory=list
#     )

#     escalation: EscalationInfo = Field(
#         default_factory=EscalationInfo
#     )

#     sources: List[LegalSupport] = Field(
#         default_factory=list
#     )

#     disclaimer: Optional[str] = None

#     # --------------------------------------------------------
#     # Complete recommendation
#     # --------------------------------------------------------

#     final_recommendation: FinalRecommendation = Field(
#         default_factory=FinalRecommendation
#     )


# # ============================================================
# # FINAL RESULT REQUEST
# # ============================================================

# class FinalResultRequest(BaseModel):

#     message: str = Field(
#         ...,
#         min_length=1
#     )

#     analysis: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     answers: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     extra_info: Optional[str] = None

#     language: str = "en"


# # ============================================================
# # FINAL RESULT RESPONSE
# # ============================================================

# class FinalResultResponse(BaseModel):

#     understand: Dict[str, Any]

#     laws: List[Dict[str, Any]] = Field(
#         default_factory=list
#     )

#     actions: List[str] = Field(
#         default_factory=list
#     )

#     evidence: List[str] = Field(
#         default_factory=list
#     )

#     escalation: Optional[Any] = None

#     document: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     sources: List[Dict[str, Any]] = Field(
#         default_factory=list
#     )


# # ============================================================
# # GENERATE DRAFT REQUEST
# # ============================================================

# class DraftRequest(BaseModel):

#     category: str = Field(
#         ...,
#         min_length=1
#     )

#     information: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     language: str = "en"


# # ============================================================
# # GENERATE DRAFT RESPONSE
# # ============================================================

# class DraftResponse(BaseModel):

#     title: str

#     content: str

#     language: str

# # ============================================================
# # FINAL RESULT REQUEST
# # ============================================================

# class FinalResultRequest(BaseModel):

#     problem_text: str = Field(
#         ...,
#         min_length=1,
#     )

#     analysis: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     answers: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     extra_info: Optional[str] = None

#     lang: str = "en"


# # ============================================================
# # FINAL RESULT RESPONSE
# # ============================================================

# class FinalResultResponse(BaseModel):

#     category: str

#     understand: Dict[str, Any]

#     laws: List[Dict[str, Any]] = Field(
#         default_factory=list
#     )

#     actions: List[str] = Field(
#         default_factory=list
#     )

#     evidence: List[str] = Field(
#         default_factory=list
#     )

#     escalation: Optional[str] = None

#     document: Dict[str, Any] = Field(
#         default_factory=dict
#     )

#     sources: List[Dict[str, Any]] = Field(
#         default_factory=list
#     )

# # from typing import Any, Dict, List, Optional

# # from pydantic import BaseModel, Field


# # # ============================================================
# # # ANALYZE REQUEST
# # # ============================================================

# # class AnalyzeRequest(BaseModel):
# #     message: str = Field(..., min_length=1)
# #     language: str = "en"

# #     # Answers provided after follow-up questions
# #     answers: Dict[str, Any] = Field(
# #         default_factory=dict
# #     )

# #     # Optional additional information
# #     anything_else: Optional[str] = None

# #     # User can skip follow-up questions
# #     skip_follow_up: bool = False


# # # ============================================================
# # # FOLLOW-UP QUESTION
# # # ============================================================

# # class FollowUpQuestion(BaseModel):
# #     id: str

# #     # Frontend should display this
# #     text: str

# #     why_asked: Optional[str] = None

# #     field_type: str = "text"

# #     required: bool = False


# # # ============================================================
# # # LEGAL SUPPORT
# # # ============================================================

# # class LegalSupport(BaseModel):
# #     title: str

# #     description: Optional[str] = None

# #     type: Optional[str] = None

# #     url: Optional[str] = None

# #     verify_before_use: bool = True


# # # ============================================================
# # # DOCUMENT
# # # ============================================================

# # class DocumentRequirement(BaseModel):
# #     id: str

# #     name: str

# #     required: bool = False


# # # ============================================================
# # # AUTHORITY
# # # ============================================================

# # class AuthorityInfo(BaseModel):
# #     id: str

# #     name: str

# #     role: Optional[str] = None

# #     jurisdiction: Optional[str] = None


# # # ============================================================
# # # ESCALATION
# # # ============================================================

# # class EscalationInfo(BaseModel):
# #     appropriate: bool = False

# #     reason: Optional[str] = None

# #     authorities: List[AuthorityInfo] = Field(
# #         default_factory=list
# #     )


# # # ============================================================
# # # FINAL RECOMMENDATION
# # # ============================================================

# # class FinalRecommendation(BaseModel):
# #     workflow: Optional[str] = None

# #     workflow_name: Optional[str] = None

# #     legal_support: List[LegalSupport] = Field(
# #         default_factory=list
# #     )

# #     documents: List[DocumentRequirement] = Field(
# #         default_factory=list
# #     )

# #     authorities: List[AuthorityInfo] = Field(
# #         default_factory=list
# #     )

# #     action_plan: List[str] = Field(
# #         default_factory=list
# #     )

# #     evidence: List[str] = Field(
# #         default_factory=list
# #     )

# #     escalation: EscalationInfo = Field(
# #         default_factory=EscalationInfo
# #     )

# #     disclaimer: Optional[str] = None


# # # ============================================================
# # # ANALYZE RESPONSE
# # # ============================================================

# # class AnalyzeResponse(BaseModel):

# #     # --------------------------------------------------------
# #     # Classification
# #     # --------------------------------------------------------

# #     category: str

# #     intent: str

# #     language: str

# #     initial_advice: str = ""

# #     missing_information: List[str] = Field(
# #         default_factory=list
# #     )

# #     # --------------------------------------------------------
# #     # Follow-up
# #     # --------------------------------------------------------

# #     needs_more_information: bool = False

# #     can_skip_follow_up: bool = True

# #     skipped_follow_up: bool = False

# #     follow_up_questions: List[FollowUpQuestion] = Field(
# #         default_factory=list
# #     )

# #     # --------------------------------------------------------
# #     # Workflow
# #     # --------------------------------------------------------

# #     workflow: Optional[str] = None

# #     supported: bool = True

# #     # --------------------------------------------------------
# #     # Legal / workflow result
# #     # --------------------------------------------------------

# #     legal_support: List[LegalSupport] = Field(
# #         default_factory=list
# #     )

# #     documents: List[DocumentRequirement] = Field(
# #         default_factory=list
# #     )

# #     evidence: List[str] = Field(
# #         default_factory=list
# #     )

# #     action_plan: List[str] = Field(
# #         default_factory=list
# #     )

# #     escalation: EscalationInfo = Field(
# #         default_factory=EscalationInfo
# #     )

# #     sources: List[LegalSupport] = Field(
# #         default_factory=list
# #     )

# #     disclaimer: Optional[str] = None

# #     # --------------------------------------------------------
# #     # Complete recommendation
# #     # --------------------------------------------------------

# #     final_recommendation: FinalRecommendation = Field(
# #         default_factory=FinalRecommendation
# #     )


# # # ============================================================
# # # GENERATE DRAFT REQUEST
# # # ============================================================

# # class DraftRequest(BaseModel):

# #     category: str = Field(
# #         ...,
# #         min_length=1
# #     )

# #     information: Dict[str, Any] = Field(
# #         default_factory=dict
# #     )

# #     language: str = "en"


# # # ============================================================
# # # GENERATE DRAFT RESPONSE
# # # ============================================================

# # class DraftResponse(BaseModel):

# #     title: str

# #     content: str

# #     language: str