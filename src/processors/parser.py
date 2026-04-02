from pathlib import Path


class MarkdownParser:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name
        self.stem = self.file_path.stem

    def validate(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        if self.file_path.suffix != ".md":
            raise ValueError(f"Ожидается .md файл, получен: {self.file_path.suffix}")

    def read(self) -> str:
        self.validate()
        return self.file_path.read_text(encoding="utf-8")
