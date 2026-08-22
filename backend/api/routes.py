from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    DraftRequest,
    DraftResponse,
)

from backend.services.gemma_service import gemma_service
from backend.services.workflow_service import workflow_service


router = APIRouter()


# ============================================================
# ANALYZE
# ============================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(request: AnalyzeRequest):

    try:

        # ----------------------------------------------------
        # 1. Gemma classification
        # ----------------------------------------------------

        classification = (
            gemma_service.analyze_citizen_message(
                message=request.message,
                language=request.language,
            )
        )

        if not isinstance(classification, dict):
            raise ValueError(
                "Gemma returned an invalid classification response."
            )

        # ----------------------------------------------------
        # 2. Extract classification
        # ----------------------------------------------------

        category = classification.get(
            "category",
            "unknown",
        )

        intent = classification.get(
            "intent",
            "unknown",
        )

        language = classification.get(
            "language",
            request.language,
        )

        initial_advice = classification.get(
            "initial_advice",
            "",
        )

        missing_information = classification.get(
            "missing_information",
            [],
        )

        # ----------------------------------------------------
        # 3. Combine optional extra information
        # ----------------------------------------------------

        message = request.message

        if request.anything_else:

            message = (
                message
                + "\n\nAdditional information:\n"
                + request.anything_else
            )

        # ----------------------------------------------------
        # 4. Deterministic workflow engine
        # ----------------------------------------------------

        result = workflow_service.analyze_workflow(

            category=category,

            intent=intent,

            message=message,

            language=language,

            answers=request.answers,

            skip_follow_up=request.skip_follow_up,

            initial_advice=initial_advice,

            missing_information=missing_information,
        )

        # ----------------------------------------------------
        # 5. Validate response
        # ----------------------------------------------------

        return AnalyzeResponse(
            **result
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Invalid model response: {str(exc)}",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        )


# ============================================================
# FINAL RESULT
# ============================================================

@router.post(
    "/final-result",
)
def final_result(request: Dict[str, Any]):

    print()
    print("========== FINAL RESULT REQUEST ==========")
    print(request)
    print("==========================================")

    try:

        # ----------------------------------------------------
        # Extract values
        # ----------------------------------------------------

        category = request.get(
            "category"
        )

        intent = request.get(
            "intent"
        )

        message = request.get(
            "message",
            "",
        )

        language = request.get(
            "language",
            "en",
        )

        answers = request.get(
            "answers",
            {},
        )

        initial_advice = request.get(
            "initial_advice",
            "",
        )

        missing_information = request.get(
            "missing_information",
            [],
        )

        # ----------------------------------------------------
        # Support nested analysis object
        # ----------------------------------------------------

        analysis = request.get(
            "analysis"
        )

        if isinstance(analysis, dict):

            if not category:
                category = analysis.get(
                    "category"
                )

            if not intent:
                intent = analysis.get(
                    "intent"
                )

            if not message:
                message = analysis.get(
                    "message",
                    "",
                )

            if not language:
                language = analysis.get(
                    "language",
                    "en",
                )

            if not initial_advice:
                initial_advice = analysis.get(
                    "initial_advice",
                    "",
                )

            if not missing_information:
                missing_information = analysis.get(
                    "missing_information",
                    [],
                )

        # ----------------------------------------------------
        # Alternate answer field names
        # ----------------------------------------------------

        if not answers:

            answers = request.get(
                "follow_up_answers",
                {},
            )

        if not answers:

            answers = request.get(
                "question_answers",
                {},
            )

        if not isinstance(
            answers,
            dict,
        ):
            answers = {}

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        category = str(
            category or ""
        ).strip()

        intent = str(
            intent or ""
        ).strip()

        message = str(
            message or ""
        ).strip()

        language = str(
            language or "en"
        ).strip()

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not category:

            raise ValueError(
                "category is missing from /final-result request."
            )

        if not intent:

            raise ValueError(
                "intent is missing from /final-result request."
            )

        # ----------------------------------------------------
        # Run workflow
        # ----------------------------------------------------

        result = workflow_service.analyze_workflow(

            category=category,

            intent=intent,

            message=message,

            language=language,

            answers=answers,

            skip_follow_up=True,

            initial_advice=initial_advice,

            missing_information=missing_information,
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        response = {

            "success": True,

            "category": result.get(
                "category"
            ),

            "intent": result.get(
                "intent"
            ),

            "language": result.get(
                "language"
            ),

            "initial_advice": result.get(
                "initial_advice",
                "",
            ),

            "missing_information": result.get(
                "missing_information",
                [],
            ),

            "needs_more_information": result.get(
                "needs_more_information",
                False,
            ),

            "workflow": result.get(
                "workflow"
            ),

            "supported": result.get(
                "supported",
                True,
            ),

            "legal_support": result.get(
                "legal_support",
                [],
            ),

            "documents": result.get(
                "documents",
                [],
            ),

            "evidence": result.get(
                "evidence",
                [],
            ),

            "action_plan": result.get(
                "action_plan",
                [],
            ),

            "escalation": result.get(
                "escalation",
                {},
            ),

            "sources": result.get(
                "sources",
                [],
            ),

            "disclaimer": result.get(
                "disclaimer"
            ),

            "final_recommendation": result.get(
                "final_recommendation",
                {},
            ),
        }

        print()
        print("========== FINAL RESULT SUCCESS ==========")
        print(
            "category =",
            response.get("category"),
        )
        print(
            "intent =",
            response.get("intent"),
        )
        print(
            "workflow =",
            response.get("workflow"),
        )
        print("==========================================")
        print()

        return response

    except ValueError as exc:

        print(
            "FINAL RESULT VALIDATION ERROR:",
            str(exc),
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "FINAL RESULT INTERNAL ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Final result generation failed: "
                + str(exc)
            ),
        )


# ============================================================
# GENERATE DRAFT
# ============================================================

@router.post(
    "/generate-draft",
    response_model=DraftResponse,
)
def generate_draft(request: DraftRequest):

    print()
    print("========== GENERATE DRAFT REQUEST ==========")
    print("category =", request.category)
    print("language =", request.language)
    print("information =", request.information)
    print("============================================")

    try:

        # ----------------------------------------------------
        # Call Gemma
        # ----------------------------------------------------

        result = gemma_service.generate_draft(

            category=request.category,

            information=request.information,

            language=request.language,
        )

        # ----------------------------------------------------
        # Validate Gemma response
        # ----------------------------------------------------

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                "Gemma returned an invalid draft response."
            )

        # ----------------------------------------------------
        # Normalize response
        # ----------------------------------------------------

        title = result.get(
            "title",
            "NyayaPath Draft",
        )

        content = result.get(
            "content",
            result.get(
                "body",
                "",
            ),
        )

        language = result.get(
            "language",
            request.language,
        )

        if not content:

            raise ValueError(
                "Gemma returned an empty draft."
            )

        response = DraftResponse(

            title=str(
                title
            ),

            content=str(
                content
            ),

            language=str(
                language
            ),
        )

        print()
        print("========== GENERATE DRAFT SUCCESS ==========")
        print("title =", response.title)
        print("language =", response.language)
        print("============================================")
        print()

        return response

    except ValueError as exc:

        print(
            "GENERATE DRAFT VALIDATION ERROR:",
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=f"Invalid draft response: {str(exc)}",
        )

    except Exception as exc:

        print(
            "GENERATE DRAFT INTERNAL ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Draft generation failed: "
                + str(exc)
            ),
        )


