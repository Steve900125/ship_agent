from langchain_core.documents.base import Document
from langchain_core.tools import tool
from pathlib import Path
from typing import List
import sys

FILE = Path(__file__).resolve()
AGENT_ROOT = FILE.parents[1]
sys.path.insert(0, str(AGENT_ROOT))  # for import modules

from rag.rag_process import init_rag_process

@tool(parse_docstring=True)
def get_system_rag_answer(question: str) -> List[Document] | str:
    """
    Perform retrieval-augmented generation (RAG) by querying the vectorstore. 
    The documents primarily consist of major maritime transport accident investigation reports. 
    Use these reports to retrieve relevant information regarding accident causes, solutions, and recommendations. 
    Provide clear, concise, and actionable responses based on the retrieved content.

    Note{
        Answer the users QUESTION using the DOCUMENT text above.
        Keep your answer ground in the facts of the DOCUMENT.
        If the user's question does not require a search, simply 
        ignore the document content and directly respond to the user's original question yourself.
    }

    Args:
        question:   Analyze the query question to extract the most important keywords for similarity search.
                    If no suitable keywords are found, ask the user to refine their query.
                    If the query is irrelevant to the company document information, return an empty string.

    Returns:
        A list of documents relevant to the query from internal company files or str
    """
    print('[Info] call get_system_rag_answer')
    print('[Question]: ', question)

    if not question:
        return "No tools required for this query. Please answer the question by yourself."
    else:
        # Initialize the file paths
        AGENT_ROOT = Path(__file__).resolve().parents[1]
        doc_path = AGENT_ROOT / "documents" / "system"
        files_record_path =  doc_path / "files_record.json"
        chorma_db_path = doc_path / "system_chroma_db"

        # Initialize the RAG process (Get the vectorstore)
        vectorstore = init_rag_process(
                doc_path= doc_path,
                files_record_path= files_record_path,
                db_path= chorma_db_path 
            )

        # Perform similarity search
        docs = vectorstore.similarity_search(question)

        return docs