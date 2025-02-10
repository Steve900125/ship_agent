from langchain_core.tools import tool
from typing import Dict

# Hash Table
component_catalog = {
    "Carriage Bolt": {
        "Size": "40 mm",
        "Manufacturer": "BoltTech",
        "Stock": 200
    },
    "Hex Bolt": {
        "Size": "38 mm",
        "Manufacturer": "FastenCo",
        "Stock": 175
    },
    "Hex Nut": {
        "Size": "32 mm",
        "Manufacturer": "Gamma Supplies",
        "Stock": 149
    },
    "R Clip": {
        "Size": "28 mm",
        "Manufacturer": "SecureFast",
        "Stock": 300
    },
    "Split Lock Washer": {
        "Size": "34 mm",
        "Manufacturer": "Gamma Supplies",
        "Stock": 317
    },
    "Washer": {
        "Size": "36 mm",
        "Manufacturer": "FastenCo",
        "Stock": 250
    }
}

@tool
def get_component_log(component_name: str) -> Dict[str, str]:
    """
    查詢零件型錄資訊，以英文作為輸入。
    
    Args:
        component_name: 零件名稱，例如 "Hex Bolt"。
    
    Returns:
        dict: 包含該零件的尺寸、製造商與庫存數量。
    """
    component_name =component_name.strip()
    if component_name in component_catalog:
        return component_catalog[component_name]
    else:
        return {"Error": "查無此零件，請輸入正確的零件名稱。"}

if __name__=="__main__":
    print(get_component_log("Hex Bolt"))
    print(get_component_log("Hex Nut"))
    print(get_component_log("Washer"))
    print(get_component_log("R Clip"))
    print(get_component_log("Split Lock Washer"))
    print(get_component_log("Carriage Bolt"))
    print(get_component_log("Hex Nut"))