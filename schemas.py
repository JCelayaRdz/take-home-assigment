from pydantic import BaseModel, Field

class EvaluationSchema(BaseModel):
    content_score: float = Field(..., ge=1.0, le=5.0)
    content_explanation: str
    format_score: float = Field(..., ge=1.0, le=5.0)
    format_explanation: str