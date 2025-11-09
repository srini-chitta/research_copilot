# Observability Implementation

## Overview

This project implements comprehensive observability through structured logging to `trace.jsonl`. Every significant step in the multi-agent workflow is captured in JSON Lines (JSONL) format, enabling detailed analysis, debugging, and monitoring.

## Implementation

### TraceLogger Class

The `utils/trace_logger.py` module provides a thread-safe singleton `TraceLogger` class that handles all structured logging:

```python
from utils.trace_logger import get_trace_logger

trace_logger = get_trace_logger("trace.jsonl")
```

### Thread Safety

The TraceLogger uses file locking (`fcntl.flock`) to ensure safe concurrent writes from multiple agents and threads.

## Event Types

### 1. Workflow Events

**workflow_start**: Captures the beginning of a workflow run
```json
{
  "event": "workflow_start",
  "timestamp": "2025-11-09T22:49:40.123456",
  "config": {
    "model": "gpt-4o",
    "temperature": 0.0,
    "seed": 42,
    "topic": "Human-Centered AI",
    "pdf_folder": "pdfs_downloaded",
    "output_file": "mini_survey.txt"
  }
}
```

**workflow_complete**: Captures workflow completion
```json
{
  "event": "workflow_complete",
  "timestamp": "2025-11-09T22:50:15.987654",
  "output_file": "mini_survey.txt",
  "success": true
}
```

### 2. Agent Events

**agent_init**: When an agent is initialized
```json
{
  "event": "agent_init",
  "agent": "PDFMinerAgent",
  "timestamp": "2025-11-09T22:49:41.456789",
  "config": {
    "topic": "Human-Centered AI",
    "download_dir": "pdfs_downloaded"
  }
}
```

**agent_action**: Agent-specific actions
```json
{
  "event": "agent_action",
  "agent": "PDFMinerAgent",
  "action": "mining_complete",
  "timestamp": "2025-11-09T22:49:45.234567",
  "details": {
    "papers_downloaded": 6
  }
}
```

### 3. LLM Events

**llm_request**: Captures LLM API requests
```json
{
  "event": "llm_request",
  "agent": "openai_agent",
  "model": "gpt-4o",
  "prompt_preview": "Summarize the following research paper...",
  "prompt_length": 4160,
  "temperature": 0.0,
  "seed": 42,
  "timestamp": "2025-11-09T22:49:46.003379"
}
```

**llm_response**: Captures LLM API responses
```json
{
  "event": "llm_response",
  "agent": "openai_agent",
  "response_preview": "**Main Contributions:**\n1. The paper...",
  "response_length": 1816,
  "tokens": {
    "prompt": 1163,
    "completion": 326,
    "total": 1489
  },
  "system_fingerprint": "fp_cbf1785567",
  "timestamp": "2025-11-09T22:49:50.035436"
}
```

**tool_call**: Captures tool invocations by LLM (if any)
```json
{
  "event": "tool_call",
  "agent": "openai_agent",
  "tool_name": "search_papers",
  "tool_input": {"query": "machine learning"},
  "timestamp": "2025-11-09T22:49:51.123456"
}
```

### 4. Decision Events

**decision**: Orchestrator decisions with reasoning
```json
{
  "event": "decision",
  "component": "orchestrator",
  "decision": "use_existing_pdfs",
  "reason": "PDF folder provided: pdfs_downloaded",
  "timestamp": "2025-11-09T22:49:42.567890"
}
```

### 5. PDF Operations

**pdf_operation**: PDF downloads and parsing
```json
{
  "event": "pdf_operation",
  "agent": "PDFParserAgent",
  "operation": "parse",
  "file": "paper_1.pdf",
  "success": true,
  "text_length": 45678,
  "timestamp": "2025-11-09T22:49:43.789012"
}
```

### 6. Memory Operations

**memory_operation**: Inter-agent message passing
```json
{
  "event": "memory_operation",
  "operation": "store",
  "thread_id": "pdf_parsing_results",
  "message_count": 6,
  "timestamp": "2025-11-09T22:49:44.890123"
}
```

### 7. Error Events

**error**: Captures errors with context
```json
{
  "event": "error",
  "agent": "PDFParserAgent",
  "error_type": "PDFParseError",
  "error_message": "Failed to parse PDF: corrupted file",
  "context": {
    "file": "bad_paper.pdf"
  },
  "timestamp": "2025-11-09T22:49:45.901234"
}
```