# from typing import Any, Dict

# from fastapi import APIRouter, HTTPException

# from backend.models.schemas import (
#     AnalyzeRequest,
#     AnalyzeResponse,
#     DraftRequest,
#     DraftResponse,
# )

# from backend.services.gemma_service import gemma_service
# from backend.services.workflow_service import workflow_service


# router = APIRouter()


# # ============================================================
# # ANALYZE
# # ============================================================

# @router.post(
#     "/analyze",
#     response_model=AnalyzeResponse,
# )
# def analyze(
#     request: AnalyzeRequest,
# ):

#     try:

#         # ------------------------------------------------------
#         # 1. Gemma classification
#         # ------------------------------------------------------

#         classification = (
#             gemma_service.analyze_citizen_message(
#                 message=request.message,
#                 language=request.language,
#             )
#         )

#         if not isinstance(
#             classification,
#             dict,
#         ):

#             raise ValueError(
#                 "Gemma returned an invalid classification response."
#             )

#         # ------------------------------------------------------
#         # 2. Extract classification
#         # ------------------------------------------------------

#         category = classification.get(
#             "category",
#             "unknown",
#         )

#         intent = classification.get(
#             "intent",
#             "unknown",
#         )

#         language = classification.get(
#             "language",
#             request.language,
#         )

