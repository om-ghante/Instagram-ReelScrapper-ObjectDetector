from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import traceback
import os
from dotenv import load_dotenv
import instagram_processor
import object_detector
import clip_embedder
import faiss_matcher

# Load environment variables
load_dotenv()

app = FastAPI()

# Enhanced CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
            "http://www.instagram.com/reel/"
        ]):
            raise HTTPException(
                status_code=400,
                detail="URL must be in format: https://www.instagram.com/reel/REEL_ID/"
            )

        # Test mode bypass
        if request.test_mode:
            logger.info("Running in test mode with mock data")
            return {
                "status": "success",
                "results": [{
                    "object": "chair",
                    "confidence": 0.92,
                    "matches": [{
                        "name": "Modern Chair",
                        "image_url": "https://example.com/chair.jpg",
                        "similarity_score": 0.95
                    }]
                }]
            }

        # Step 1: Download media with error handling
        try:
            media_paths = await instagram_processor.download_media(url)
            if not media_paths:
                raise HTTPException(
                    status_code=404,
                    detail="No media found at this URL"
                )
            logger.info(f"Downloaded {len(media_paths)} media files")
        except Exception as e:
            logger.error(f"Media download failed: {traceback.format_exc()}")
            raise HTTPException(
                status_code=503,
                detail="Failed to download media. Instagram may be blocking requests."
            )

        # Rest of your processing pipeline...
        # [Keep your existing object detection and matching code]

        return {
            "status": "success",
            "results": results
        }

    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he.detail)}")
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