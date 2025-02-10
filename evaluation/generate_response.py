from pathlib import Path
import shutil
import json
import os
import sys
# python -m evaluation.generate_response
FILE = Path(__file__).resolve()
PROJECT_ROOT = FILE.parents[1]
EVAL_ROOT = PROJECT_ROOT / "evaluation" 
DATASET_ROOT = EVAL_ROOT / "dataset"

SHIP_SAFETY_ROOT = DATASET_ROOT  / "ship_safety"
SHIP_LAW_ROOT = DATASET_ROOT / "ship_law"
SHIP_ACCIDENT_REPORT1 = DATASET_ROOT / "ship_accident_report1"
SHIP_ACCIDENT_REPORT2 = DATASET_ROOT / "ship_accident_report2"

sys.path.insert(0, str(PROJECT_ROOT))  # for import modules
from agent.agent_main import get_agent_answer


def clean_folder(folder_path: Path):
    '''
        'clean_folder' is using in server to clean temporary files
    '''
    if folder_path.exists():
        shutil.rmtree(folder_path)
        print(f"{folder_path} has been deleted.")
        os.makedirs(folder_path)

def generate_responses(data_path: Path, output_path: Path):
    """
    讀取 dataset.json，對每個問題生成回應，並存入 output JSON。

    :param data_path: 問題 JSON 檔案路徑
    :param output_path: 產生的問答 JSON 檔案路徑
    """
    try:
        # 確保來源檔案存在
        if not data_path.exists():
            print(f"Error: {data_path} does not exist.")
            return
        
        # 讀取 JSON
        with open(data_path, "r", encoding="utf-8") as f:
            question_groups = json.load(f)

        responses = []
        for question_group in question_groups:
            question = question_group.get("question", "").strip()
            if question:  # 確保 question 不為空
                agent_response = get_agent_answer(question)
                responses.append({
                    "question": question,
                    "agent_answer": agent_response
                })

        # 存入 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=4)

        print(f"Responses saved to {output_path}")

    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {data_path}.")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Example usage:
if __name__ == "__main__":
    dataset_path = SHIP_ACCIDENT_REPORT2 / "dataset.json"
    response_path = SHIP_ACCIDENT_REPORT2 / "responses.json"
    generate_responses(dataset_path, response_path)
