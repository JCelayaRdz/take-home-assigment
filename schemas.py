from pydantic import BaseModel, Field

class EvaluationSchema(BaseModel):
    content_score: int = Field(..., ge=1, le=5)
    content_explanation: str
    format_score: int = Field(..., ge=1, le=5)
    format_explanation: str