import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

VIDEO_ENABLED = os.getenv("VIDEO_ENABLED", "false").lower() == "true"
MAGIC_HOUR_API_KEY = os.getenv("MAGIC_HOUR_API_KEY")

OUTPUT_DIR = Path(os.getenv("VIDEO_OUTPUT_DIR", "videos"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_MODEL = "ltx-2.5"
VIDEO_RESOLUTION = "480p"
VIDEO_SECONDS = 10.0

POLL_INTERVAL = 5          # segundos entre consultas
JOB_TIMEOUT = 600          # 10 min
KEEP_DAYS = 3              # apaga vídeos mais antigos que isso
MAX_TELEGRAM_MB = 50       # limite do envio via bot
