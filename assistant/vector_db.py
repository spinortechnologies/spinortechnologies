import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

def create_vector_store(documents):
    """Create and save a vector store from a list of documents."""
    # Split documents (if not already chunked)
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""]
    )
    
    # Create documents from the input
    docs = []
    for doc in documents:
        if isinstance(doc, dict):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            docs.append(Document(page_content=text, metadata=metadata))
        else:
            # Handle other document types if needed
            pass
    
    texts = text_splitter.split_documents(docs)
    
    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = FAISS.from_documents(texts, embeddings)
    return vector_store

def load_vector_store(index_path, embeddings):
    """Load an existing vector store from disk."""
    return FAISS.load_local(index_path, embeddings)