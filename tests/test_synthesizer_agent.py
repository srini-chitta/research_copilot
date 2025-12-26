from unittest.mock import MagicMock

from src.agents.synthesizer_agent import SynthesizerAgent


def test_synthesize_happy_path():
    openai_agent = MagicMock()
    openai_agent.handle_message.return_value = "synthesis text"

    agent = SynthesizerAgent(openai_agent)

    summaries = [
        {"summary": "sum1"},
        {"summary": "sum2"},
    ]

    result = agent.synthesize(summaries)

    openai_agent.handle_message.assert_called_once()
    assert result["synthesis"] == "synthesis text"


def test_synthesize_handles_exception():
    openai_agent = MagicMock()
    openai_agent.handle_message.side_effect = Exception("fail")

    agent = SynthesizerAgent(openai_agent)

    summaries = [{"summary": "sum1"}]

    result = agent.synthesize(summaries)

    assert result["synthesis"] == ""
