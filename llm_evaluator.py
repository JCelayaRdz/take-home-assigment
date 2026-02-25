from openai import AsyncOpenAI
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential
)
from schemas import EvaluationSchema
from log import setup_logger

logger = setup_logger("LLMEvaluator")

class LLMEvaluator:
    def __init__(self, 
                 api_key: str, 
                 gpt_model: str, 
                 system_prompt: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.gpt_model = gpt_model
        self.system_prompt = system_prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def evaluate(self, ticket: str, reply: str) -> EvaluationSchema:
        logger.info("Sending request to OpenAI...")
        response = await self.client.beta.chat.completions.parse(
            model=self.gpt_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Ticket {ticket}\nReply: {reply}"}
            ],
            response_format=EvaluationSchema
        )
        logger.info("Response received and parsed successfully")
        return response.choices[0].message.parsed