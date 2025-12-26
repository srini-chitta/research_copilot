import os
from unittest.mock import MagicMock

from src.orchestrator import ResearchCopilotOrchestrator


def test_run_returns_none_when_no_topic_or_folder():
    orchestrator = ResearchCopilotOrchestrator(
        pdf_miner=MagicMock(),
        pdf_parser=MagicMock(),
        summarizer=MagicMock(),
        synthesizer=MagicMock(),
        survey_writer=MagicMock(),
    )

    result = orchestrator.run(topic=None, pdf_folder=None)

    assert result is None


def test_run_with_topic_uses_pdf_miner_and_pipeline():
    pdf_miner = MagicMock()
    pdf_miner.mine_pdfs.return_value = ["paper1.pdf", "paper2.pdf"]

    pdf_parser = MagicMock()
    pdf_parser.parse_pdf.side_effect = ["text1", "text2"]

    summarizer = MagicMock()
    summarizer.summarize.side_effect = [
        {"summary": "sum1", "metadata": {"pdf_path": "paper1.pdf"}},
        {"summary": "sum2", "metadata": {"pdf_path": "paper2.pdf"}},
    ]

    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = {"synthesis": "synth"}

    survey_writer = MagicMock()
    survey_writer.write_survey.return_value = "final survey"

    orchestrator = ResearchCopilotOrchestrator(
        pdf_miner, pdf_parser, summarizer, synthesizer, survey_writer
    )

    result = orchestrator.run(topic="test topic", pdf_folder=None)

    pdf_miner.mine_pdfs.assert_called_once()
    assert pdf_parser.parse_pdf.call_count == 2
    assert summarizer.summarize.call_count == 2
    synthesizer.synthesize.assert_called_once()
    survey_writer.write_survey.assert_called_once()
    assert result == "final survey"


def test_run_with_pdf_folder_uses_existing_pdfs(tmp_path):
    pdf1 = tmp_path / "a.pdf"
    pdf1.write_bytes(b"fake pdf content")
    pdf2 = tmp_path / "b.PDF"
    pdf2.write_bytes(b"fake pdf content")
    other = tmp_path / "not_pdf.txt"
    other.write_text("ignore me")

    pdf_parser = MagicMock()
    pdf_parser.parse_pdf.side_effect = ["text1", "text2"]

    summarizer = MagicMock()
    summarizer.summarize.side_effect = [
        {"summary": "sum1", "metadata": {"pdf_path": str(pdf1)}},
        {"summary": "sum2", "metadata": {"pdf_path": str(pdf2)}},
    ]

    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = {"synthesis": "synth"}

    survey_writer = MagicMock()
    survey_writer.write_survey.return_value = "survey"

    orchestrator = ResearchCopilotOrchestrator(
        pdf_miner=MagicMock(),
        pdf_parser=pdf_parser,
        summarizer=summarizer,
        synthesizer=synthesizer,
        survey_writer=survey_writer,
    )

    result = orchestrator.run(topic=None, pdf_folder=str(tmp_path))

    assert pdf_parser.parse_pdf.call_count == 2
    assert result == "survey"


def test_run_returns_none_when_no_pdfs_found(tmp_path):
    orchestrator = ResearchCopilotOrchestrator(
        pdf_miner=MagicMock(),
        pdf_parser=MagicMock(),
        summarizer=MagicMock(),
        synthesizer=MagicMock(),
        survey_writer=MagicMock(),
    )

    result = orchestrator.run(topic=None, pdf_folder=str(tmp_path))

    assert result is None