#         initial_advice = classification.get(
#             "initial_advice",
#             "",
#         )

#         missing_information = classification.get(
#             "missing_information",
#             [],
#         )

#         # ------------------------------------------------------
#         # 3. Combine additional information
#         # ------------------------------------------------------

#         message = request.message

#         if request.anything_else:

#             message = (
#                 message
#                 + "\n\nAdditional information:\n"
#                 + request.anything_else
#             )

#         # ------------------------------------------------------
#         # 4. Workflow
#         # ------------------------------------------------------

#         result = workflow_service.analyze_workflow(

#             category=category,

#             intent=intent,

#             message=message,

#             language=language,

#             answers=request.answers,

#             skip_follow_up=request.skip_follow_up,

#             initial_advice=initial_advice,

#             missing_information=missing_information,
#         )

#         # ------------------------------------------------------
#         # 5. Validate response
#         # ------------------------------------------------------

#         return AnalyzeResponse(
#             **result
#         )

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=502,
#             detail=f"Invalid model response: {str(exc)}",
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=f"Analysis failed: {str(exc)}",
#         )


# # ============================================================
# # FINAL RESULT
# # ============================================================

# @router.post(
#     "/final-result",
# )
# def final_result(
#     request: Dict[str, Any],
# ):

#     try:

#         print(
#             "\n========== FINAL RESULT REQUEST =========="
#         )

#         print(request)

#         print(
#             "==========================================\n"
#         )

#         # ------------------------------------------------------
#         # Extract values
#         # ------------------------------------------------------

#         category = request.get(
#             "category",
#             "",
#         )

#         intent = request.get(
#             "intent",
#             "",
#         )

#         message = request.get(
#             "message",
#             "",
#         )

#         language = request.get(
#             "language",
#             "en",
#         )

#         answers = request.get(
#             "answers",
#             {},
#         )

#         initial_advice = request.get(
#             "initial_advice",
#             "",
#         )

#         missing_information = request.get(
#             "missing_information",
#             [],
#         )

#         # ------------------------------------------------------
#         # Support nested analysis
#         # ------------------------------------------------------

#         analysis = request.get(
#             "analysis"
#         )

#         if isinstance(
#             analysis,
#             dict,
#         ):

#             if not category:

#                 category = analysis.get(
#                     "category",
#                     "",
#                 )

#             if not intent:

#                 intent = analysis.get(
#                     "intent",
#                     "",
#                 )

#             if not message:

#                 message = analysis.get(
#                     "message",
#                     "",
#                 )

#             if not language:

#                 language = analysis.get(
#                     "language",
#                     "en",
#                 )

#             if not initial_advice:

#                 initial_advice = analysis.get(
#                     "initial_advice",
#                     "",
#                 )

#             if not missing_information:

#                 missing_information = analysis.get(
#                     "missing_information",
#                     [],
#                 )

#         # ------------------------------------------------------
#         # Alternate answer names
#         # ------------------------------------------------------

#         if not answers:

#             answers = request.get(
#                 "follow_up_answers",
#                 {},
#             )

#         if not answers:

#             answers = request.get(
#                 "question_answers",
#                 {},
#             )

#         if not isinstance(
#             answers,
#             dict,
#         ):

#             answers = {}

#         # ------------------------------------------------------
#         # Normalize
#         # ------------------------------------------------------

