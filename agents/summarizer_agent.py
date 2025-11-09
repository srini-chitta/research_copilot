"""
SummarizerAgent: Uses OpenAIAgent to summarize text.
Stub for assignment structure.
"""

from utils.trace_logger import get_trace_logger

class SummarizerAgent:
    def __init__(self, openai_agent):
        self.openai_agent = openai_agent
        self.trace_logger = get_trace_logger()
        self.trace_logger.log_agent_init("SummarizerAgent")

    def summarize(self, text, metadata=None):
        """
        Summarize the given text using the OpenAIAgent.
        Returns a structured summary (dict or string).
        """
        self.trace_logger.log_agent_action("SummarizerAgent", "summarize_start",
                                          {"text_length": len(text), "metadata": metadata})
        prompt = (
            "Summarize the following research paper text in a structured format: "
            "- Main contributions\n- Methods\n- Key findings\n- Limitations\n- Citation (if available)\n"
            "Text:\n" + (text[:4000] if text else "")  # Truncate for token safety
        )
        try:
            summary = self.openai_agent.handle_message(prompt)
            self.trace_logger.log_agent_action("SummarizerAgent", "summarize_complete",
                                              {"summary_length": len(summary), "metadata": metadata})
            return {"summary": summary, "metadata": metadata}
        except Exception as e:
            print(f"Error summarizing text: {e}")
            self.trace_logger.log_error("SummarizerAgent", f"Error summarizing text: {str(e)}")
            return {"summary": "", "metadata": metadata}
