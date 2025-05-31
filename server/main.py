from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import traceback
import os
from dotenv import load_dotenv
import base64
import cv2

# Initialize FastAPI app first
app = FastAPI()

# Then import your modules (they can now use the 'app' instance)
import instagram_processor
import object_detector
import clip_embedder
import faiss_matcher

# Load environment variables
load_dotenv()

# Enhanced CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request Model with enhanced validation
class InstagramRequest(BaseModel):
    url: str
    test_mode: bool = False  # New field for testing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_instagram_url(url: str) -> str:
    """Convert share URLs to standard reel URLs"""
    if "/share/reel/" in url:
        reel_id = url.split("/share/reel/")[1].split("/")[0]
        return f"https://www.instagram.com/reel/{reel_id}/"
    return url

@app.post("/api/process-instagram")
async def process_instagram(request: InstagramRequest):
    try:
        # Normalize URL and validate
        url = normalize_instagram_url(request.url)
        logger.info(f"Processing URL: {url}")
        
        if not any(url.startswith(base) for base in [
            "https://www.instagram.com/reel/",
            "http://www.instagram.com/reel/",
            "https://www.instagram.com/p/",
            "http://www.instagram.com/p/",
            "https://www.instagram.com/reels/DKTyUyGKeig/"
        ]):
            raise HTTPException(
                status_code=400,
                detail="URL must be an Instagram reel or post URL"
            )

        # Test mode bypass
        if request.test_mode:
            logger.info("Running in test mode with mock data")
            return {
                "status": "success",
                "results": [{
                    "object": "chair",
                    "confidence": 0.92,
                    "cropped_image": None,  # Would be base64 in real response
                    "matches": [{
                        "name": "Modern Chair",
                        "image_url": "https://example.com/chair.jpg",
                        "similarity_score": 0.95
                    }]
                }]
            }

        # Step 1: Download media and extract frames
        try:
            media_paths = await instagram_processor.download_media(url)
            if not media_paths:
                raise HTTPException(
                    status_code=404,
                    detail="No media found at this URL"
                )
            logger.info(f"Downloaded {len(media_paths)} frames")
        except Exception as e:
            logger.error(f"Media download failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=503,
                detail="Failed to download media. Please check the URL."
            )

        # Step 2: Process each frame for object detection
        all_detections = []
        for frame_path in media_paths:
            frame_detections = object_detector.detect_objects(frame_path)
            all_detections.extend(frame_detections)
            
            # Clean up frame file
            try:
                os.remove(frame_path)
            except:
                pass

        if not all_detections:
            raise HTTPException(
                status_code=404,
                detail="No products detected in the media"
            )

        # Step 3: Find matches for each detected object
        results = []
        for detection in all_detections:
            # Generate embedding for the cropped object
            embedding = clip_embedder.generate_embedding(detection["cropped_image"])
            
            # Find matching products
            matches = faiss_matcher.find_matches(embedding)
            
            # Convert image to base64 for response
            _, buffer = cv2.imencode('.jpg', detection["cropped_image"])
            cropped_base64 = base64.b64encode(buffer).decode('utf-8')
            
            results.append({
                "object": detection["object"],
                "confidence": detection["confidence"],
                "cropped_image": cropped_base64,
                "matches": matches
            })

        return {
            "status": "success",
            "results": results
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )

@app.get("/")
async def health_check():
    return {"status": "ok", "version": "1.0.1"}