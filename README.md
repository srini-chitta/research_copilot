
# Research Co-Pilot

## Purpose
The Research Co-Pilot is a multi-agent system designed to automate the process of mining, parsing, summarizing, synthesizing, and surveying research papers on a given topic. It leverages the MOYA framework and OpenAI LLMs to generate structured mini-surveys from arXiv or user-provided PDFs.

## Project Organization

```
research_copilot/
├── agents/                        # All agent implementations
│   ├── pdf_miner_agent.py         # Downloads PDFs from arXiv
│   ├── pdf_parser_agent.py        # Extracts text from PDFs
│   ├── summarizer_agent.py        # Summarizes paper text using LLM
│   ├── synthesizer_agent.py       # Synthesizes cross-paper insights
│   ├── survey_writer_agent.py     # Generates the final mini-survey
│   ├── reproducible_agent.py      # Reproducible OpenAI agent wrapper
│   └── __init__.py                # Exports all agents
├── memory/
│   ├── ephemeral_memory_setup.py  # EphemeralMemory configuration
│   └── __init__.py
├── config.py                      # Configuration and reproducibility settings
├── orchestrator.py                # Orchestrates the multi-agent workflow
├── main.py                        # CLI entrypoint
├── requirements.txt               # Project dependencies
├── mini_survey.txt                # Output: generated mini-survey
├── research_copilot.log           # Run logs (gitignored)
├── REPRODUCIBILITY.md             # Reproducibility documentation
└── README.md                      # Project documentation
```

## File Details

### Agents Directory (`agents/`)
All agent implementations are centralized in the `agents/` directory:

- **pdf_miner_agent.py**: Mines and downloads PDFs from arXiv for a given topic.
- **pdf_parser_agent.py**: Extracts text from PDF files using pdfplumber.
- **summarizer_agent.py**: Uses OpenAI LLM to summarize each paper in a structured format.
- **synthesizer_agent.py**: Synthesizes insights and research gaps across all summaries.
- **survey_writer_agent.py**: Generates a concise mini-survey with inline citations.
- **reproducible_agent.py**: Custom wrapper for OpenAI agent with temperature and seed support.
- **__init__.py**: Exports all agents for clean imports (`from agents import PDFMinerAgent, ...`).

### Core Files
- **config.py**: Configuration file containing reproducibility parameters (temperature, seed, model).
- **orchestrator.py**: Coordinates the workflow between all agents.
- **main.py**: Command-line interface for running the full pipeline with logging.
- **requirements.txt**: Lists all required Python packages.

### Output Files
- **mini_survey.txt**: Generated mini-survey output.
- **mini_survey_config.json**: Configuration used for the run (gitignored).
- **research_copilot.log**: Human-readable log file with run details and configuration (gitignored).
- **trace.jsonl**: Structured JSONL trace of all workflow events for observability (gitignored).

### Memory
- **memory/ephemeral_memory_setup.py**: Sets up shared memory for agent communication.

## Installation

1. **Clone the repository** (if not already):
	```sh
	git clone <your-repo-url>
	cd research_copilot
	```

2. **Clone or download the MOYA framework**

	> **Note:** This project depends on the MOYA framework. Please clone or download the MOYA repository at the same directory level as this project (i.e., both `research_copilot` and `moya` should be in the same parent folder) before installing requirements.

	```sh
	git clone https://github.com/montycloud/moya.git
	# Ensure the folder structure is:
	# parent_folder/
	# ├── moya/
	# └── research_copilot/
	```

3. **(Recommended) Create and activate a virtual environment:**
	```sh
	python3 -m venv .venv
	source .venv/bin/activate
	```

4. **Install dependencies:**
	```sh
	pip install -r requirements.txt
	```

5. **Set your OpenAI API key:**
	```sh
	export OPENAI_API_KEY=your-api-key-here
	```

## CLI Usage

Run the CLI to generate a mini-survey from arXiv:

```sh
python main.py --topic "Artificial General Intelligence"
```

Or, to process your own PDFs:

