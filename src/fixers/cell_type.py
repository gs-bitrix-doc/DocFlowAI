import re


# Ячейка с именем поля и следующей за ней строкой типа:
# || **fieldName**          (возможно с ^*^ или пояснением)
# [`type`](url) | description ||
_FIELD_BLOCK_RE = re.compile(
    r'(\|\|[ \t]+\*\*[^\*\n]+\*\*[^\n]*\n)([^\n]+)',
    re.MULTILINE,
)

# Строка типа в YFM-ячейке: начинается с [`type`](url)
_TYPE_LINE_RE = re.compile(r'^\[`[^`\n]+`\]\([^)\n]+\)')

# Лишний || в конце строки, добавленный LLM
_TRAILING_PIPES_RE = re.compile(r'\s*\|\|$')


def fix_cell_types(original: str, translated: str) -> tuple[str, int]:
    """Восстанавливает сломанные строки типа в YFM-ячейках по оригиналу.

    Алгоритм:
    1. Из оригинала строим карту: имя_поля → список правильных строк типа (по порядку)
    2. В переводе находим те же поля по якорю || **fieldName**, отслеживая номер вхождения
    3. Если строка типа сломана — восстанавливаем из оригинала
    4. Если оригинал не закрывал ячейку, а перевод добавил || — удаляем
    5. Если оригинал закрывал ячейку, а перевод не закрыл — добавляем

    Возвращает исправленный текст и количество исправлений.
    """
    orig_map: dict[str, list[str]] = {}
    for m in _FIELD_BLOCK_RE.finditer(original):
        field_line = m.group(1).strip()
        type_line = m.group(2)
        if _TYPE_LINE_RE.match(type_line):
            orig_map.setdefault(field_line, []).append(type_line)

    if not orig_map:
        return translated, 0

    fixes = 0
    occurrence_count: dict[str, int] = {}

    def _fix(m: re.Match) -> str:
        nonlocal fixes
        field_line = m.group(1).strip()
        type_line = m.group(2)
        originals = orig_map.get(field_line)
        if not originals:
            return m.group(0)

        # Позиционное сопоставление: N-е вхождение в переводе → N-е в оригинале
        idx = occurrence_count.get(field_line, 0)
        occurrence_count[field_line] = idx + 1
        correct = originals[min(idx, len(originals) - 1)]

        if not _TYPE_LINE_RE.match(type_line):
            # Сломана ссылка типа — восстанавливаем из оригинала
            fixes += 1
            return m.group(1) + correct
        orig_multiline = not correct.rstrip().endswith('||')
        trans_closed = type_line.rstrip().endswith('||')
        if orig_multiline and trans_closed:
            # LLM закрыл многострочную ячейку лишним || — убираем
            fixes += 1
            return m.group(1) + _TRAILING_PIPES_RE.sub('', type_line)
        if not orig_multiline and not trans_closed:
            # LLM удалил закрывающий || однострочной ячейки — возвращаем
            fixes += 1
            return m.group(1) + type_line.rstrip() + ' ||'
        return m.group(0)

    result = _FIELD_BLOCK_RE.sub(_fix, translated)
    return result, fixes