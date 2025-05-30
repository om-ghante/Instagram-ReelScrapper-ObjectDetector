from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("yolov8n.pt")

# Define product categories we care about
PRODUCT_CATEGORIES = ["tie", "handbag", "suitcase", "bottle", 
                     "chair", "couch", "tv", "laptop"]

def detect_objects(image_path: str) -> list:
    results = model(image_path)
    detections = []
    
    for result in results:
        for box in result.boxes:
            label = model.names[int(box.cls)]
            if label in PRODUCT_CATEGORIES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_img = result.orig_img[y1:y2, x1:x2]
                
                detections.append({
                    "label": label,
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf),
                    "cropped_image": cropped_img
                })
    
    return detections