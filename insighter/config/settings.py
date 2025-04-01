import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "insighter", "data")

# Database settings
DATABASE_PATH = os.path.join(DATA_DIR, "sales_marketing.db")

# Projects directory
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# Default configurations
DEFAULT_APP_SETTINGS = {
    "theme": "light",
    "debug": False,
}

# Ensure directories exist
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True) 