from ultralytics import YOLO
from collections import Counter
from typing import Dict, Optional
from pathlib import Path
from glob import glob
import shutil
import os

VISION_PATH = Path(__file__).resolve().parents[0]
IMAGES_PATH = VISION_PATH / "images"
MODEL_PATH = VISION_PATH / "model" /"yolov11_detect.pt"

def clean_folder(folder_path: Path):
    '''
        'clean_folder' is using in server to clean temporary files
    '''
    if folder_path.exists():
        shutil.rmtree(folder_path)
        print(f"{folder_path} has been deleted.")
        os.makedirs(folder_path)

def default_detect() -> Optional[Dict[str, int]] | None:
    model = YOLO(MODEL_PATH)
    image_files = glob(str(IMAGES_PATH) + '/*.[JjPp][PpNn][Gg]')

    if not image_files:
        print("No image files found.")
        return None
    
    print(f"Processing {len(image_files)} images:", image_files)
    results = model.predict(image_files, save=True, save_txt=True, save_crop=True, exist_ok=True)

    object_count = Counter()
    for result in results:
        if hasattr(result, "boxes") and result.boxes is not None:
            class_ids = result.boxes.cls.tolist() if result.boxes.cls is not None else []
            object_count.update(class_ids)

    # 將 class ID 轉換為物件名稱
    if hasattr(model, "names"):
        object_counts_named = {model.names[int(k)]: v for k, v in object_count.items()}
    else:
        object_counts_named = dict(object_count)  # 直接回傳 ID 和數量

    print("Named object counts:", object_counts_named)
    return object_counts_named if object_counts_named else None  # 若無檢測結果，回傳 None


if __name__ == "__main__":
    default_detect()