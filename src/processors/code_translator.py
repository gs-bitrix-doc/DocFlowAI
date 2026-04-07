import re


_CODE_BLOCK_PATTERN = re.compile(r'(```[^\n]*\n)(.*?)(```)', re.DOTALL)
_CYRILLIC_DOUBLE = re.compile(r'"([^"]*[а-яёА-ЯЁ][^"]*)"')
_CYRILLIC_SINGLE = re.compile(r"'([^']*[а-яёА-ЯЁ][^']*)'")
_INLINE_CODE_CYRILLIC = re.compile(r'`(?!])([^`\n| ][^`\n|]*[а-яёА-ЯЁ][^`\n|]*|[а-яёА-ЯЁ][^`\n|]*)`')

_BATCH_PROMPT = (
    "Translate each Russian string to English. "
    "Return only the translations, one per line, in the same order. "
    "No explanations, no quotes, no extra text. "
    "Localization rules: Russia/Россия → United States, "
    "Russian cities → American cities, +7 → +1, .ru domains → .com."
)


class CodeTranslator:
    """Переводит кириллические строковые значения внутри блоков кода и инлайн-кода."""

    def __init__(self, translator):
        self._translator = translator

    def translate(self, content: str) -> str:
        block_cyrillic = []
        for match in _CODE_BLOCK_PATTERN.finditer(content):
            body = match.group(2)
            block_cyrillic += _CYRILLIC_DOUBLE.findall(body)
            block_cyrillic += _CYRILLIC_SINGLE.findall(body)

        inline_cyrillic = _INLINE_CODE_CYRILLIC.findall(content)

        if not block_cyrillic and not inline_cyrillic:
            return content

        translation_map = {}

        if block_cyrillic:
            unique_block = list(dict.fromkeys(block_cyrillic))
            block_translations = self._batch_translate(unique_block)
            translation_map.update(dict(zip(unique_block, block_translations)))

        if inline_cyrillic:
            unique_inline = list(dict.fromkeys(inline_cyrillic))
            inline_translations = self._batch_translate(unique_inline)
            translation_map.update(dict(zip(unique_inline, inline_translations)))

        content = _CODE_BLOCK_PATTERN.sub(
            lambda m: self._apply_block(m, translation_map), content
        )
        content = self._apply_inline_code(content, translation_map)
        return content

    def _apply_block(self, match: re.Match, translation_map: dict) -> str:
        opening, body, closing = match.group(1), match.group(2), match.group(3)

        if not _CYRILLIC_DOUBLE.search(body) and not _CYRILLIC_SINGLE.search(body):
            return match.group(0)

        def replace_double(m: re.Match) -> str:
            return f'"{translation_map.get(m.group(1), m.group(1))}"'

        def replace_single(m: re.Match) -> str:
            return f"'{translation_map.get(m.group(1), m.group(1))}'"

        body = _CYRILLIC_DOUBLE.sub(replace_double, body)
        body = _CYRILLIC_SINGLE.sub(replace_single, body)
        return f"{opening}{body}{closing}"

    def _apply_inline_code(self, content: str, translation_map: dict) -> str:
        def replace_inline(m: re.Match) -> str:
            original = m.group(1)
            return f'`{translation_map.get(original, original)}`'

        return _INLINE_CODE_CYRILLIC.sub(replace_inline, content)

    def _batch_translate(self, strings: list[str]) -> list[str]:
        text = "\n".join(strings)
        result = self._translator.translate(text, system_prompt=_BATCH_PROMPT)
        lines = result.strip().split("\n")

        if len(lines) < len(strings):
            lines += strings[len(lines):]

        return lines[: len(strings)]