import os
import json
from datetime import datetime
from data_loader import get_arxiv_papers, extract_text_from_pdf
from vector_db import create_vector_store

def build_knowledge_base():
    print("Building quantitative finance knowledge base...")
    
    # Fetch papers
    papers = get_arxiv_papers(
        query="quantitative finance OR econophysics OR stochastic volatility",
        max_results=100  # Reduced for testing
    )
    
    if not papers:
        print("No papers retrieved from ArXiv.")
        return

    print(f"Retrieved {len(papers)} papers from ArXiv")
    
    # Process documents
    documents = []
    for i, paper in enumerate(papers):
        try:
            print(f"Processing [{i+1}/{len(papers)}]: {paper['title']}")
            text = extract_text_from_pdf(paper['pdf_url'])
            if not text or len(text.strip()) == 0:
                print(f"Warning: No text extracted from {paper['title']}")
                continue
                
            metadata = {
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "published": paper.get("published", datetime.now()).strftime("%Y-%m-%d"),
                "url": paper.get("pdf_url", ""),
                "source": "ArXiv"
            }
            documents.append({"text": text, "metadata": metadata})
        except Exception as e:
            print(f"Error processing {paper.get('title', 'Unknown')}: {str(e)}")

    if not documents:
        print("No documents processed successfully.")
        return

    # Create and save vector store
    vector_store = create_vector_store(documents)
    base_dir = os.environ.get('KNOWLEDGE_BASE', os.getcwd())
    index_path = os.path.join(base_dir, "quant_finance_index")
    vector_store.save_local(index_path)

    # Save metadata
    metadata_path = os.path.join(base_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump([doc["metadata"] for doc in documents], f, ensure_ascii=False, indent=2)

    print(f"Knowledge base saved to {index_path}")

if __name__ == "__main__":
    build_knowledge_base()