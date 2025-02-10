import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util

# python -m evaluation.generate_response
FILE = Path(__file__).resolve()
PROJECT_ROOT = FILE.parents[1]
EVAL_ROOT = PROJECT_ROOT / "evaluation" 
DATASET_ROOT = EVAL_ROOT / "dataset"
SHIP_SAFETY_ROOT = DATASET_ROOT  / "ship_safety"
SHIP_LAW_ROOT = DATASET_ROOT / "ship_law"
SHIP_ACCIDENT_REPORT1 = DATASET_ROOT / "ship_accident_report1"
SHIP_ACCIDENT_REPORT2 = DATASET_ROOT / "ship_accident_report2"

def compute_similarity(dataset_path: Path, response_path: Path, output_path: Path):
    """
    讀取 dataset.json 取得正確答案 (answer)，
    從 responses.json 取得 LLM 回應 (agent_answer)，
    計算 answer 與 agent_answer 的語義相似度 (con_sim)，
    並存入新的 JSON 檔案。

    :param dataset_path: 包含正確答案的 JSON 檔案
    :param response_path: 包含 LLM 回應的 JSON 檔案
    :param output_path: 存放結果 JSON 檔案
    """
    try:
        # 檢查檔案是否存在
        if not dataset_path.exists():
            print(f"Error: {dataset_path} does not exist.")
            return
        if not response_path.exists():
            print(f"Error: {response_path} does not exist.")
            return

        # 讀取 dataset.json（正確答案）
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
        answer_dict = {item["question"]: item["answer"] for item in dataset}

        # 讀取 responses.json（LLM 回應）
        with open(response_path, "r", encoding="utf-8") as f:
            responses = json.load(f)

        # 加載預訓練模型 (IBM Granite)
        model_path = "ibm-granite/granite-embedding-278m-multilingual"
        model = SentenceTransformer(model_path)

        # 計算相似度
        for item in responses:
            question = item.get("question", "").strip()
            agent_answer = item.get("agent_answer", "").strip()
            correct_answer = answer_dict.get(question, "").strip()

            if agent_answer and correct_answer:
                # 轉換為向量
                embeddings = model.encode([agent_answer, correct_answer])
                similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
            else:
                similarity = 0.0  # 若任一為空，設相似度為 0

            # 新增 con_sim 欄位
            item["answer"] = correct_answer  # 添加正確答案
            item["con_sim"] = round(similarity, 4)  # 保留 4 位小數

        # 存入新 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=4)

        print(f"Responses with similarity saved to {output_path}")

    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage:
if __name__ == "__main__":
    dataset_path = SHIP_ACCIDENT_REPORT2  / "dataset.json"
    response_path = SHIP_ACCIDENT_REPORT2  / "responses.json"
    output_path = SHIP_ACCIDENT_REPORT2  / "responses_with_sim.json"

    compute_similarity(dataset_path, response_path, output_path)