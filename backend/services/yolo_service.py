"""YOLO inference service — loads model and processes video frames for behavior detection."""
import cv2
import numpy as np
import time
import asyncio
from pathlib import Path
from typing import Optional
import config

# Try to import ultralytics; graceful fallback
try:
    from ultralytics import YOLO
    HAS_ULTRALYTICS = True
except ImportError:
    HAS_ULTRALYTICS = False
    print("[WARN] ultralytics not installed. Using simulated inference.")


class YOLOService:
    """Manages YOLO model lifecycle and frame inference."""

    def __init__(self):
        self.model = None
        self.model_name: str = config.DEFAULT_MODEL
        self.confidence: float = config.CONFIDENCE_THRESHOLD
        self.iou: float = config.IOU_THRESHOLD
        self.is_running: bool = False
        self._frame_id: int = 0
        self._track_counter: int = 0

    def load_model(self, model_name: Optional[str] = None):
        """Load a YOLO model from the available model files."""
        if model_name:
            self.model_name = model_name

        model_path = config.MODEL_FILES.get(self.model_name, list(config.MODEL_FILES.values())[0])

        if not Path(model_path).exists():
            print(f"[ERROR] Model file not found: {model_path}")
            return False

        if HAS_ULTRALYTICS:
            try:
                self.model = YOLO(model_path)
                print(f"[INFO] Loaded model: {model_path}")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to load model: {e}")
                return False
        else:
            print(f"[INFO] Simulated model load: {model_path}")
            self.model = "simulated"
            return True

    def update_params(self, confidence: Optional[float] = None, iou: Optional[float] = None):
        """Update detection parameters."""
        if confidence is not None:
            self.confidence = max(0.1, min(1.0, confidence))
        if iou is not None:
            self.iou = max(0.1, min(1.0, iou))

    def infer_frame(self, frame: np.ndarray) -> dict:
        """Run inference on a single frame. Returns structured detection results."""
        self._frame_id += 1
        h, w = frame.shape[:2]
        timestamp = int(time.time() * 1000)

        objects = []

        if self.model and HAS_ULTRALYTICS and self.model != "simulated":
            try:
                results = self.model(
                    frame,
                    conf=self.confidence,
                    iou=self.iou,
                    verbose=False,
                )
                if results and len(results) > 0:
                    result = results[0]
                    boxes = result.boxes
                    if boxes is not None and len(boxes) > 0:
                        for i, box in enumerate(boxes):
                            # Get box coordinates (xyxy format)
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            cls_id = int(box.cls[0].cpu().numpy())
                            conf = float(box.conf[0].cpu().numpy())

                            # Convert to relative center coords
                            cx = ((x1 + x2) / 2) / w
                            cy = ((y1 + y2) / 2) / h
                            bw = (x2 - x1) / w
                            bh = (y2 - y1) / h

                            action = config.BEHAVIOR_CLASSES.get(cls_id, "Listening")
                            track_id = f"T{i+1:02d}"

                            objects.append({
                                "track_id": track_id,
                                "student_id": None,
                                "bbox": [round(cx, 4), round(cy, 4), round(bw, 4), round(bh, 4)],
                                "action": action,
                                "confidence": round(conf, 3),
                            })
            except Exception as e:
                print(f"[ERROR] Inference failed: {e}")
                objects = self._simulate_detections()
        else:
            objects = self._simulate_detections()

        # Calculate metrics
        total = len(objects)
        focus = sum(1 for o in objects if o["action"] in config.FOCUS_BEHAVIORS)
        distracted = sum(1 for o in objects if o["action"] in config.DISTRACTED_BEHAVIORS)
        violation = sum(1 for o in objects if o["action"] in config.VIOLATION_BEHAVIORS)

        # Attention score calculation (from doc formula)
        if total > 0:
            score = (config.W_LISTENING * focus) / total * 100
            score -= violation * config.PHONE_PENALTY
            score = max(0, min(100, round(score, 1)))
        else:
            score = 0

        return {
            "timestamp": timestamp,
            "frame_id": self._frame_id,
            "metrics": {
                "total": total,
                "focus": focus,
                "distracted": distracted,
                "violation": violation,
                "score": score,
            },
            "objects": objects,
        }

    def _simulate_detections(self) -> list:
        """Generate simulated detection results for demo purposes."""
        import random
        n_people = random.randint(8, 18)
        objects = []
        actions_pool = (
            ["Listening"] * 50 +
            ["Reading_Writing"] * 20 +
            ["Sleeping"] * 10 +
            ["Looking_Around"] * 10 +
            ["Using_Phone"] * 7 +
            ["Standing_Leaving"] * 3
        )
        for i in range(n_people):
            action = random.choice(actions_pool)
            cx = random.uniform(0.1, 0.9)
            cy = random.uniform(0.15, 0.85)
            bw = random.uniform(0.04, 0.12)
            bh = random.uniform(0.08, 0.2)
            objects.append({
                "track_id": f"T{i+1:02d}",
                "student_id": None,
                "bbox": [round(cx, 4), round(cy, 4), round(bw, 4), round(bh, 4)],
                "action": action,
                "confidence": round(random.uniform(0.6, 0.98), 3),
            })
        return objects


# Global singleton
yolo_service = YOLOService()