#         category = str(
#             category or ""
#         ).strip()

#         intent = str(
#             intent or ""
#         ).strip()

#         message = str(
#             message or ""
#         ).strip()

#         language = str(
#             language or "en"
#         ).strip()

#         # ------------------------------------------------------
#         # Validation
#         # ------------------------------------------------------

#         if not category:

#             raise ValueError(
#                 "category is missing from /final-result request."
#             )

#         if not intent:

#             raise ValueError(
#                 "intent is missing from /final-result request."
#             )

#         # ------------------------------------------------------
#         # Debug
#         # ------------------------------------------------------

#         print(
#             "\n========== FINAL RESULT VALUES =========="
#         )

#         print(
#             "category =",
#             repr(category),
#         )

#         print(
#             "intent =",
#             repr(intent),
#         )

#         print(
#             "message =",
#             repr(message),
#         )

#         print(
#             "language =",
#             repr(language),
#         )

#         print(
#             "answers =",
#             repr(answers),
#         )

#         print(
#             "=========================================\n"
#         )

#         # ------------------------------------------------------
#         # Run workflow
#         # ------------------------------------------------------

#         result = workflow_service.analyze_workflow(

#             category=category,

#             intent=intent,

#             message=message,

#             language=language,

#             answers=answers,

#             skip_follow_up=True,

#             initial_advice=initial_advice,

#             missing_information=missing_information,
#         )

#         # ------------------------------------------------------
#         # Return complete result
#         # ------------------------------------------------------

#         response = {

#             "success": True,

#             "category": result.get(
#                 "category"
#             ),

#             "intent": result.get(
#                 "intent"
#             ),

#             "language": result.get(
#                 "language"
#             ),

#             "initial_advice": result.get(
#                 "initial_advice",
#                 "",
#             ),

#             "missing_information": result.get(
#                 "missing_information",
#                 [],
#             ),

#             "needs_more_information": result.get(
#                 "needs_more_information",
#                 False,
#             ),

#             "can_skip_follow_up": result.get(
#                 "can_skip_follow_up",
#                 True,
#             ),

#             "skipped_follow_up": result.get(
#                 "skipped_follow_up",
#                 True,
#             ),

#             "follow_up_questions": result.get(
#                 "follow_up_questions",
#                 [],
#             ),

#             "workflow": result.get(
#                 "workflow"
#             ),

#             "supported": result.get(
#                 "supported",
#                 True,
#             ),

#             "legal_support": result.get(
#                 "legal_support",
#                 [],
#             ),

#             "documents": result.get(
#                 "documents",
#                 [],
#             ),

#             "evidence": result.get(
#                 "evidence",
#                 [],
#             ),

#             "action_plan": result.get(
#                 "action_plan",
#                 [],
#             ),

#             "escalation": result.get(
#                 "escalation",
#                 {},
#             ),

#             "sources": result.get(
#                 "sources",
#                 [],
#             ),

#             "disclaimer": result.get(
#                 "disclaimer"
#             ),

#             "final_recommendation": result.get(
#                 "final_recommendation",
#                 {},
#             ),
#         }

#         print(
#             "\n========== FINAL RESULT SUCCESS =========="
#         )

#         print(
#             "workflow =",
#             response.get(
#                 "workflow"
#             ),
#         )

#         print(
#             "==========================================\n"
#         )

#         return response

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=400,
#             detail=str(exc),
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Final result generation failed: "
#                 + str(exc)
#             ),
#         )


# # ============================================================
# # GENERATE DRAFT
# # ============================================================

# @router.post(
#     "/generate-draft",
#     response_model=DraftResponse,
# )
# def generate_draft(
#     request: DraftRequest,
# ):

#     try:

#         print(
#             "\n========== GENERATE DRAFT REQUEST =========="
#         )

#         print(
#             "category =",
#             repr(request.category),
#         )

#         print(
#             "information =",
#             repr(request.information),
#         )

#         print(
#             "language =",
#             repr(request.language),
#         )

#         print(
#             "============================================\n"
#         )

#         # ------------------------------------------------------
#         # Generate draft using Gemma
#         # ------------------------------------------------------

