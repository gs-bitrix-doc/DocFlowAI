import re


_CODE_BLOCK_PATTERN = re.compile(r'(```[^\n]*\n)(.*?)(```)', re.DOTALL)
_CYRILLIC_DOUBLE = re.compile(r'"([^"]*[а-яёА-ЯЁ][^"]*)"')
_CYRILLIC_SINGLE = re.compile(r"'([^']*[а-яёА-ЯЁ][^']*)'")
_INLINE_CODE_CYRILLIC = re.compile(r'`([^`\n]*[а-яёА-ЯЁ][^`\n]*)`')

_BATCH_PROMPT = (
    "Translate each Russian string to English. "
    "Return only the translations, one per line, in the same order. "
    "No explanations, no quotes, no extra text."
)


class CodeTranslator:
    """Переводит кириллические строковые значения внутри блоков кода и инлайн-кода."""

    def __init__(self, translator):
        self._translator = translator

    def translate(self, content: str) -> str:
        content = _CODE_BLOCK_PATTERN.sub(self._process_block, content)
        content = self._process_inline_code(content)
        return content

    def _process_block(self, match: re.Match) -> str:
        opening, body, closing = match.group(1), match.group(2), match.group(3)

        strings_double = _CYRILLIC_DOUBLE.findall(body)
        strings_single = _CYRILLIC_SINGLE.findall(body)
        all_cyrillic = strings_double + strings_single

        if not all_cyrillic:
            return match.group(0)

        unique = list(dict.fromkeys(all_cyrillic))
        translations = self._batch_translate(unique)
        translation_map = dict(zip(unique, translations))

        def replace_double(m: re.Match) -> str:
            return f'"{translation_map.get(m.group(1), m.group(1))}"'

        def replace_single(m: re.Match) -> str:
            return f"'{translation_map.get(m.group(1), m.group(1))}'"

        body = _CYRILLIC_DOUBLE.sub(replace_double, body)
        body = _CYRILLIC_SINGLE.sub(replace_single, body)
        return f"{opening}{body}{closing}"

    def _process_inline_code(self, content: str) -> str:
        cyrillic_inline = _INLINE_CODE_CYRILLIC.findall(content)
        if not cyrillic_inline:
            return content

        unique = list(dict.fromkeys(cyrillic_inline))
        translations = self._batch_translate(unique)
        translation_map = dict(zip(unique, translations))

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