## Instrumentation Points

### All Agents
- Initialization with configuration
- Start and completion of major actions
- Errors with context

### ReproducibleOpenAIAgent
- Every LLM request with model, prompt preview, temperature, seed
- Every LLM response with tokens, response preview, system_fingerprint
- Tool calls (if LLM invokes any tools)

### Orchestrator
- All workflow decisions (use PDF miner vs existing PDFs, start parsing, etc.)
- Agent action completions
- Memory operations between agents

### Individual Agents
- **PDFMinerAgent**: Paper searches, downloads, errors
- **PDFParserAgent**: Parsing operations with success/failure
- **SummarizerAgent**: Summarization start/complete with text lengths
- **SynthesizerAgent**: Synthesis operations
- **SurveyWriterAgent**: Survey writing with word counts

## Analysis Examples

### Count Event Types
```bash
cat trace.jsonl | grep -o '"event": "[^"]*"' | sort | uniq -c
```

Output:
```
  30 "event": "agent_action"
   6 "event": "agent_init"
   5 "event": "decision"
   8 "event": "llm_request"
   8 "event": "llm_response"
  14 "event": "memory_operation"
   6 "event": "pdf_operation"
   1 "event": "workflow_complete"
   1 "event": "workflow_start"
```

### Total Token Usage
```bash
grep '"event": "llm_response"' trace.jsonl | jq '.tokens.total' | awk '{sum+=$1} END {print "Total tokens:", sum}'
```

### Workflow Timeline
```bash
cat trace.jsonl | jq -r '[.timestamp, .event, .agent // .action // ""] | @tsv'
```

### Find Errors
```bash
grep '"event": "error"' trace.jsonl | jq .
```

### LLM Request Details
```bash
grep '"event": "llm_request"' trace.jsonl | jq '{model, temperature, seed, prompt_length}'
```

### Agent Performance
```bash
# Time between agent_init and action completion for each agent
cat trace.jsonl | jq -r 'select(.event == "agent_init" or .event == "agent_action") | [.timestamp, .agent, .event, .action // ""] | @tsv'
```

### PDF Processing Status
```bash
# Check success/failure of PDF operations
grep '"event": "pdf_operation"' trace.jsonl | jq '{file, operation, success}'
```

## Benefits

1. **Debugging**: Trace exact execution flow and identify where issues occur
2. **Performance Analysis**: Measure time spent in each component
3. **Cost Tracking**: Monitor LLM token usage across runs
4. **Reproducibility**: Verify exact LLM parameters used in each request
5. **Audit Trail**: Complete record of all decisions and actions
6. **Monitoring**: Detect patterns, failures, or anomalies across runs

## File Format

- **Format**: JSON Lines (JSONL) - one JSON object per line
- **Timestamps**: ISO 8601 format with microsecond precision
- **Size**: Typical run generates ~20-50KB of trace data
- **Location**: `trace.jsonl` in project root (gitignored)

## Integration

The trace logging is automatically initialized in `main.py`:

```python
from utils.trace_logger import get_trace_logger

# Initialize trace logger
trace_logger = get_trace_logger(config.TRACE_FILE)

# Log workflow start
trace_logger.log_workflow_start(run_config)

# ... orchestrator runs ...

# Log workflow completion
trace_logger.log_workflow_complete(output_file, success=True)
```

All agents receive the trace logger and use it throughout their lifecycle.

## Comparison with Other Logs

| File | Format | Purpose | Audience |
|------|--------|---------|----------|
| `trace.jsonl` | Structured JSON | Machine-readable detailed trace | Analysis tools, monitoring |
| `research_copilot.log` | Plain text | Human-readable run log | Developers, debugging |
| `*_config.json` | JSON | Run configuration | Reproducibility |

## Best Practices

1. **Analyze after runs**: Use jq and grep to understand workflow behavior
2. **Monitor token usage**: Track costs across multiple runs
3. **Debug with trace**: When issues occur, check trace.jsonl first
4. **Archive important traces**: Save trace files for significant runs
5. **Filter noise**: Use jq to focus on specific event types of interest

## Future Enhancements

Potential improvements:
- Real-time trace streaming to monitoring dashboard
- Trace aggregation and visualization tools
- Anomaly detection on trace patterns
- Performance profiling based on trace data
- Integration with observability platforms (Datadog, New Relic, etc.)
