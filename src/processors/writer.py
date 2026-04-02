from pathlib import Path


class MarkdownWriter:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)

    def save(self, content: str, stem: str) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"{stem}.en.md"
        output_file.write_text(content, encoding="utf-8")
        return output_file
