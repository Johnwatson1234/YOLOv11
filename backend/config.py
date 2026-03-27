"""Global configuration for ClassVision backend."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR
VIDEO_DIR = BASE_DIR

# Model configuration
DEFAULT_MODEL = "best_1200_pre.pt"
MODEL_FILES = {
    "yolov11.pt": str(MODEL_DIR / "best_1200_pre.pt"),
    "yolov12.pt": str(MODEL_DIR / "best_1200_pre.pt"),
}
CURRENT_MODEL = DEFAULT_MODEL
CONFIDENCE_THRESHOLD = 0.45
IOU_THRESHOLD = 0.5

# Video configuration
VIDEO_SOURCE = str(VIDEO_DIR / "class.mp4")

# Behavior classes mapping (from model training)
# The model outputs numeric class IDs, mapped to readable labels
BEHAVIOR_CLASSES = {
    0: "Listening",
    1: "Reading_Writing",
    2: "Sleeping",
    3: "Looking_Around",
    4: "Using_Phone",
    5: "Standing_Leaving",
}

# Behavior categories
FOCUS_BEHAVIORS = {"Listening", "Reading_Writing"}
DISTRACTED_BEHAVIORS = {"Sleeping", "Looking_Around"}
VIOLATION_BEHAVIORS = {"Using_Phone"}
ABNORMAL_BEHAVIORS = {"Standing_Leaving"}

# Behavior display names (Chinese)
BEHAVIOR_NAMES_CN = {
    "Listening": "专注听讲",
    "Reading_Writing": "阅读/记笔记",
    "Sleeping": "低头/趴桌",
    "Looking_Around": "左顾右盼",
    "Using_Phone": "玩手机",
    "Standing_Leaving": "起立/离开",
}

# Behavior colors for frontend
BEHAVIOR_COLORS = {
    "Listening": "#00E676",
    "Reading_Writing": "#00E676",
    "Sleeping": "#FFB300",
    "Looking_Around": "#FFB300",
    "Using_Phone": "#FF2A55",
    "Standing_Leaving": "#FF2A55",
}

# Attention score weights
W_LISTENING = 1.0
W_READING_WRITING = 1.0
PHONE_PENALTY = 3.0  # Points deducted per phone user

# WebSocket
WS_PUSH_INTERVAL = 0.3  # seconds between WebSocket pushes

# Server
HOST = "0.0.0.0"
PORT = 8000
