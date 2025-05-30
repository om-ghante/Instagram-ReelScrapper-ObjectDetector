import instaloader
import tempfile
import os
import cv2

async def download_media(url: str) -> list:
    loader = instaloader.Instaloader(
        dirname_pattern=tempfile.gettempdir(),
        save_metadata=False,
        download_videos=True
    )
    
    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    
    media_paths = []
    
    if post.is_video:
        # Download video
        loader.download_post(post, target=shortcode)
        video_path = f"{tempfile.gettempdir()}/{shortcode}/{shortcode}.mp4"
        
        # Extract frames
        vidcap = cv2.VideoCapture(video_path)
        success, image = vidcap.read()
        frame_count = 0
        while success:
            frame_path = f"{tempfile.gettempdir()}/{shortcode}_frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, image)
            media_paths.append(frame_path)
            frame_count += 1
            success, image = vidcap.read()
    else:
        # Download image
        loader.download_post(post, target=shortcode)
        media_paths.append(f"{tempfile.gettempdir()}/{shortcode}/{post.url.split('/')[-1]}")
    
    return media_paths