#         result = gemma_service.generate_draft(

#             category=request.category,

#             information=request.information,

#             language=request.language,
#         )

#         # ------------------------------------------------------
#         # Validate Gemma response
#         # ------------------------------------------------------

#         if not isinstance(
#             result,
#             dict,
#         ):

#             raise ValueError(
#                 "Gemma returned an invalid draft response."
#             )

#         # ------------------------------------------------------
#         # Make sure required fields exist
#         # ------------------------------------------------------

#         title = result.get(
#             "title",
#             "",
#         )

#         content = result.get(
#             "content",
#             "",
#         )

#         language = result.get(
#             "language",
#             request.language,
#         )

#         if not title:

#             raise ValueError(
#                 "Generated draft has no title."
#             )

#         if not content:

#             raise ValueError(
#                 "Generated draft has no content."
#             )

#         # ------------------------------------------------------
#         # Return validated response
#         # ------------------------------------------------------

#         response = DraftResponse(

#             title=title,

#             content=content,

#             language=language,
#         )

#         print(
#             "\n========== GENERATE DRAFT SUCCESS =========="
#         )

#         print(
#             "title =",
#             response.title,
#         )

#         print(
#             "============================================\n"
#         )

#         return response

#     except ValueError as exc:

#         raise HTTPException(
#             status_code=502,
#             detail=f"Draft generation failed: {str(exc)}",
#         )

#     except Exception as exc:

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Draft generation failed: "
#                 + str(exc)
#             ),
#         )



# # from typing import Any, Dict

# # from fastapi import APIRouter, HTTPException

# # from backend.models.schemas import (
# #     AnalyzeRequest,
# #     AnalyzeResponse,
# #     DraftRequest,
# #     DraftResponse,
# # )

# # from backend.services.gemma_service import gemma_service
# # from backend.services.workflow_service import workflow_service


# # router = APIRouter()


# # # ============================================================
# # # ANALYZE
# # # ============================================================

# # @router.post(
# #     "/analyze",
# #     response_model=AnalyzeResponse,
# # )
# # def analyze(request: AnalyzeRequest):

# #     try:

# #         # ----------------------------------------------------
# #         # 1. Gemma classification
# #         # ----------------------------------------------------

# #         classification = gemma_service.analyze_citizen_message(
# #             message=request.message,
# #             language=request.language,
# #         )

# #         if not isinstance(classification, dict):
# #             raise ValueError(
# #                 "Gemma returned an invalid classification response."
# #             )

# #         # ----------------------------------------------------
# #         # 2. Extract classification
# #         # ----------------------------------------------------

# #         category = str(
# #             classification.get("category", "unknown")
# #         ).strip()

# #         intent = str(
# #             classification.get("intent", "unknown")
# #         ).strip()

# #         language = str(
# #             classification.get(
# #                 "language",
# #                 request.language,
# #             )
# #         ).strip()

# #         initial_advice = classification.get(
# #             "initial_advice",
# #             "",
# #         )

# #         missing_information = classification.get(
# #             "missing_information",
# #             [],
# #         )

# #         if not isinstance(missing_information, list):
# #             missing_information = []

# #         # ----------------------------------------------------
# #         # 3. Combine optional additional information
# #         # ----------------------------------------------------

# #         message = request.message

# #         if request.anything_else:
# #             message = (
# #                 message
# #                 + "\n\nAdditional information:\n"
# #                 + request.anything_else
# #             )

# #         # ----------------------------------------------------
# #         # 4. Workflow engine
# #         # ----------------------------------------------------

# #         result = workflow_service.analyze_workflow(
# #             category=category,
# #             intent=intent,
# #             message=message,
# #             language=language,
# #             answers=request.answers,
# #             skip_follow_up=request.skip_follow_up,
# #             initial_advice=initial_advice,
# #             missing_information=missing_information,
# #         )

# #         # ----------------------------------------------------
# #         # 5. Return structured response
# #         # ----------------------------------------------------

# #         return AnalyzeResponse(**result)

# #     except ValueError as exc:

