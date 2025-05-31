from ultralytics import YOLO
import cv2
import numpy as np

# Load the larger YOLOv8x model
model = YOLO("yolov8x.pt")

# Define product categories we care about (expanded list)
PRODUCT_CATEGORIES = [
    "tie", "handbag", "suitcase", "bottle", "wine glass", "cup",
    "chair", "couch", "tv", "laptop", "mouse", "remote", "keyboard",
    "cell phone", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush", "backpack", "umbrella", "shoe",
    "sunglasses", "hat", "dining table", "bed", "mirror"
]

def detect_objects(image_path: str) -> list:
    """Detect objects in an image using YOLOv8x"""
    image = cv2.imread(image_path)
    if image is None:
        return []
    
    results = model(image)
    detections = []
    
    for result in results:
        for box in result.boxes:
            label = model.names[int(box.cls)]
            if label in PRODUCT_CATEGORIES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped_img = image[y1:y2, x1:x2]
                
                # Convert BGR to RGB for display purposes
                cropped_img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                
                detections.append({
                    "object": label,
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf),
                    "cropped_image": cropped_img_rgb,
                    "original_image_path": image_path
                })
    
    return detections