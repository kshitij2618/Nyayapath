from fastapi import APIRouter
from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    DraftRequest,
    DraftResponse,
)

from backend.services.gemma_service import gemma_service

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        result = gemma_service.analyze_citizen_message(
            message= request.message,
            language=  request.language,
        )
        return AnalyzeResponse(**result)
    except Exception as exc:
        raise HTTPExecution(
            status_code = 500,
            detail = f"Analysis failed: {str(exc)}",
        )

@router.post("/generate-draft", response_model=DraftResponse)
def generate_draft(request: DraftRequest):
    try:
        result= gemma_service.generate_draft(
            category=request.category,
            information= request.information,
            language= request.language,
        )
        return DraftResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code = 500,
            detail = f"Draft generation failed: {str(exc)}",
        )