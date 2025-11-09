"""
SynthesizerAgent: Uses OpenAIAgent to synthesize insights and gaps across summaries.
Stub for assignment structure.
"""

from utils.trace_logger import get_trace_logger

class SynthesizerAgent:
    def __init__(self, openai_agent):
        self.openai_agent = openai_agent
        self.trace_logger = get_trace_logger()
        self.trace_logger.log_agent_init("SynthesizerAgent")

    def synthesize(self, summaries):
        """
        Synthesize cross-paper insights and gaps from a list of summaries using OpenAIAgent.
        Returns a synthesis result (dict or string).
        """
        self.trace_logger.log_agent_action("SynthesizerAgent", "synthesize_start",
                                          {"num_summaries": len(summaries)})
        joined_summaries = "\n\n".join(s['summary'] for s in summaries if s.get('summary'))
        prompt = (
            "Given the following research paper summaries, synthesize the main cross-paper insights and identify key research gaps. "
            "Present insights and gaps in a structured format.\n\n"
            f"Summaries:\n{joined_summaries}"
        )
        try:
            synthesis = self.openai_agent.handle_message(prompt)
            self.trace_logger.log_agent_action("SynthesizerAgent", "synthesize_complete",
                                              {"synthesis_length": len(synthesis)})
            return {"synthesis": synthesis}
        except Exception as e:
            print(f"Error synthesizing summaries: {e}")
            self.trace_logger.log_error("SynthesizerAgent", f"Error synthesizing summaries: {str(e)}")
            return {"synthesis": ""}
