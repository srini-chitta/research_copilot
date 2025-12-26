# Research Co-Pilot Architecture

This document captures a high-level architecture diagram for the `research_copilot` project.

## System Overview

```mermaid
flowchart TD
    %% Entry
    CLI["Command Line\n(research_copilot.py / src/main.py)"] --> ORCH["ResearchCopilotOrchestrator\n(src/orchestrator.py)"]

    %% Input selection
    ORCH -->|topic provided| MINER["PDFMinerAgent\n(src/agents/pdf_miner_agent.py)"]
    ORCH -->|pdf_folder provided| FS_PDFS["Local PDF Folder"]

    MINER --> DL_PDFS["Downloaded PDFs\n(pdfs_downloaded/)"]
    DL_PDFS --> ORCH
    FS_PDFS --> ORCH

    %% Parsing
    ORCH --> PARSER["PDFParserAgent\n(src/agents/pdf_parser_agent.py)"]
    PARSER --> PARSED_TEXT["Parsed Text per PDF"]
    PARSED_TEXT --> ORCH

    %% Summarization (per-paper)
    ORCH --> SUMM["SummarizerAgent\n(src/agents/summarizer_agent.py)"]
    SUMM --> SUMMARIES["Per-paper Summaries"]
    SUMMARIES --> ORCH

    %% Synthesis (across papers)
    ORCH --> SYNTH["SynthesizerAgent\n(src/agents/synthesizer_agent.py)"]
    SYNTH --> SYNTHESIS["Cross-paper Synthesis"]
    SYNTHESIS --> ORCH

    %% Survey writing
    ORCH --> SURVEY["SurveyWriterAgent\n(src/agents/survey_writer_agent.py)"]
    SURVEY --> SURVEY_TXT["Mini-survey Text"]

    %% Outputs
    SURVEY_TXT --> OUT["Output Files\n(outputs/mini_survey.txt,\noutputs/*_config.json)"]

    %% LLM + MOYA layer
    subgraph LLM["LLM & MOYA Layer"]
        ROA["ReproducibleOpenAIAgent\n(src/agents/reproducible_agent.py)"]
        OCFG["OpenAIAgentConfig\n(moya.agents.openai_agent)"]
        OPENAI["OpenAI API"]
        ROA --> OPENAI
        OCFG --> ROA
    end

    SUMM --> ROA
    SYNTH --> ROA
    SURVEY --> ROA

    %% Observability
    subgraph OBS["Observability"]
        LOG["Python Logging\nlogs/research_copilot.log"]
        TRACE["Trace Logger\nlogs/trace.jsonl\n(src/utils/trace_logger.py)"]
    end

    CLI --> LOG
    ORCH --> LOG
    MINER --> LOG
    PARSER --> LOG
    SUMM --> LOG
    SYNTH --> LOG
    SURVEY --> LOG

    CLI --> TRACE
    ORCH --> TRACE
    SUMM --> TRACE
    SYNTH --> TRACE
    SURVEY --> TRACE
```

## Notes

- `ReproducibleOpenAIAgent` is constructed in `src/main.py` using `OpenAIAgentConfig` from the MOYA library and then injected into `SummarizerAgent`, `SynthesizerAgent`, and `SurveyWriterAgent`.
- The orchestrator (`ResearchCopilotOrchestrator`) coordinates all agents and decides whether to mine PDFs from arXiv via `PDFMinerAgent` or use an existing local PDF folder.
- Observability is implemented via:
  - Standard Python logging to `logs/research_copilot.log`.
  - A JSONL trace logger (`get_trace_logger`) that records workflow, decisions, LLM requests/responses, and errors into `logs/trace.jsonl`.
