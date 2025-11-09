# agents/__init__.py
"""
Research Copilot Agents Module
Contains all agent implementations for the multi-agent research system.
"""

from .pdf_miner_agent import PDFMinerAgent
from .pdf_parser_agent import PDFParserAgent
from .summarizer_agent import SummarizerAgent
from .synthesizer_agent import SynthesizerAgent
from .survey_writer_agent import SurveyWriterAgent
from .reproducible_agent import ReproducibleOpenAIAgent

__all__ = [
    'PDFMinerAgent',
    'PDFParserAgent',
    'SummarizerAgent',
    'SynthesizerAgent',
    'SurveyWriterAgent',
    'ReproducibleOpenAIAgent',
]