# #         raise HTTPException(
# #             status_code=502,
# #             detail=f"Invalid model response: {str(exc)}",
# #         )

# #     except Exception as exc:

# #         raise HTTPException(
# #             status_code=500,
# #             detail=f"Analysis failed: {str(exc)}",
# #         )


# # # ============================================================
# # # FINAL RESULT
# # # ============================================================

# # @router.post("/final-result")
# # def final_result(request: Dict[str, Any]):

# #     print("\n========== FINAL RESULT REQUEST ==========")
# #     print(request)
# #     print("==========================================")

# #     try:

# #         # ----------------------------------------------------
# #         # 1. Read top-level values
# #         # ----------------------------------------------------

# #         category = request.get("category", "")
# #         intent = request.get("intent", "")
# #         message = request.get("message", "")
# #         language = request.get("language", "en")

# #         answers = request.get("answers", {})

# #         initial_advice = request.get(
# #             "initial_advice",
# #             "",
# #         )

# #         missing_information = request.get(
# #             "missing_information",
# #             [],
# #         )

# #         # ----------------------------------------------------
# #         # 2. Support nested analysis object
# #         # ----------------------------------------------------

# #         analysis = request.get("analysis")

# #         if isinstance(analysis, dict):

# #             if not category:
# #                 category = analysis.get(
# #                     "category",
# #                     "",
# #                 )

# #             if not intent:
# #                 intent = analysis.get(
# #                     "intent",
# #                     "",
# #                 )

# #             if not message:
# #                 message = analysis.get(
# #                     "message",
# #                     "",
# #                 )

# #             if not language:
# #                 language = analysis.get(
# #                     "language",
# #                     "en",
# #                 )

# #             if not initial_advice:
# #                 initial_advice = analysis.get(
# #                     "initial_advice",
# #                     "",
# #                 )

# #             if not missing_information:
# #                 missing_information = analysis.get(
# #                     "missing_information",
# #                     [],
# #                 )

# #         # ----------------------------------------------------
# #         # 3. Support alternate answer names
# #         # ----------------------------------------------------

# #         if not answers:
# #             answers = request.get(
# #                 "follow_up_answers",
# #                 {},
# #             )

# #         if not answers:
# #             answers = request.get(
# #                 "question_answers",
# #                 {},
# #             )

# #         if not isinstance(answers, dict):
# #             answers = {}

# #         # ----------------------------------------------------
# #         # 4. Normalize values
# #         # ----------------------------------------------------

# #         category = str(
# #             category or ""
# #         ).strip()

# #         intent = str(
# #             intent or ""
# #         ).strip()

# #         message = str(
# #             message or ""
# #         ).strip()

# #         language = str(
# #             language or "en"
# #         ).strip()

# #         if not isinstance(
# #             missing_information,
# #             list,
# #         ):
# #             missing_information = []

# #         # ----------------------------------------------------
# #         # DEBUG
# #         # ----------------------------------------------------

# #         print("\n========== FINAL RESULT VALUES ==========")
# #         print("category =", repr(category))
# #         print("intent =", repr(intent))
# #         print("message =", repr(message))
# #         print("language =", repr(language))
# #         print("answers =", repr(answers))
# #         print("initial_advice =", repr(initial_advice))
# #         print(
# #             "missing_information =",
# #             repr(missing_information),
# #         )
# #         print("=========================================\n")

# #         # ----------------------------------------------------
# #         # 5. Validate
# #         # ----------------------------------------------------

# #         if not category:
# #             raise ValueError(
# #                 "category is missing from /final-result request."
# #             )

# #         if not intent:
# #             raise ValueError(
# #                 "intent is missing from /final-result request."
# #             )

# #         # ----------------------------------------------------
# #         # 6. Run workflow
# #         # ----------------------------------------------------

# #         result = workflow_service.analyze_workflow(
# #             category=category,
# #             intent=intent,
# #             message=message,
# #             language=language,
# #             answers=answers,
# #             skip_follow_up=True,
# #             initial_advice=initial_advice,
# #             missing_information=missing_information,
# #         )

