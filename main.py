import asyncio
import os
from dotenv import load_dotenv
from log import setup_logger
from ticket_processor import TicketProcessor
from llm_evaluator import LLMEvaluator

load_dotenv()
logger = setup_logger("LLMTicketEvaluator")

async def main():
    SYSTEM_PROMPT = """
You are an expert Quality Assurance (QA) Analyst specializing in Customer Support Excellence. 
Your task is to evaluate AI-generated responses to customer tickets based on two specific dimensions: Content and Format.

### EVALUATION DIMENSIONS:

1. **Content (Relevance, Correctness, Completeness):**
   - **5 (Excellent):** Perfectly addresses all customer concerns with one hundred percent accurate information. No missing details.
   - **3 (Average):** The response is helpful but might miss a minor detail or contain slightly redundant information.
   - **1 (Poor):** Irrelevant, factually incorrect, or fails to address the customer's primary issue.

2. **Format (Clarity, Structure, Grammar/Spelling):** [cite: 10]
   - **5 (Excellent):** Professional tone, logically structured (e.g., use of greeting/closing), and flawless grammar/spelling.
   - **3 (Average):** Understandable but lacks professional polish, has minor grammatical slips, or poor paragraph spacing.
   - **1 (Poor):** Unprofessional tone, significant spelling/grammar errors, or completely unstructured text.

### GUIDELINES FOR EXPLANATIONS:
- Be objective and professional.
- Keep explanations concise (1-2 sentences). 
- Explicitly mention what was missing or what could be improved if the score is less than 5.

### OUTPUT FORMAT:
You must strictly return a JSON object matching the requested schema. Ensure scores are integers between 1 and 5
"""
    
    processor = TicketProcessor("./data/tickets.csv", "./data/tickets_evaluated.csv")
    evaluator = LLMEvaluator(
        api_key=os.getenv("OPENAI_API_KEY"),
        gpt_model="gpt-4o",
        system_prompt=SYSTEM_PROMPT
    )

    rows = processor.load_tickets()
    
    semaphore = asyncio.Semaphore(2)

    async def evaluate_task(row):
        async with semaphore:
            try:
                evaluation = await evaluator.evaluate(row['ticket'], row['reply'])
                return {
                    **row,
                    "content_score": evaluation.content_score,
                    "content_explanation": evaluation.content_explanation,
                    "format_score": evaluation.format_score,
                    "format_explanation": evaluation.format_explanation
                }
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                return {**row, "content_score": 0, "content_explanation": "Error in evaluation", 
                        "format_score": 0, "format_explanation": "Error in evaluation"}

    logger.info(f"Starting evaluation of {len(rows)} tickets")
    tasks = [evaluate_task(row) for row in rows]
    results = await asyncio.gather(*tasks)
    
    processor.save_results(results)
    logger.info("Evaluation process completed")

if __name__ == "__main__":
    asyncio.run(main())