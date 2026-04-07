"""
Запускает шаги 1-4 пайплайна и показывает текст в том виде,
в котором он поступает в Translator (шаг 5).

Использование:
    python tools/inspect_pipeline.py <path_to_file.md>
    python tools/inspect_pipeline.py <path_to_file.md> --no-code-translate
    python tools/inspect_pipeline.py <path_to_file.md> --output tools/debug/my_output.txt

По умолчанию сохраняет в tools/debug/<имя_файла>.txt
"""
import argparse
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.parser import MarkdownParser
from src.processors.pre_translator import PreTranslator
from src.processors.protector import MarkdownProtector


def inspect(file_path: str, skip_code_translate: bool = False) -> str:
    out = StringIO()

    def p(*args, **kwargs):
        print(*args, **kwargs, file=out)

    # Шаг 1: Parser
    parser = MarkdownParser(file_path)
    content = parser.read()
    p(f"=== ИСХОДНИК ({len(content)} символов) ===\n")
    p(content)

    # Шаг 2: PreTranslator
    content = PreTranslator().translate(content)
    p(f"\n\n{'='*60}")
    p(f"=== ПОСЛЕ PreTranslator ({len(content)} символов) ===\n")
    p(content)

    # Шаг 3: CodeTranslator (опционально — требует API)
    if not skip_code_translate:
        try:
            from config import API_KEY, BASE_URL, MODEL
            from src.processors.translator import Translator
            from src.processors.code_translator import CodeTranslator
            translator = Translator(api_key=API_KEY, base_url=BASE_URL, model=MODEL, prompt="")
            content = CodeTranslator(translator).translate(content)
            p(f"\n\n{'='*60}")
            p(f"=== ПОСЛЕ CodeTranslator ({len(content)} символов) ===\n")
            p(content)
        except Exception as e:
            p(f"\n\n[CodeTranslator пропущен: {e}]")
    else:
        p(f"\n\n[CodeTranslator пропущен (--no-code-translate)]")

    # Шаг 4: Protector
    protector = MarkdownProtector()
    protected = protector.protect(content)
    p(f"\n\n{'='*60}")
    p(f"=== ПОСЛЕ Protector — ВХОД В TRANSLATOR ({len(protected)} символов, {protector.block_count} плейсхолдеров) ===\n")
    p(protected)

    p(f"\n\n{'='*60}")
    p(f"=== ПЛЕЙСХОЛДЕРЫ ===\n")
    for placeholder, original in protector._blocks.items():
        p(f"  {placeholder}  =>  {repr(original)}")

    return out.getvalue()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Inspect pipeline steps 1-4")
    arg_parser.add_argument("file_path", help="Путь к .md файлу")
    arg_parser.add_argument("--no-code-translate", action="store_true", help="Пропустить CodeTranslator (без API-вызова)")
    arg_parser.add_argument("--output", default=None, help="Сохранить результат в файл (UTF-8)")
    args = arg_parser.parse_args()

    result = inspect(args.file_path, skip_code_translate=args.no_code_translate)

    if args.output:
        output_path = Path(args.output)
    else:
        debug_dir = Path(__file__).parent / "debug"
        debug_dir.mkdir(exist_ok=True)
        output_path = debug_dir / (Path(args.file_path).stem + ".txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"Сохранено: {output_path}")