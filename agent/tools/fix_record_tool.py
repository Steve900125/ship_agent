import os
import datetime
import json
from langchain_core.tools import tool
from typing import Dict

# 設定維修日誌存放的資料夾
LOGS_DIR = "maintenance_logs"
os.makedirs(LOGS_DIR, exist_ok=True)

@tool
def fill_maintenance_log(name: str, employee_id: str, description: str) -> Dict[str, str]:
    """
    填寫維修紀錄表單，並將記錄存入 maintenance_logs 資料夾，以時間命名檔案。

    Args:
        name: 維修人員姓名
        employee_id: 員工編號
        description: 維修描述
    
    Returns:
        dict: 紀錄填寫結果，包括存檔路徑與內容
    """
    # 取得當前時間
    current_time = datetime.datetime.now()
    formatted_date = current_time.strftime("%Y-%m-%d %H:%M:%S")
    filename = current_time.strftime("%Y%m%d_%H%M%S") + ".json"
    file_path = os.path.join(LOGS_DIR, filename)

    # 建立維修紀錄內容
    maintenance_record = {
        "Name": name,
        "Employee ID": employee_id,
        "Date": formatted_date,
        "Description": description
    }

    # 儲存 JSON 檔案
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(maintenance_record, file, ensure_ascii=False, indent=4)

    return {
        "Message": "維修紀錄已成功填寫並儲存。",
        "File Path": file_path,
        "Record": maintenance_record
    }

if __name__ == "__main__":
    # 測試填寫維修紀錄（修正後）
    print(fill_maintenance_log.invoke({
        "name": "張偉",
        "employee_id": "E12345",
        "description": "更換機械臂液壓缸"
    }))