from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub

class QuantFinanceAgent:
    def __init__(self, vector_store):
        """
        Initialize the agent with a vector store.
        
        Args:
            vector_store: Pre-loaded vector store for document retrieval
        """
        self.retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
        self.llm = HuggingFaceHub(
            repo_id="google/flan-t5-xxl",
            model_kwargs={"temperature": 0.1, "max_length": 512}
        )
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )

    def query(self, question: str):
        """Execute financial query and return answer with sources."""
        result = self.qa({"query": f"Quantitative finance context: {question}"})
        return {
            "result": result.get("result", ""),
            "source_documents": result.get("source_documents", [])
        }