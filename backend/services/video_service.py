"""Video stream service — reads frames from class.mp4 and provides streaming."""
import cv2
import asyncio
import time
from pathlib import Path
from typing import Optional, AsyncGenerator
import config


class VideoService:
    """Manages video source lifecycle and frame extraction."""

    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.video_path: str = config.VIDEO_SOURCE
        self.is_streaming: bool = False
        self.fps: float = 25.0
        self.width: int = 0
        self.height: int = 0
        self.total_frames: int = 0
        self._current_frame: int = 0

    def open(self, path: Optional[str] = None) -> bool:
        """Open a video source."""
        if path:
            self.video_path = path

        if not Path(self.video_path).exists():
            print(f"[ERROR] Video not found: {self.video_path}")
            return False

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"[ERROR] Cannot open video: {self.video_path}")
            return False

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._current_frame = 0
        print(f"[INFO] Video opened: {self.width}x{self.height} @ {self.fps:.1f}fps, {self.total_frames} frames")
        return True

    def read_frame(self):
        """Read the next frame. Loops back to start when video ends."""
        if self.cap is None or not self.cap.isOpened():
            if not self.open():
                return None

        ret, frame = self.cap.read()
        if not ret:
            # Loop video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            self._current_frame = 0
            if not ret:
                return None

        self._current_frame += 1
        return frame

    def get_jpeg_frame(self) -> Optional[bytes]:
        """Get current frame as JPEG bytes."""
        frame = self.read_frame()
        if frame is None:
            return None
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        return jpeg.tobytes()

    async def generate_mjpeg_stream(self) -> AsyncGenerator[bytes, None]:
        """Generate MJPEG stream for HTTP streaming."""
        self.is_streaming = True
        interval = 1.0 / min(self.fps, 15)  # Cap at 15fps for streaming

        while self.is_streaming:
            jpeg_bytes = self.get_jpeg_frame()
            if jpeg_bytes is None:
                await asyncio.sleep(0.1)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                jpeg_bytes +
                b"\r\n"
            )
            await asyncio.sleep(interval)

    def stop(self):
        """Stop streaming and release resources."""
        self.is_streaming = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_info(self) -> dict:
        """Get video source info."""
        return {
            "path": self.video_path,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "total_frames": self.total_frames,
            "current_frame": self._current_frame,
            "is_streaming": self.is_streaming,
        }


# Global singleton
video_service = VideoService()
