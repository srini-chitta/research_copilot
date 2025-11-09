"""
CLI entrypoint for the research co-pilot assignment.
"""

import argparse
import os
import sys
import logging
import json
from datetime import datetime
from agents import (
    PDFMinerAgent,
    PDFParserAgent,
    SummarizerAgent,
    SynthesizerAgent,
    SurveyWriterAgent,
    ReproducibleOpenAIAgent
)
from orchestrator import ResearchCopilotOrchestrator
from utils.trace_logger import get_trace_logger
import config

from moya.agents.openai_agent import OpenAIAgentConfig

logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Research Co-Pilot: Multi-agent research survey generator")
    parser.add_argument('--topic', type=str, help='Research topic to mine papers for (uses arXiv)')
    parser.add_argument('--pdf-folder', type=str, help='Folder containing PDF files to process')
    parser.add_argument('--output', type=str, default=config.DEFAULT_OUTPUT_FILE, help='Output file for the mini-survey')
    parser.add_argument('--openai-api-key', type=str, default=None, help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--temperature', type=float, default=config.DEFAULT_TEMPERATURE, help='LLM temperature for reproducibility (default: 0.0)')
    parser.add_argument('--seed', type=int, default=config.DEFAULT_SEED, help='Random seed for reproducibility (default: 42)')
    parser.add_argument('--model', type=str, default=config.DEFAULT_MODEL, help='OpenAI model to use (default: gpt-4o)')
    args = parser.parse_args()

    api_key = args.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key required. Use --openai-api-key or set OPENAI_API_KEY env var.")
        sys.exit(1)
    
    run_config = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "temperature": args.temperature,
        "seed": args.seed,
        "topic": args.topic,
        "pdf_folder": args.pdf_folder,
        "output_file": args.output
    }
    logger.info("=== Research Co-Pilot Run Configuration ===")
    logger.info(f"Configuration: {json.dumps(run_config, indent=2)}")
    
    trace_logger = get_trace_logger(config.TRACE_FILE)
    trace_logger.log_workflow_start(run_config)
    
    openai_agent = ReproducibleOpenAIAgent(
        config=OpenAIAgentConfig(
            agent_name=config.AGENT_NAME,
            description="LLM agent for summarization, synthesis, and survey writing",
            api_key=api_key,
            model_name=args.model,
            agent_type=config.AGENT_TYPE,
            is_streaming=config.IS_STREAMING
        ),
        temperature=args.temperature,
        seed=args.seed
    )

    logger.info("Initializing agents...")
    pdf_miner = PDFMinerAgent(args.topic, download_dir=config.DEFAULT_DOWNLOAD_DIR)
    pdf_parser = PDFParserAgent()
    summarizer = SummarizerAgent(openai_agent)
    synthesizer = SynthesizerAgent(openai_agent)
    survey_writer = SurveyWriterAgent(openai_agent)

    orchestrator = ResearchCopilotOrchestrator(
        pdf_miner, pdf_parser, summarizer, synthesizer, survey_writer
    )

    logger.info("Starting research workflow...")
    survey = orchestrator.run(topic=args.topic, pdf_folder=args.pdf_folder)
    if survey:
        with open(args.output, 'w') as f:
            f.write(survey)
        logger.info(f"Mini-survey written to {args.output}")
        
        config_output = args.output.replace('.txt', '_config.json')
        with open(config_output, 'w') as f:
            json.dump(run_config, f, indent=2)
        logger.info(f"Run configuration saved to {config_output}")
        
        trace_logger.log_workflow_complete(args.output, success=True)
    else:
        logger.warning("No survey generated.")
        trace_logger.log_workflow_complete("", success=False)

if __name__ == "__main__":
    main()
