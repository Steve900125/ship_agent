from pathlib import Path
from typing import List
from .load import check_folder_changes, pdf_loader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import shutil
from langchain_core.documents.base import Document

FROCE_UPDATE = False

def init_rag_process(doc_path: Path, files_record_path: Path, db_path: Path) -> Chroma:
    """
    Initializes the RAG (Retrieval-Augmented Generation) process. If no changes are detected 
    in the files, it directly reads the existing database. Otherwise, it deletes the database 
    and rebuilds it.

    Args:
        doc_path (Path): Path to the directory containing the documents (PDF files) to process.
        files_record_path (Path): Path to the file that records the current state of the documents.
        db_path (Path): Path to the directory where the Chroma vector database is stored.

    Returns:
        Chroma: The Chroma vector store object.

    Raises:
        FileNotFoundError: If the `doc_path` or `files_record_path` does not exist.
        ValueError: If an unexpected error occurs during file processing.
    """
    # Check for changes in the document directory
    changes, _, _ = check_folder_changes(doc_path, files_record_path)

    # Initialize the embedding model
    embeddings = HuggingFaceEmbeddings(model_name="ibm-granite/granite-embedding-278m-multilingual")

    if changes or FROCE_UPDATE:
        # Changes detected, rebuild the database
        if db_path.exists():
            print(f"Changes detected, deleting the existing database: {db_path}")
            shutil.rmtree(db_path)

        # Reload documents and rebuild the database
        filter_docs = pdf_loader(doc_path)
        vectorstore = Chroma.from_documents(
            documents=filter_docs,
            embedding=embeddings,
            persist_directory=str(db_path)
        )
       
        print("Database rebuilt and saved.")
    else:
        # No changes detected, load the existing database
        print("No changes detected, loading the existing database.")
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=str(db_path)
        )

    return vectorstore

if __name__ == '__main__':
    AGENT_ROOT = Path(__file__).resolve().parents[1]
    doc_path = AGENT_ROOT / "documents" / "law"
    CHROMA_DB_PATH = Path(__file__).resolve().parents[1] / "law_chroma_db"
  
    files_record_path =  doc_path / "files_record.json"
    print(doc_path, files_record_path)
    print(CHROMA_DB_PATH)
    vector = init_rag_process(doc_path, files_record_path, CHROMA_DB_PATH)
    print(vector.similarity_search("航運經驗定義"))



