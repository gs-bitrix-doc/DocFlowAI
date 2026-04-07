from pathlib import Path

import click

from config import load_prompt, load_dictionary, load_glossary, setup_logging
from src import pipeline


@click.command()
@click.argument("file_path", required=False)
@click.option("--dir", "dir_path", default=None, help="Перевести все .md файлы в папке")
@click.option("--dry-run", is_flag=True, help="Запуск без перевода — проверка пайплайна")
@click.option("--test", "test_mode", is_flag=True, help="Сохранить как test_N_<file>.en.md")
def main(file_path: str, dir_path: str, dry_run: bool, test_mode: bool):
    """Переводит .md файл(ы) с русского на английский."""
    logger = setup_logging()

    if not file_path and not dir_path:
        click.echo("Укажите файл или папку. Используй --help для справки.")
        return

    try:
        dictionary = load_dictionary()
        glossary = load_glossary()
        base_prompt = load_prompt()

        if dir_path:
            files = list(Path(dir_path).glob("*.md"))
            if not files:
                logger.warning(f"В папке {dir_path} не найдено .md файлов")
                return
            logger.info(f"Найдено файлов: {len(files)}")
            for f in files:
                logger.info(f"Переводим: {f.name}")
                pipeline.run(str(f), dry_run, dictionary, base_prompt, logger, glossary, test_mode)
        else:
            logger.info(f"Переводим: {file_path}")
            pipeline.run(file_path, dry_run, dictionary, base_prompt, logger, glossary, test_mode)

    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {e}")
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
