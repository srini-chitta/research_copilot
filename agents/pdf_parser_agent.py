"""
PDFParserAgent: Extracts text from PDF files.
Stub for assignment structure.
"""


import pdfplumber
from utils.trace_logger import get_trace_logger

class PDFParserAgent:
    def __init__(self):
        self.trace_logger = get_trace_logger()
        self.trace_logger.log_agent_init("PDFParserAgent")

    def parse_pdf(self, pdf_path):
        """
        Extract text from a PDF file at pdf_path using pdfplumber.
        Returns the extracted text as a string.
        """
        try:
            self.trace_logger.log_agent_action("PDFParserAgent", "parse_start", {"pdf_path": pdf_path})
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            self.trace_logger.log_pdf_operation("PDFParserAgent", "parse", pdf_path, 
                                               success=True)
            self.trace_logger.log_agent_action("PDFParserAgent", "parse_complete",
                                              {"pdf_path": pdf_path, "text_length": len(text)})
            return text
        except Exception as e:
            print(f"Error parsing {pdf_path}: {e}")
            self.trace_logger.log_pdf_operation("PDFParserAgent", "parse", pdf_path,
                                               success=False, error=str(e))
            return ""
