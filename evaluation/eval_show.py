import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# python -m evaluation.generate_response
FILE = Path(__file__).resolve()
PROJECT_ROOT = FILE.parents[1]
EVAL_ROOT = PROJECT_ROOT / "evaluation" 
DATASET_ROOT = EVAL_ROOT / "dataset"

SHIP_SAFETY_ROOT = DATASET_ROOT  / "ship_safety"
SHIP_LAW_ROOT = DATASET_ROOT / "ship_law"
SHIP_ACCIDENT_REPORT1 = DATASET_ROOT / "ship_accident_report1"
SHIP_ACCIDENT_REPORT2 = DATASET_ROOT / "ship_accident_report2"

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List

def analyze_similarity_scores(response_paths: List[Path]):
    """
    讀取多個 responses_with_sim.json，使用 pandas 顯示 con_sim 的統計分析。

    :param response_paths: responses_with_sim.json 的路徑列表 (可傳入多個 JSON 檔案)
    """
    try:
        all_data = []

        # 遍歷所有檔案
        for response_path in response_paths:
            if not response_path.exists():
                print(f"⚠️ Warning: {response_path} does not exist, skipping...")
                continue  # 跳過不存在的檔案

            # 讀取 JSON
            with open(response_path, "r", encoding="utf-8") as f:
                responses = json.load(f)

            # 轉換成 DataFrame
            df = pd.DataFrame(responses)

            # 確保 con_sim 存在且為數值
            if "con_sim" not in df.columns:
                print(f"⚠️ Warning: {response_path} 缺少 'con_sim' 欄位，跳過分析。")
                continue

            df["con_sim"] = pd.to_numeric(df["con_sim"], errors="coerce")
            df["source_file"] = response_path.name  # 加入來源檔案名稱
            
            all_data.append(df)

        if not all_data:
            print("❌ No valid data found for analysis.")
            return

        # 合併所有 DataFrame
        combined_df = pd.concat(all_data, ignore_index=True)

        # 顯示整體統計數據
        print("\n🔹 整體相似度統計數據 (合併所有檔案)：")
        print(combined_df["con_sim"].describe())

        # 分佈視覺化
        plt.figure(figsize=(8, 5))
        sns.histplot(combined_df["con_sim"], bins=20, kde=True, color="skyblue")
        plt.xlabel("相似度 (con_sim)")
        plt.ylabel("頻率")
        plt.title("LLM 回應與標準答案的相似度分佈 (所有檔案)")
        plt.grid()
        plt.show()

        # 分別顯示每個檔案的統計數據
        print("\n🔹 每個檔案的相似度統計數據：")
        grouped_stats = combined_df.groupby("source_file")["con_sim"].describe()
        print(grouped_stats)

    except json.JSONDecodeError:
        print("Error: 無法解析 JSON，請檢查文件格式。")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage:
if __name__ == "__main__":
    response_paths = [
        # SHIP_LAW_ROOT / "responses_with_sim.json",
        # SHIP_SAFETY_ROOT / "responses_with_sim.json",
        # SHIP_ACCIDENT_REPORT1 / "responses_with_sim.json",
        SHIP_ACCIDENT_REPORT2 / "responses_with_sim.json",
    ]
    analyze_similarity_scores(response_paths)

