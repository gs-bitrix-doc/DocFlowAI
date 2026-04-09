from pathlib import Path


class MarkdownWriter:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)

    def save(self, content: str, stem: str, test_mode: bool = False) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if test_mode:
            filename = self._next_test_filename(stem)
        else:
            filename = f"{stem}.md"
        output_file = self.output_dir / filename
        output_file.write_text(content, encoding="utf-8")
        return output_file

    def _next_test_filename(self, stem: str) -> str:
        existing = list(self.output_dir.glob(f"test_*_{stem}.md"))
        nums = []
        for f in existing:
            try:
                nums.append(int(f.name.split("_")[1]))
            except (IndexError, ValueError):
                pass
        n = max(nums) + 1 if nums else 1
        return f"test_{n}_{stem}.md"
