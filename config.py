"""
Configuration file for Research Co-Pilot.
Contains reproducibility parameters and other settings.
"""

# LLM Configuration for Reproducibility
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0  # Set to 0 for deterministic output
DEFAULT_SEED = 42  # Fixed seed for reproducibility
DEFAULT_MAX_TOKENS = 4096

# Agent Configuration
AGENT_NAME = "openai_agent"
AGENT_TYPE = "ChatAgent"
IS_STREAMING = False

# Output Configuration
DEFAULT_OUTPUT_FILE = "mini_survey.txt"
DEFAULT_DOWNLOAD_DIR = "pdfs_downloaded"

# Logging Configuration
LOG_FILE = "research_copilot.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Observability Configuration
TRACE_FILE = "trace.jsonl"  # Structured trace file for observability
