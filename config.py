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


# Словарь терминов (идёт в промпт + в валидатор)
def load_dictionary(path: str | Path = "data/dictionary.json") -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Расширенный глоссарий (только в валидатор, не в промпт)
def load_glossary(path: str | Path = "data/glossary.json") -> dict[str, str]:
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Базовый промпт без словаря
def load_prompt(prompt_path: str | Path = "data/prompt.txt") -> str:
    return Path(prompt_path).read_text(encoding="utf-8").strip()

# Промпт с отфильтрованным словарём — только термины, встречающиеся в документе
def build_prompt(base_prompt: str, dictionary: dict[str, str], content: str) -> str:
    import re
    filtered = {
        ru: en for ru, en in dictionary.items()
        if re.search(r'\b' + re.escape(ru) + r'\b', content, re.IGNORECASE)
    }
    if not filtered:
        return base_prompt
    terms = "\n".join(f"- {ru} → {en}" for ru, en in filtered.items())
    return f"{base_prompt}\n\nGlossary:\n{terms}"