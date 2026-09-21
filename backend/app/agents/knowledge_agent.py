import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.tools import create_retriever_tool
from dotenv import load_dotenv

load_dotenv()

class KnowledgeAgent:
    def __init__(self, data_path: str = "app/data/nigerian_ailments.md", persist_directory: str = "./faiss_index"):
        self.data_path = data_path
        self.persist_directory = persist_directory
        
        # Use fastembed (very lightweight, no torch required)
        self.embedding_function = FastEmbedEmbeddings()
        self.vectorstore = self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        # Check if database already exists
        if os.path.exists(self.persist_directory):
            print("Loading existing FAISS database...")
            return FAISS.load_local(self.persist_directory, self.embedding_function, allow_dangerous_deserialization=True)
        
        print("Creating new FAISS database from documents...")
        # Load the mock medical data
        loader = TextLoader(self.data_path)
        docs = loader.load()

        # Split into manageable chunks
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)

        # Create and persist the vector database
        vectorstore = FAISS.from_documents(documents=splits, embedding=self.embedding_function)
        vectorstore.save_local(self.persist_directory)
        return vectorstore
    
    def get_retriever_tool(self):
        """Returns a LangChain tool that the Assessment Agent can use to search the medical database."""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        tool = create_retriever_tool(
            retriever,
            "search_medical_guidelines",
            "Search for symptoms, diseases, and emergency red flags. Use this tool BEFORE diagnosing or triaging a patient to ensure factual accuracy."
        )
        return tool

# Singleton instance for the app
knowledge_agent = KnowledgeAgent()
