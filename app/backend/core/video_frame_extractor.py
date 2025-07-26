import subprocess
import os
import logging
from typing import Optional
import shutil

logger = logging.getLogger(__name__)

class VideoFrameExtractor:
    """Utility class for extracting video frames using FFmpeg."""
    
    def __init__(self, video_dir: str = "./data/content_understanding/videos", 
                 output_dir: str = "./static/video_thumbnails"):
        self.video_dir = video_dir
        self.output_dir = output_dir
        self._ensure_output_dir()
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available."""
        if not shutil.which("ffmpeg"):
            logger.warning("FFmpeg not found. Video thumbnail extraction will be disabled.")
            self.ffmpeg_available = False
        else:
            logger.info("FFmpeg found and ready for video processing.")
            self.ffmpeg_available = True
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_thumbnail(self, video_filename: str, timestamp: str = "00:00:01", 
                         output_filename: Optional[str] = None) -> Optional[str]:
        """
        Extract a thumbnail from a video at the specified timestamp.
        
        Args:
            video_filename: Name of the video file (e.g., "huawei.mp4")
            timestamp: Timestamp in format "HH:MM:SS" or "HH:MM:SS.mmm"
            output_filename: Optional custom output filename
            
        Returns:
            Relative path to the generated thumbnail or None if failed
        """
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available, cannot extract thumbnail")
            return None
            
        try:
            # Construct paths
            video_path = os.path.join(self.video_dir, video_filename)
            
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            # Generate output filename if not provided
            if not output_filename:
                base_name = os.path.splitext(video_filename)[0]
                timestamp_safe = timestamp.replace(":", "-").replace(".", "-")
                output_filename = f"{base_name}_{timestamp_safe}.jpg"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # FFmpeg command to extract frame
            cmd = [
                "ffmpeg",
                "-ss", timestamp,           # Seek to timestamp
                "-i", video_path,           # Input video
                "-frames:v", "1",           # Extract 1 frame
                "-q:v", "2",               # High quality
                "-y",                      # Overwrite output file
                output_path
            ]
            
            # Run FFmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Return relative path for web access
                relative_path = f"/video_thumbnails/{output_filename}"
                logger.info(f"Successfully extracted thumbnail: {relative_path}")
                return relative_path
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg timeout for {video_filename} at {timestamp}")
            return None
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {str(e)}")
            return None
    
    def extract_multiple_thumbnails(self, video_filename: str, timestamps: list[str]) -> dict[str, str]:
        """
        Extract multiple thumbnails from a video.
        
        Args:
            video_filename: Name of the video file
            timestamps: List of timestamps
            
        Returns:
            Dictionary mapping timestamps to thumbnail paths
        """
        thumbnails = {}
        for timestamp in timestamps:
            thumbnail_path = self.extract_thumbnail(video_filename, timestamp)
            if thumbnail_path:
                thumbnails[timestamp] = thumbnail_path
        return thumbnails
