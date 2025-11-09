"""
PDFMinerAgent: Mines/downloads PDFs from open research sites given a topic.
Stub for assignment structure.
"""


import os
import requests
from urllib.parse import urlencode
from xml.etree import ElementTree
from utils.trace_logger import get_trace_logger

class PDFMinerAgent:
    def __init__(self, topic, download_dir):
        self.topic = topic
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.trace_logger = get_trace_logger()
        self.trace_logger.log_agent_init("PDFMinerAgent", {"topic": topic, "download_dir": download_dir})

    def mine_pdfs(self, max_papers=6):
        """
        Search arXiv for the topic and download up to max_papers PDFs.
        Returns a list of file paths to downloaded PDFs.
        """
        self.trace_logger.log_agent_action("PDFMinerAgent", "search_arxiv",
                                          {"topic": self.topic, "max_papers": max_papers})
        # Search arXiv API
        base_url = "http://export.arxiv.org/api/query?"
        query = {
            "search_query": f"all:{self.topic}",
            "start": 0,
            "max_results": max_papers
        }
        url = base_url + urlencode(query)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"arXiv API error: {response.status_code}")
            self.trace_logger.log_error("PDFMinerAgent", f"arXiv API error: {response.status_code}")
            return []
        # Parse XML
        root = ElementTree.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        pdf_links = []
        for entry in entries:
            for link in entry.findall('atom:link', ns):
                if link.attrib.get('title') == 'pdf':
                    pdf_links.append(link.attrib['href'])
        # Download PDFs
        file_paths = []
        for i, pdf_url in enumerate(pdf_links):
            try:
                pdf_resp = requests.get(pdf_url)
                if pdf_resp.status_code == 200:
                    file_path = os.path.join(self.download_dir, f"paper_{i+1}.pdf")
                    with open(file_path, 'wb') as f:
                        f.write(pdf_resp.content)
                    file_paths.append(file_path)
                    self.trace_logger.log_pdf_operation("PDFMinerAgent", "download", file_path, success=True)
                else:
                    print(f"Failed to download {pdf_url}")
                    self.trace_logger.log_pdf_operation("PDFMinerAgent", "download", pdf_url, 
                                                       success=False, error=f"HTTP {pdf_resp.status_code}")
            except Exception as e:
                print(f"Error downloading {pdf_url}: {e}")
                self.trace_logger.log_error("PDFMinerAgent", f"Error downloading {pdf_url}: {str(e)}")
        
        self.trace_logger.log_agent_action("PDFMinerAgent", "mining_complete", 
                                          {"downloaded": len(file_paths), "requested": max_papers})
        return file_paths
