"""
SurveyWriterAgent: Uses OpenAIAgent to generate the final mini-survey with citations.
Stub for assignment structure.
"""

from utils.trace_logger import get_trace_logger

class SurveyWriterAgent:
    def __init__(self, openai_agent):
        self.openai_agent = openai_agent
        self.trace_logger = get_trace_logger()
        self.trace_logger.log_agent_init("SurveyWriterAgent")

    def write_survey(self, synthesis, summaries):
        """
        Generate a concise mini-survey (≤800 words) with inline citations using OpenAIAgent.
        Returns the survey as a string.
        """
        self.trace_logger.log_agent_action("SurveyWriterAgent", "write_survey_start",
                                          {"num_summaries": len(summaries)})
        # Prepare context for the prompt
        joined_summaries = "\n\n".join(f"Paper {i+1}: {s['summary']}" for i, s in enumerate(summaries) if s.get('summary'))
        prompt = (
            "Write a concise mini-survey (≤800 words) on the following topic, synthesizing the provided insights and summaries. "
            "Include inline citations in the form [Paper 1], [Paper 2], etc.\n\n"
            f"Synthesis:\n{synthesis.get('synthesis', '')}\n\n"
            f"Summaries:\n{joined_summaries}\n\n"
            "The survey should be clear, well-structured, and highlight key trends, gaps, and future directions."
        )
        try:
            survey = self.openai_agent.handle_message(prompt)
            self.trace_logger.log_agent_action("SurveyWriterAgent", "write_survey_complete",
                                              {"survey_length": len(survey), "word_count": len(survey.split())})
            return survey
        except Exception as e:
            print(f"Error writing survey: {e}")
            self.trace_logger.log_error("SurveyWriterAgent", f"Error writing survey: {str(e)}")
            return ""
