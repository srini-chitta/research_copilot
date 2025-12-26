from unittest.mock import MagicMock

from src.agents.summarizer_agent import SummarizerAgent


def test_summarize_happy_path():
    openai_agent = MagicMock()
    openai_agent.handle_message.return_value = "summary text"

    agent = SummarizerAgent(openai_agent)

    result = agent.summarize("some long text", metadata={"pdf_path": "paper1.pdf"})

    openai_agent.handle_message.assert_called_once()
    assert result["summary"] == "summary text"
    assert result["metadata"]["pdf_path"] == "paper1.pdf"


def test_summarize_handles_exception():
    openai_agent = MagicMock()
    openai_agent.handle_message.side_effect = Exception("boom")

    agent = SummarizerAgent(openai_agent)

    result = agent.summarize("some text", metadata={"pdf_path": "paper1.pdf"})

    assert result["summary"] == ""
    assert result["metadata"]["pdf_path"] == "paper1.pdf"
