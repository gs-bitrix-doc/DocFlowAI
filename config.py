import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Пути
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
LOGS_DIR = Path("logs")

# API
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

# Логирование
def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


# Словарь терминов
def load_dictionary(path: str | Path = "data/dictionary.json") -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Промпт
def build_prompt(
    dictionary: dict[str, str],
    prompt_path: str | Path = "data/prompt.txt",
) -> str:
    base_prompt = Path(prompt_path).read_text(encoding="utf-8").strip()
    terms = "\n".join(f"- {ru} → {en}" for ru, en in dictionary.items())
    return f"{base_prompt}\n\nGlossary:\n{terms}"