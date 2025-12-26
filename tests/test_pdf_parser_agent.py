from unittest.mock import MagicMock, patch

from src.agents.pdf_parser_agent import PDFParserAgent


def test_parse_pdf_happy_path():
    fake_page1 = MagicMock()
    fake_page1.extract_text.return_value = "Page 1 text"
    fake_page2 = MagicMock()
    fake_page2.extract_text.return_value = "Page 2 text"

    fake_pdf = MagicMock()
    fake_pdf.pages = [fake_page1, fake_page2]

    class FakeContextManager:
        def __enter__(self):
            return fake_pdf

        def __exit__(self, exc_type, exc, tb):
            return False

    parser = PDFParserAgent()

    with patch("src.agents.pdf_parser_agent.pdfplumber.open", return_value=FakeContextManager()):
        text = parser.parse_pdf("dummy.pdf")

    assert "Page 1 text" in text
    assert "Page 2 text" in text
    assert "\n" in text


def test_parse_pdf_on_error_returns_empty_string():
    parser = PDFParserAgent()

    with patch("src.agents.pdf_parser_agent.pdfplumber.open", side_effect=Exception("boom")):
        text = parser.parse_pdf("dummy.pdf")

    assert text == ""
