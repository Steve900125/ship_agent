from ultralytics import YOLO
from typing import List
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

def default_detect()->List:
    model = YOLO(MODEL_PATH)
    image_files = glob(str(IMAGES_PATH) + '/*.[JjPp][PpNn][Gg]')

    if not image_files:
        print("No image files found.")
        return None
    
    #clean_folder()
    print(image_files)
    results = model.predict(image_files, save=True, save_txt=True, save_crop=True, exist_ok=True)
    print(results)
    # return results

if __name__ == "__main__":
    default_detect()