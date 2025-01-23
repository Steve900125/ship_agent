import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.documents.base import Document

def pdf_loader(doc_path: Path) -> List:
    """
    Load and process PDF files, ensuring that sentence boundaries are preserved.

    Args:
        doc_path (Path): Path to the directory containing PDF files.
    
    Returns:
        List: Processed documents with improved chunking.
    """
    # 獲取所有 PDF 文件路徑
    pdf_files = get_pdf_document_paths(doc_path)
    pdf_files = [str(file_path) for file_path in pdf_files]

    # 初始化 UnstructuredLoader
    loader = UnstructuredLoader(
        file_path=pdf_files,
        chunking_strategy="by_title",    # 按標題分塊
        max_characters=1000,            # 增大分塊大小以減少切分
        include_orig_elements=False,    # 不包含原始元素
    )

    # 加載文檔
    docs = loader.load()

    # 後處理：自定義切分以保證句子完整
    processed_docs = []
    for doc in docs:
        processed_content = preserve_sentence_boundaries(doc.page_content, max_length=1000)
        for chunk in processed_content:
            processed_docs.append(
                Document(metadata=doc.metadata, page_content=chunk)
            )
    filter_docs = filter_complex_metadata(processed_docs)

    return filter_docs

def preserve_sentence_boundaries(text: str, max_length: int = 1000) -> List[str]:
    """
    Preserve sentence boundaries by splitting text at punctuation marks and respecting max length.

    Args:
        text (str): The input text to be split.
        max_length (int): The maximum allowed length for each chunk.
    
    Returns:
        List[str]: A list of chunks with sentence boundaries preserved.
    """
    sentences = re.split(r'(?<=[。！？.?!])', text)  # 按中文或英文句號、感嘆號、問號切分
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def check_folder_changes(doc_path: Path, files_record_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Check for changes in a folder containing PDF files, comparing the current state with a stored record.
    
    Args:
        doc_path: Path to the directory containing PDF documents.
        files_record_path: Path to the JSON file storing previous file hashes.
    
    Returns:
        has_changes (bool): True if there are changes, False otherwise.
        added_files (List[str]): List of newly added files.
        removed_files (List[str]): List of removed files.
    """
    # Load previous records
    previous_records = load_previous_records(files_record_path)

    # Get current PDF files and their hashes
    current_files = {str(file_path): hash_file(file_path) for file_path in get_pdf_document_paths(doc_path)}

    # Determine added, removed, and changed files
    added_files = [file for file in current_files if file not in previous_records]
    removed_files = [file for file in previous_records if file not in current_files]
    changed_files = [
        file for file in current_files
        if file in previous_records and previous_records[file] != current_files[file]
    ]

    # Determine if there are any changes
    has_changes = bool(added_files or removed_files or changed_files)

    # Save current state to the record file
    save_current_records(current_files, files_record_path)

    return has_changes, added_files, removed_files


def get_pdf_document_paths(doc_path: Path) -> List[Path]:
    """Get a list of PDF document paths from a specified directory."""
    if not doc_path.exists():
        return []
    return [doc_path / doc_name for doc_name in os.listdir(doc_path) if doc_name.lower().endswith(".pdf")]

def hash_file(file_path: Path) -> str:
    """Calculate the MD5 hash of a file."""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def load_previous_records(files_record_path: Path) -> Dict[str, str]:
    """Load the previous records of file hashes from a JSON file."""
    if not files_record_path.exists():
        return {}
    with open(files_record_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_current_records(files_info: Dict[str, str], files_record_path: Path) -> None:
    """
    Save the current records of file hashes to a JSON file.

    Args:
        files_info: Dictionary of file paths and their corresponding MD5 hashes.
        files_record_path: Path to the JSON file for saving the records.
    """
    files_record_path.parent.mkdir(parents=True, exist_ok=True)

    with open(files_record_path, 'w', encoding='utf-8') as f:
        json.dump(files_info, f, ensure_ascii=False, indent=2)


# Example usage
if __name__ == "__main__":
    AGENT_ROOT = Path(__file__).resolve().parents[1]
    folder_path = AGENT_ROOT / "documents" / "system"
    record_file =  folder_path / "files_record.json"

    changes, added, removed, current_files= check_folder_changes(folder_path, record_file)
    print("Changes (New/Modified):", changes)
    print("Added Files:", added)
    print("Removed Files:", removed)

