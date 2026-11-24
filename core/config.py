"""설정. API 키는 코드에 쓰지 않고 환경변수(.env)에서만 읽는다."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = Path(os.getenv("MI_DB_PATH", BASE_DIR / "data" / "market_insight.db"))
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

CATEGORIES = [
    "기업 실적", "금리", "전쟁/국제정세", "정부 정책", "신기술/산업 변화",
    "인수합병", "금융위기", "원자재", "환율/물가",
]
