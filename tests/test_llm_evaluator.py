import pytest
from schemas import EvaluationSchema
from llm_evaluator import LLMEvaluator
from unittest.mock import (
    AsyncMock,
    patch,
    MagicMock
)

class TestLLMEvaluator:
    @pytest.mark.asyncio
    async def test_evaluate_success(self):
        mock_parsed_result = EvaluationSchema(
            content_score=5.0,
            content_explanation="Excellent content",
            format_score=4.5,
            format_explanation="Almost perfect format"
        )

        evaluator = LLMEvaluator(api_key="fake-key", gpt_model="gpt-4o", system_prompt="Test")

        with patch.object(evaluator.client.beta.chat.completions, 'parse', new_callable=AsyncMock) as mock_parse:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(parsed=mock_parsed_result))]
            mock_parse.return_value = mock_response

            result = await evaluator.evaluate("Ticket message", "AI Reply")

            assert result.content_score == 5.0
            assert result.format_explanation == "Almost perfect format"
            mock_parse.assert_called_once()