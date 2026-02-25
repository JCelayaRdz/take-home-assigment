# LLM-Based Ticket Reply Evaluation
This repository contains an automated evaluation system designed to audit AI-generated customer support responses. The system leverages GPT-4o to assess replies across two key dimensions: Content and Format.

## Project Structure
The project structure is the following:

```bash
.
├── data/
│   ├── tickets.csv            # Input file with tickets and replies 
│   └── tickets_evaluated.csv  # Output file with detailed evaluations
├── tests/                     # Unit testing suite
│   ├── test_llm_evaluator.py  # API Mocks and evaluation logic
│   ├── test_schemas.py        # Pydantic type and range validation
│   └── test_ticket_processor.py # CSV I/O testing
├── llm_evaluator.py           # OpenAI client, retry logic, and parsing
├── ticket_processor.py        # Pandas encapsulation for I/O
├── schemas.py                 # Data model definitions (Pydantic)
├── log.py                     # Centralized Logger configuration
├── main.py                    # Async orchestrator and entry point
├── pyproject.toml             # Project definition and dependencies (uv)
└── uv.lock                    # Lockfile for exact reproducibility
```

## Key Features
- **Asynchronous Processing:** Built with `asyncio` and `Semaphore` to handle multiple evaluations in parallel, optimizing throughput and reducing execution time.

- **Structured Outputs & Validation:** Utilizes OpenAI's parse method combined with `Pydantic` schemas to ensure all evaluations strictly follow the required format and data types.

- **Granular Scoring:** Implements a refined 0.5 increment scale (e.g., 4.5) to capture subtle quality differences that a standard 1-5 integer scale might miss.

- **Resilient Design:** Features exponential backoff retry logic using tenacity to gracefully handle API rate limits and transient errors.

- **Decoupled Architecture:** Separation of concerns between data processing (`TicketProcessor`), AI logic (`LLMEvaluator`), and configuration.

## Setup & Installation
I used [uv](https://docs.astral.sh/uv/getting-started/installation/) for this assimgent for dependency management.

1. Clone the Repository:

```bash
git clone https://github.com/JCelayaRdz/take-home-assigment.git
cd take-home-assignment
```

2. Environment Configuration:
Create a .env file in the root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

3. Install Dependencies:

```bash
uv sync
```

## Usage

To run the evaluation pipeline, ensure your input file is located at `data/tickets.csv`  and execute:

```bash
uv run main.py
```

The script will generate a `data/tickets_evaluated.csv` file containing the original data plus the four evaluation columns: `content_score`, `content_explanation`, `format_score`, and `format_explanation` .


## Testing
I used pytest for unit testing. The test suite uses Mocks to simulate OpenAI API responses, ensuring the logic is tested without consuming credits or requiring an internet connection.
Run tests with:

```bash
uv run pytest
```

## Engineering Decisions
- **Prompt Engineering:** The system prompt uses a detailed rubric to minimize model hallucination and ensure objective scoring.

- **Pydantic over JSON:** Pydantic was chosen to enforce field constraints (like `ge=1` and `le=5`) at the code level, providing a second layer of validation.

- **Pandas for Performance:** While Python's built-in csv library is sufficient for simple tasks, Pandas was chosen for its superior speed and efficiency in handling data structures, especially when scaling to larger datasets or performing future data analysis.

- **Logging:** A custom logger tracks the flow of each ticket, providing visibility into the asynchronous execution and any potential row-level failures

- **Framework Choice (OpenAI SDK vs. LangChain)**: I intentionally opted for the OpenAI SDK with Structured Outputs instead of a high-level framework like LangChain. For this specific task, I think that LangChain adds unnecessary abstraction and overhead.