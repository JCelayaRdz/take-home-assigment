import pytest
from schemas import EvaluationSchema

class TestEvaluationSchema:
    def test_valid_data(self):
        data = {
            "content_score": 4.5,
            "content_explanation": "Well done",
            "format_score": 3.0,
            "format_explanation": "Average"
        }
        schema = EvaluationSchema(**data)
        assert schema.content_score == 4.5

    def test_invalid_score_raises_error(self):
        with pytest.raises(ValueError):
            EvaluationSchema(
                content_score=6.0,
                content_explanation="N/A",
                format_score=3.0,
                format_explanation="N/A"
            )