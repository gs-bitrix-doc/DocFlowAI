import re

_CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)
_CYRILLIC_RE = re.compile(r'[а-яёА-ЯЁ]')

# Однострочная ячейка: [`тип`](url) | описание ||
_SINGLE_CELL_RE = re.compile(
    r'^(\[`[^`\n]+`\]\([^)\n]+\)[ \t]*\|[ \t]*)(.+?)(\s*\|\|)$'
)

# Начало многострочной ячейки: [`тип`](url) | описание (без ||)
_MULTILINE_CELL_START_RE = re.compile(
    r'^(\[`[^`\n]+`\]\([^)\n]+\)[ \t]*\|[ \t]*)(.+)$'
)

_BATCH_PROMPT = (
    "Translate Russian text to English. "
    "Return only translations, one per line, same order. "
    "Preserve markdown, inline code, and placeholders unchanged."
)


class TranslationFixer:
    def fix(self, content: str, translator) -> tuple[str, int]:
        units = self._collect_units(content)
        if not units:
            return content, 0

        unique_sources = list(dict.fromkeys(u[1] for u in units))
        translations = self._batch_translate(unique_sources, translator)
        source_map = dict(zip(unique_sources, translations))

        line_map: dict[str, str] = {}
        for original_line, source_text, prefix, suffix in units:
            translated_full = source_map.get(source_text, source_text)
            if translated_full == source_text:
                continue
            if prefix and suffix:
                # Однострочная ячейка: извлекаем описание из ответа LLM
                m = _SINGLE_CELL_RE.match(translated_full)
                if not m:
                    continue  # LLM сломал структуру — пропускаем
                translated_line = prefix + m.group(2) + suffix
            elif prefix:
                # Многострочная ячейка: извлекаем описание без ||
                m = _MULTILINE_CELL_START_RE.match(translated_full)
                if not m:
                    continue
                translated_line = prefix + m.group(2)
            else:
                translated_line = translated_full
            if not _CYRILLIC_RE.search(translated_line):
                line_map[original_line] = translated_line

        fix_count = 0
        for original_line, translated_line in line_map.items():
            content = re.sub(
                r'^' + re.escape(original_line) + r'$',
                lambda m, _t=translated_line: _t,
                content,
                flags=re.MULTILINE,
            )
            fix_count += 1

        return content, fix_count

    def _collect_units(self, content: str) -> list[tuple[str, str, str, str]]:
        """Возвращает (original_line, text_to_translate, prefix, suffix)."""
        code_ranges = [(m.start(), m.end()) for m in _CODE_BLOCK_RE.finditer(content)]

        result = []
        pos = 0
        for line in content.split('\n'):
            end = pos + len(line)
            in_code = any(s <= pos and end <= e for s, e in code_ranges)

            if not in_code and _CYRILLIC_RE.search(line):
                m = _SINGLE_CELL_RE.match(line)
                if m:
                    # Однострочная ячейка — отправляем полную строку для контекста,
                    # из ответа извлекаем только описание
                    result.append((line, line, m.group(1), m.group(3)))
                else:
                    m2 = _MULTILINE_CELL_START_RE.match(line)
                    if m2:
                        # Начало многострочной ячейки с кириллицей в описании —
                        # отправляем полную строку, извлекаем только описание
                        result.append((line, line, m2.group(1), ''))
                    else:
                        # Обычная строка — переводим целиком
                        result.append((line, line, '', ''))

            pos = end + 1

        return result

    def _batch_translate(self, lines: list[str], translator) -> list[str]:
        text = '\n'.join(lines)
        result = translator.translate(text, system_prompt=_BATCH_PROMPT)
        translated = result.strip().split('\n')
        if len(translated) < len(lines):
            translated += lines[len(translated):]
        return translated[:len(lines)]