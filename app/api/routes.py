from fastapi import APIRouter, HTTPException

from app.schemas.request_schema import ValidationRequest
from app.services.validation_service import ValidationService

router = APIRouter()


@router.post("/validate")
def validate_reports(request: ValidationRequest):
    try:
        service = ValidationService()
        return service.validate(
            batch=request.batch,
            host_generator_key=request.host_generator_key,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc