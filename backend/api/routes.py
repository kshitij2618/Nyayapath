from typing import Any, Dict, Optional

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
                message=request.message,
                language=language,
                answers=request.answers,
                skip_follow_up=request.skip_follow_up,
                initial_advice=initial_advice,
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
# GENERATE DRAFT
# ============================================================

@router.post(
    "/generate-draft",
    response_model=DraftResponse,
)
def generate_draft(request: DraftRequest):

    try:

        result = gemma_service.generate_draft(
            category=request.category,
            information=request.information,
            language=request.language,
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Gemma returned an invalid draft response."
            )

        return DraftResponse(
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
            detail=f"Draft generation failed: {str(exc)}",
        )