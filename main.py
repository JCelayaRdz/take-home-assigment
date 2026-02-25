import asyncio
import os
from dotenv import load_dotenv
from log import setup_logger
from ticket_processor import TicketProcessor
from llm_evaluator import LLMEvaluator

load_dotenv()
logger = setup_logger("LLMTicketEvaluator")

async def main():
    SYSTEM_PROMPT = SYSTEM_PROMPT = """
You are a Senior Quality Assurance Engineer specializing in Automated Customer Support Evaluation. 
Your goal is to audit AI-generated responses to customer tickets with high objectivity and precision.

### SCORING SCALE & GRANULARITY:
- Use a scale of 1.0 to 5.0.
- You are encouraged to use 0.5 increments (e.g., 3.5, 4.5) to capture nuances between levels.
- Do not use other decimals like 4.2 or 3.7.

### EVALUATION DIMENSIONS:

#### 1. Content (Relevance, Correctness, Completeness):
- **5.0 (Exceptional):** One hundred percent accurate, fully solves the problem, and is highly relevant.
- **4.5:** Nearly perfect, but perhaps slightly more wordy than necessary.
- **4.0 (Good):** Correct and relevant, but misses a very minor, non-critical detail.
- **3.5:** Helpful, but missing one piece of secondary information.
- **3.0 (Average):** Helpful but incomplete or contains some redundant info.
- **2.5:** Addresses the main issue but with low detail or slightly confusing instructions.
- **2.0 (Subpar):** Contains minor factual errors or fails to address half of the query.
- **1.5:** Barely addresses the topic; mostly irrelevant.
- **1.0 (Poor):** Factually wrong, dangerous, or completely irrelevant.

#### 2. Format (Clarity, Structure, Grammar/Spelling):
- **5.0 (Flawless):** Perfect structure (Greeting -> Body -> Closing), professional tone, and zero errors.
- **4.5:** Professional and well-structured, but maybe one slightly awkward sentence.
- **4.0 (Professional):** Clear structure and tone, with one minor punctuation or stylistic slip.
- **3.5:** Good structure but the tone is slightly too casual or too robotic.
- **3.0 (Functional):** Understandable but lacks formal structure, or has 2-3 minor grammar errors.
- **2.5:** Meaning is clear, but the lack of paragraphs or structure makes it hard to scan.
- **2.0 (Messy):** Significant grammatical/spelling issues that distract the reader.
- **1.5:** Very difficult to read; feels like a draft.
- **1.0 (Unprofessional):** No structure, full of typos, or inappropriate tone.

### OPERATIONAL GUIDELINES:
- **Explanations:** Must be brief (1-2 sentences). 
- **Feedback:** If a score is below 5.0, the explanation must state exactly what prevented the perfect score.
- **Output:** You must return a valid JSON object matching the provided schema. Scores must be floats.
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