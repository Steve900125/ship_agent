from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path
import sqlite3
from datetime import datetime

# Define the database path in the current directory
PATH = Path(__file__).resolve().parent
DB_PATH = PATH / "conversations.db"


def fetch_recent_conversations(
    db_path: Path, user_id: str, limit: int
) -> Optional[List[Dict[str, str]]]:
    """
    Fetches recent conversation records for a given user ID.

    Args:
        db_path (Path): Path to the SQLite database file.
        user_id (str): The unique identifier for the user whose conversations are to be retrieved.
        limit (int): The number of recent records to fetch.

    Returns:
        Optional[List[Dict[str, str]]]: A list of dictionaries representing conversation records, or None if empty.
    """
    select_sql = """
    SELECT user_message, ai_message, timestamp
    FROM conversation_records
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?;
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(select_sql, (user_id, limit))
        rows = cursor.fetchall()

    if rows:
        return [
            {"user_message": row[0], "ai_message": row[1], "timestamp": row[2]}
            for row in rows
        ]
    return None


def format_conversation_to_history(chat_history: Optional[List[Dict[str, str]]]):
    """
    Converts chat history to a format usable by initial history.

    Args:
        chat_history (Optional[List[Dict[str, str]]]): The chat history to format.

    Returns:
        List: Formatted initial history list.
    """
    initial_history = []
    if chat_history is not None:
        for row_data in chat_history:
            initial_history.append(HumanMessage(content=row_data["user_message"]))
            initial_history.append(AIMessage(content=row_data["ai_message"]))
    else:
        print("No sufficient history messages from this user")
    return initial_history


def save_data(user: dict, agent: dict, db_path: Path):
    """
    Saves a conversation record to a SQLite database.

    Args:
        user (dict): User message data containing user_id, user_message, and timestamp.
        agent (dict): Agent message data containing ai_message and timestamp.
        db_path (Path): Path to the SQLite database file.

    Returns:
        None
    """
    insert_sql = """
        INSERT INTO conversation_records (user_id, user_message, ai_message, timestamp)
        VALUES (?, ?, ?, ?);
    """

    try:
        # Connect to SQLite database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Format timestamp
            timestamp_dt = datetime.fromtimestamp(user["timestamp"] / 1000.0)

            # Prepare data
            conversation_data = (
                user["user_id"],
                user["user_message"],
                agent["agent_message"],
                timestamp_dt,
            )

            # Insert data
            cursor.execute(insert_sql, conversation_data)
            conn.commit()
            print("Conversation inserted successfully.")

    except sqlite3.DatabaseError as e:
        print(f"Error saving data: {e}")



def get_history(user_id: str, limit: int):
    """
    Fetches recent conversation records for a given user ID.

    Args:
        user_id (str): The unique identifier for the user whose conversations are to be retrieved.
        limit (int): The number of recent records to fetch.

    Returns:
        Optional[List[Dict[str, str]]]: A list of dictionaries representing conversation records, or None if empty.
    """
    chat_history = fetch_recent_conversations(DB_PATH, user_id, limit)
    return format_conversation_to_history(chat_history)

def test_save_and_fetch():
    """
    Tests the save_data and fetch_recent_conversations functions.
    """
    # Database path
    db_path = DB_PATH 

    

    # Test data
    user_data = {
        "user_id": "12345",
        "user_message": "Hello, how are you?",
        "timestamp": int(datetime.now().timestamp() * 1000),  # Current time in milliseconds
    }
    agent_data = {
        "user_id": "12345",
        "agent_message": "I'm good, thank you!",
        "timestamp": user_data["timestamp"],
    }

    # Save data to database
    print("Saving data...")
    save_data(user_data, agent_data, db_path)

    # Fetch recent conversations
    print("Fetching data...")
    chat_history = fetch_recent_conversations(db_path, user_id="12345", limit=5)
    print("Raw chat history:", chat_history)

    # Convert to history format
    initial_history = format_conversation_to_history(chat_history)
    print("Formatted chat history:")
    for message in initial_history:
        print(f"{message.__class__.__name__}: {message.content}")


if __name__ == "__main__":
    test_save_and_fetch()