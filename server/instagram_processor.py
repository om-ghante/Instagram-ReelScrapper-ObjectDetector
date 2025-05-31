import yt_dlp
import cv2
import tempfile
import os
import numpy as np

async def download_media(url: str) -> list:
    """Download Instagram reel using yt-dlp and extract frames"""
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(id)s.%(ext)s'),
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            # Extract frames
            media_paths = []
            vidcap = cv2.VideoCapture(video_path)
            success, image = vidcap.read()
            frame_count = 0
            
            # We'll take 3 key frames
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_indices = [int(total_frames * i/4) for i in range(1, 4)]  # Get 3 frames evenly spaced
            
            for i in frame_indices:
                vidcap.set(cv2.CAP_PROP_POS_FRAMES, i)
                success, image = vidcap.read()
                if success:
                    frame_path = os.path.join(tempfile.gettempdir(), f"{info['id']}_frame_{i}.jpg")
                    cv2.imwrite(frame_path, image)
                    media_paths.append(frame_path)
            
            vidcap.release()
            return media_paths
            
    except Exception as e:
        print(f"Error downloading media: {str(e)}")
        raise