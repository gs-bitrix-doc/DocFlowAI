import logging
import re

from config import API_KEY, BASE_URL, MODEL, OUTPUT_DIR, build_prompt
from src.processors.code_translator import CodeTranslator
from src.processors.parser import MarkdownParser
from src.processors.pre_translator import PreTranslator
from src.processors.protector import MarkdownProtector
from src.processors.translator import Translator
from src.processors.writer import MarkdownWriter
from src.validators.structure import StructureValidator
from src.fixers.cell_type import fix_cell_types
from src.fixers.translation import TranslationFixer

# Максимальный размер одного запроса к LLM (символов защищённого текста)
_CHUNK_SIZE = 4000


def _split_for_translation(content: str) -> list[str]:
    """Делит защищённый текст на чанки по границам H2-разделов.

    Если документ помещается в один чанк — возвращает список из одного элемента.
    Если раздел сам по себе больше CHUNK_SIZE — бьёт его по двойным переносам строк.
    """
    if len(content) <= _CHUNK_SIZE:
        return [content]

    # Режем по H2 заголовкам (## ...) — безопасные границы разделов
    sections = re.split(r'(?=^## )', content, flags=re.MULTILINE)

    chunks: list[str] = []
    current = ""

    for section in sections:
        if len(section) > _CHUNK_SIZE:
            # Раздел сам слишком большой — бьём по абзацам
            if current:
                chunks.append(current)
                current = ""
            paragraphs = section.split('\n\n')
            para_chunk = ""
            for para in paragraphs:
                candidate = para_chunk + ('\n\n' if para_chunk else '') + para
                if para_chunk and len(candidate) > _CHUNK_SIZE:
                    chunks.append(para_chunk)
                    para_chunk = para
                else:
                    para_chunk = candidate
            if para_chunk:
                chunks.append(para_chunk)
        elif current and len(current) + len(section) > _CHUNK_SIZE:
            chunks.append(current)
            current = section
        else:
            current += section

    if current:
        chunks.append(current)

    return chunks


def run(file_path: str, dry_run: bool, dictionary: dict, base_prompt: str, logger: logging.Logger, glossary: dict | None = None, test_mode: bool = False) -> None:
    parser = MarkdownParser(file_path)
    content = parser.read()
    logger.info(f"  Размер: {len(content)} символов")

    content = PreTranslator().translate(content)

    prompt = build_prompt(base_prompt, dictionary, content)

    if not dry_run:
        translator = Translator(api_key=API_KEY, base_url=BASE_URL, model=MODEL, prompt=prompt, logger=logger)
        content = CodeTranslator(translator).translate(content)

    protector = MarkdownProtector()
    protected = protector.protect(content)
    logger.info(f"  Плейсхолдеров: {protector.block_count}")

    if dry_run:
        translated = protected
    else:
        chunks = _split_for_translation(protected)
        if len(chunks) > 1:
            logger.info(f"  Документ разбит на {len(chunks)} части")
        translated_parts = [translator.translate(chunk) for chunk in chunks]
        translated = ''.join(p.rstrip('\n') + '\n\n' for p in translated_parts).rstrip('\n') + '\n'
        logger.info("  Перевод получен")

    restored = protector.restore(translated)

    restored, fix_count = fix_cell_types(content, restored)
    if fix_count:
        logger.info(f"  Исправлено ячеек типа: {fix_count}")

    if not dry_run:
        restored, cyrillic_count = TranslationFixer().fix(restored, translator)
        if cyrillic_count:
            logger.info(f"  Доперевод: {cyrillic_count} строк")

    combined = {**glossary, **dictionary} if glossary else dictionary
    result = StructureValidator().validate(content, restored, combined)
    for error in result.errors:
        logger.error(f"  Ошибка структуры: {error}")
    for warning in result.warnings:
        logger.warning(f"  Предупреждение: {warning}")
    if result.is_valid:
        logger.info("  Валидация пройдена")

    saved_path = MarkdownWriter(OUTPUT_DIR).save(restored, parser.stem, test_mode=test_mode)
    logger.info(f"  Сохранено: {saved_path}")