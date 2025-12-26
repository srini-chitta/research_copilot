from unittest.mock import MagicMock, patch
from xml.etree.ElementTree import Element, SubElement, tostring

from src.agents.pdf_miner_agent import PDFMinerAgent


def _build_arxiv_xml_with_pdf_link(url: str) -> bytes:
    feed = Element("feed", xmlns="http://www.w3.org/2005/Atom")
    entry = SubElement(feed, "entry")
    SubElement(entry, "link", title="pdf", href=url)
    return tostring(feed)


def test_mine_pdfs_happy_path(tmp_path):
    agent = PDFMinerAgent(topic="test", download_dir=str(tmp_path))

    xml_bytes = _build_arxiv_xml_with_pdf_link("http://example.com/paper1.pdf")

    resp_api = MagicMock()
    resp_api.status_code = 200
    resp_api.content = xml_bytes

    resp_pdf = MagicMock()
    resp_pdf.status_code = 200
    resp_pdf.content = b"PDF bytes"

    with patch("src.agents.pdf_miner_agent.requests.get", side_effect=[resp_api, resp_pdf]):
        paths = agent.mine_pdfs(max_papers=1)

    assert len(paths) == 1
    assert paths[0].endswith(".pdf")
    assert (tmp_path / "paper_1.pdf").exists()


def test_mine_pdfs_api_error_returns_empty_list(tmp_path):
    agent = PDFMinerAgent(topic="test", download_dir=str(tmp_path))

    resp_api = MagicMock()
    resp_api.status_code = 500
    resp_api.content = b""

    with patch("src.agents.pdf_miner_agent.requests.get", return_value=resp_api):
        paths = agent.mine_pdfs(max_papers=1)

    assert paths == []