# #         if not isinstance(result, dict):
# #             raise ValueError(
# #                 "Workflow service returned an invalid result."
# #             )

# #         # ----------------------------------------------------
# #         # 7. Return COMPLETE result
# #         # ----------------------------------------------------

# #         response = {
# #             "success": True,

# #             "category": result.get(
# #                 "category",
# #                 category,
# #             ),

# #             "intent": result.get(
# #                 "intent",
# #                 intent,
# #             ),

# #             "language": result.get(
# #                 "language",
# #                 language,
# #             ),

# #             "initial_advice": result.get(
# #                 "initial_advice",
# #                 initial_advice,
# #             ),

# #             "missing_information": result.get(
# #                 "missing_information",
# #                 missing_information,
# #             ),

# #             "needs_more_information": result.get(
# #                 "needs_more_information",
# #                 False,
# #             ),

# #             "can_skip_follow_up": result.get(
# #                 "can_skip_follow_up",
# #                 True,
# #             ),

# #             "skipped_follow_up": result.get(
# #                 "skipped_follow_up",
# #                 True,
# #             ),

# #             "follow_up_questions": result.get(
# #                 "follow_up_questions",
# #                 [],
# #             ),

# #             "workflow": result.get(
# #                 "workflow"
# #             ),

# #             "supported": result.get(
# #                 "supported",
# #                 True,
# #             ),

# #             "legal_support": result.get(
# #                 "legal_support",
# #                 [],
# #             ),

# #             "documents": result.get(
# #                 "documents",
# #                 [],
# #             ),

# #             "evidence": result.get(
# #                 "evidence",
# #                 [],
# #             ),

# #             "action_plan": result.get(
# #                 "action_plan",
# #                 [],
# #             ),

# #             "escalation": result.get(
# #                 "escalation",
# #                 {},
# #             ),

# #             "sources": result.get(
# #                 "sources",
# #                 [],
# #             ),

# #             "disclaimer": result.get(
# #                 "disclaimer"
# #             ),

# #             "final_recommendation": result.get(
# #                 "final_recommendation",
# #                 {},
# #             ),
# #         }

# #         print("\n========== FINAL RESULT SUCCESS ==========")
# #         print(
# #             "category =",
# #             response.get("category"),
# #         )
# #         print(
# #             "intent =",
# #             response.get("intent"),
# #         )
# #         print(
# #             "workflow =",
# #             response.get("workflow"),
# #         )
# #         print("==========================================\n")

# #         return response

# #     except ValueError as exc:

# #         print(
# #             "\nFINAL RESULT VALIDATION ERROR:",
# #             str(exc),
# #         )

# #         raise HTTPException(
# #             status_code=400,
# #             detail=str(exc),
# #         )

# #     except Exception as exc:

# #         print(
# #             "\nFINAL RESULT INTERNAL ERROR:",
# #             repr(exc),
# #         )

# #         raise HTTPException(
# #             status_code=500,
# #             detail=(
# #                 "Final result generation failed: "
# #                 + str(exc)
# #             ),
# #         )


# # # ============================================================
# # # GENERATE DRAFT
# # # ============================================================

# # @router.post(
# #     "/generate-draft",
# #     response_model=DraftResponse,
# # )
# # def generate_draft(request: DraftRequest):

# #     try:

# #         print("\n========== GENERATE DRAFT REQUEST ==========")
# #         print(request.model_dump())
# #         print("=============================================")

# #         result = gemma_service.generate_draft(
# #             category=request.category,
# #             information=request.information,
# #             language=request.language,
# #         )

# #         if not isinstance(result, dict):
# #             raise ValueError(
# #                 "Gemma returned an invalid draft response."
# #             )

# #         return DraftResponse(**result)

# #     except ValueError as exc:

# #         raise HTTPException(
# #             status_code=502,
# #             detail=f"Invalid model response: {str(exc)}",
# #         )

# #     except Exception as exc:

# #         raise HTTPException(
# #             status_code=500,
# #             detail=(
# #                 f"Draft generation failed: {str(exc)}"
# #             ),
# #         )