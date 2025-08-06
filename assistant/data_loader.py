import arxiv
import requests
from bs4 import BeautifulSoup
import pdfplumber
import re
import tempfile
import os
from typing import List, Dict, Optional
import time

def get_arxiv_papers(query: str, max_results: int = 10) -> List[Dict]:
    """
    Fetch papers from ArXiv and return metadata.
    Args:
        query (str): Search query for ArXiv.
        max_results (int): Maximum number of results to fetch.
    Returns:
        List[Dict]: List of paper metadata dictionaries.
    """
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
    """
    Extract text from a PDF at a given URL.
    Args:
        url (str): URL to the PDF file.
    Returns:
        str: Extracted text from the PDF, or empty string on failure.
    """
    try:
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            tmp_path = tmp_file.name
        text = []
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        os.remove(tmp_path)
        return " ".join(text)
    except Exception as e:
        print(f"Error extracting text from {url}: {str(e)}")
        return ""

def extract_text_from_local_pdf(file_path: str) -> str:
    """
    Extract text from a local PDF file.
    Args:
        file_path (str): Path to the local PDF file.
    Returns:
        str: Extracted text from the PDF, or empty string on failure.
    """
    try:
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return " ".join(text)
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
        return ""

def extract_text_from_html(url: str, selector: Optional[str] = None) -> str:
    """
    Extract text from an HTML page at a given URL.
    Args:
        url (str): URL to the HTML page.
        selector (Optional[str]): CSS selector to target specific content.
    Returns:
        str: Extracted text from the HTML page.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        if selector:
            elements = soup.select(selector)
            text = " ".join([el.get_text(separator=" ", strip=True) for el in elements])
        else:
            text = soup.get_text(separator=" ", strip=True)
        return text
    except Exception as e:
        print(f"Error extracting text from HTML {url}: {str(e)}")
        return ""

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace and non-printable characters.
    Args:
        text (str): Raw text to clean.
    Returns:
        str: Cleaned text.
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)
    return text.strip()