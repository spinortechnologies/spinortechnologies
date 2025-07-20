import arxiv
import requests
from bs4 import BeautifulSoup
import pdfplumber
import re
from typing import List, Dict
import time

def get_arxiv_papers(query: str, max_results: int = 10) -> List[Dict]:
    """Fetch papers from ArXiv and return metadata."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "published": result.published
        })
        time.sleep(1)  # Be respectful of ArXiv API
    return papers

def extract_text_from_pdf(url: str) -> str:
    """Extract text from PDF at a given URL."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        text = []
        with pdfplumber.open(response.raw) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return " ".join(text)
    except Exception as e:
        print(f"Error extracting text from {url}: {str(e)}")
        return ""