```sh
python main.py --pdf-folder pdfs_downloaded/
```

**Options:**

- `--topic <topic>`: Research topic to mine papers for (downloads from arXiv)
- `--pdf-folder <folder>`: Folder containing PDF files to process
- `--output <file>`: Output file for the mini-survey (default: mini_survey.txt)
- `--openai-api-key <key>`: OpenAI API key (or set OPENAI_API_KEY env var)
- `--temperature <float>`: LLM temperature for reproducibility (default: 0.0)
- `--seed <int>`: Random seed for reproducibility (default: 42)
- `--model <string>`: OpenAI model to use (default: gpt-4o)

The generated mini-survey will be saved to the specified output file.

## Reproducibility

This project ensures **deterministic and reproducible runs** through:

1. **Fixed Temperature**: Default temperature is set to 0.0 for deterministic outputs
2. **Fixed Seed**: Default seed is 42 for reproducible random sampling
3. **Configuration Logging**: All run parameters are logged to `research_copilot.log`
4. **Configuration Files**: Each run saves a `*_config.json` file alongside the output with the exact parameters used

To reproduce a run, use the same `--temperature`, `--seed`, and `--model` values as shown in the config file.

**Example with explicit reproducibility parameters:**

```sh
python main.py --topic "Sustainable AI" --temperature 0.0 --seed 42 --model gpt-4o
```

**Important Note:** While we implement all best practices for reproducibility, OpenAI's API provides "best-effort" determinism. Small variations in outputs may occur due to backend infrastructure changes, even with identical parameters. See `REPRODUCIBILITY_NOTES.md` for technical details.

## Observability

This project implements **comprehensive observability** through structured logging to `trace.jsonl`. Every step of the workflow is logged in JSONL (JSON Lines) format for analysis and debugging.

### What Gets Logged

The trace file captures:

1. **Workflow Events**: Start and completion with full configuration
2. **Agent Initialization**: When each agent is created
3. **LLM Interactions**: 
   - Requests with model, prompt preview, temperature, seed
   - Responses with token counts and system fingerprint
   - Tool calls (if any)
4. **Decisions**: Orchestrator decisions with reasoning
5. **Agent Actions**: Mining, parsing, summarization, synthesis, writing
6. **PDF Operations**: Downloads and parsing with success/failure status
7. **Memory Operations**: Message storage between agents
8. **Errors**: Any failures with full context

### Event Types

Each line in `trace.jsonl` is a JSON object with these event types:

- `workflow_start` - Workflow begins with configuration
- `workflow_complete` - Workflow ends with success/failure status
- `agent_init` - Agent initialization
- `agent_action` - Agent performs an action
- `llm_request` - LLM API request with parameters
- `llm_response` - LLM API response with tokens
- `tool_call` - Tool invocation by LLM
- `decision` - Orchestrator decision
- `pdf_operation` - PDF download or parsing
- `memory_operation` - Inter-agent message passing
- `error` - Error occurred

### Analyzing Traces

**Count events by type:**
```sh
cat trace.jsonl | grep -o '"event": "[^"]*"' | sort | uniq -c
```

**View all LLM requests:**
```sh
grep '"event": "llm_request"' trace.jsonl | jq .
```

**Check token usage:**
```sh
grep '"event": "llm_response"' trace.jsonl | jq '.tokens.total' | awk '{sum+=$1} END {print "Total tokens:", sum}'
```

**View workflow timeline:**
```sh
cat trace.jsonl | jq -r '[.timestamp, .event, .agent // .action // ""] | @tsv'
```

**Find errors:**
```sh
grep '"event": "error"' trace.jsonl | jq .
```

### Output Files

- **trace.jsonl**: Structured JSONL log of all events (gitignored)
- **research_copilot.log**: Human-readable logs (gitignored)

Both files are created automatically on each run and provide complementary views of the workflow.

## Example

```sh
python main.py --topic "Sustainable AI"
```

## Logs

All runs are logged to `research_copilot.log` with timestamps, configuration details, and progress information.

## License
See LICENSE file for details.
