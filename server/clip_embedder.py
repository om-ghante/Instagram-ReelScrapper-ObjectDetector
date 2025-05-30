import clip
import torch
import numpy as np
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def generate_embedding(image: np.ndarray) -> np.ndarray:
    pil_image = Image.fromarray(image)
    preprocessed = preprocess(pil_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.encode_image(preprocessed)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    
    return image_features.cpu().numpy().astype("float32")