"""
Orchestrator and workflow logic for the research co-pilot assignment.
Stub for assignment structure.
"""


import os
from memory.ephemeral_memory_setup import EphemeralMemory
from utils.trace_logger import get_trace_logger

class ResearchCopilotOrchestrator:
    def __init__(self, pdf_miner, pdf_parser, summarizer, synthesizer, survey_writer):
        self.pdf_miner = pdf_miner
        self.pdf_parser = pdf_parser
        self.summarizer = summarizer
        self.synthesizer = synthesizer
        self.survey_writer = survey_writer
        self.trace_logger = get_trace_logger()
        
        # Log orchestrator initialization
        self.trace_logger.log_agent_init("Orchestrator", {
            "agents": ["PDFMinerAgent", "PDFParserAgent", "SummarizerAgent", "SynthesizerAgent", "SurveyWriterAgent"]
        })

    def run(self, topic=None, pdf_folder=None, thread_id="default-thread"):
        """
        Main workflow:
        1. (Optional) Use PDFMinerAgent to download PDFs if topic is provided.
        2. Use PDFParserAgent to extract text from PDFs.
        3. Use SummarizerAgent to summarize each paper.
        4. Use SynthesizerAgent to synthesize insights/gaps.
        5. Use SurveyWriterAgent to generate the mini-survey.
        """
        # Step 1: Get PDF file paths
        if topic:
            print(f"Mining PDFs for topic: {topic}")
            self.trace_logger.log_decision("Orchestrator", "use_pdf_miner", 
                                          reason=f"Topic provided: {topic}")
            pdf_paths = self.pdf_miner.mine_pdfs()
            self.trace_logger.log_agent_action("Orchestrator", "pdfs_mined", 
                                              {"count": len(pdf_paths), "topic": topic})
        elif pdf_folder:
            self.trace_logger.log_decision("Orchestrator", "use_existing_pdfs",
                                          reason=f"PDF folder provided: {pdf_folder}")
            pdf_paths = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
            self.trace_logger.log_agent_action("Orchestrator", "pdfs_located",
                                              {"count": len(pdf_paths), "folder": pdf_folder})
        else:
            print("No topic or PDF folder provided.")
            self.trace_logger.log_error("Orchestrator", "No topic or PDF folder provided")
            return None
        if not pdf_paths:
            print("No PDFs found.")
            self.trace_logger.log_error("Orchestrator", "No PDFs found")
            return None

        # Step 2: Parse PDFs
        self.trace_logger.log_decision("Orchestrator", "start_parsing",
                                       reason=f"Processing {len(pdf_paths)} PDFs")
        parsed_texts = []
        for pdf_path in pdf_paths:
            print(f"Parsing {pdf_path}")
            text = self.pdf_parser.parse_pdf(pdf_path)
            EphemeralMemory.store_message(thread_id, "parser", f"Parsed {pdf_path}")
            self.trace_logger.log_memory_operation("store", thread_id, f"Parsed {pdf_path}", "parser")
            parsed_texts.append({"pdf_path": pdf_path, "text": text})

        # Step 3: Summarize each paper
        self.trace_logger.log_decision("Orchestrator", "start_summarization",
                                       reason=f"Summarizing {len(parsed_texts)} papers")
        summaries = []
        for parsed in parsed_texts:
            print(f"Summarizing {parsed['pdf_path']}")
            summary = self.summarizer.summarize(parsed["text"], metadata={"pdf_path": parsed["pdf_path"]})
            EphemeralMemory.store_message(thread_id, "summarizer", f"Summarized {parsed['pdf_path']}")
            self.trace_logger.log_memory_operation("store", thread_id, f"Summarized {parsed['pdf_path']}", "summarizer")
            summaries.append(summary)

        # Step 4: Synthesize insights/gaps
        print("Synthesizing cross-paper insights and gaps")
        self.trace_logger.log_decision("Orchestrator", "start_synthesis",
                                       reason=f"Synthesizing insights from {len(summaries)} summaries")
        synthesis = self.synthesizer.synthesize(summaries)
        EphemeralMemory.store_message(thread_id, "synthesizer", "Synthesized insights and gaps")
        self.trace_logger.log_memory_operation("store", thread_id, "Synthesized insights and gaps", "synthesizer")

        # Step 5: Generate mini-survey
        print("Generating mini-survey")
        self.trace_logger.log_decision("Orchestrator", "start_survey_writing",
                                       reason="All summaries and synthesis complete")
        survey = self.survey_writer.write_survey(synthesis, summaries)
        EphemeralMemory.store_message(thread_id, "survey_writer", "Generated mini-survey")
        self.trace_logger.log_memory_operation("store", thread_id, "Generated mini-survey", "survey_writer")

        self.trace_logger.log_agent_action("Orchestrator", "workflow_steps_complete",
                                          {"total_pdfs": len(pdf_paths), "summaries": len(summaries)})
        return survey
