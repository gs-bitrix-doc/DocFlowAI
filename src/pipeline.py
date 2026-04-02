import logging

from config import API_KEY, BASE_URL, MODEL, OUTPUT_DIR
from src.processors.parser import MarkdownParser
from src.processors.pre_translator import PreTranslator
from src.processors.protector import MarkdownProtector
from src.processors.translator import Translator
from src.processors.writer import MarkdownWriter
from src.validators.structure import StructureValidator


def run(file_path: str, dry_run: bool, dictionary: dict, prompt: str, logger: logging.Logger) -> None:
    parser = MarkdownParser(file_path)
    content = parser.read()
    logger.info(f"  Размер: {len(content)} символов")

    content = PreTranslator().translate(content)

    protector = MarkdownProtector()
    protected = protector.protect(content)
    logger.info(f"  Плейсхолдеров: {protector.block_count}")

    if dry_run:
        translated = protected
    else:
        translator = Translator(api_key=API_KEY, base_url=BASE_URL, model=MODEL, prompt=prompt)
        translated = translator.translate(protected)
        logger.info("  Перевод получен")

    restored = protector.restore(translated)

    result = StructureValidator().validate(content, restored, dictionary)
    for error in result.errors:
        logger.error(f"  Ошибка структуры: {error}")
    for warning in result.warnings:
        logger.warning(f"  Предупреждение: {warning}")
    if result.is_valid:
        logger.info("  Валидация пройдена")

    saved_path = MarkdownWriter(OUTPUT_DIR).save(restored, parser.stem)
    logger.info(f"  Сохранено: {saved_path}")
