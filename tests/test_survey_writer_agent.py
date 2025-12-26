from unittest.mock import MagicMock

from src.agents.survey_writer_agent import SurveyWriterAgent


def test_write_survey_happy_path():
    openai_agent = MagicMock()
    openai_agent.handle_message.return_value = "survey body"

    agent = SurveyWriterAgent(openai_agent)

    synthesis = {"synthesis": "synth text"}
    summaries = [
        {"summary": "sum1"},
        {"summary": "sum2"},
    ]

    survey = agent.write_survey(synthesis, summaries)

    openai_agent.handle_message.assert_called_once()
    assert survey == "survey body"


def test_write_survey_handles_exception():
    openai_agent = MagicMock()
    openai_agent.handle_message.side_effect = Exception("fail")

    agent = SurveyWriterAgent(openai_agent)

    survey = agent.write_survey({"synthesis": "synth"}, [{"summary": "sum1"}])

    assert survey == ""
