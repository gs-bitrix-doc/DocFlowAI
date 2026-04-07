import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


# Домены и паттерны которых не должно быть в переводе
_FORBIDDEN_PATTERNS = [
    (re.compile(r'https?://\S+\.ru[/\s"\'`]'), "Остался .ru домен"),
    (re.compile(r'\bbitrix24\.ru\b'), "Остался домен bitrix24.ru"),
    (re.compile(r'\b(GigaChat|YandexGPT|Яндекс|Yandex|ВКонтакте|VKontakte)\b', re.IGNORECASE), "Остался запрещённый бренд"),
    (re.compile(r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'), "Остался российский номер телефона"),
]

_RUSSIAN_CITIES = re.compile(
    r'\b(Москва|Санкт-Петербург|Новосибирск|Екатеринбург|Казань|Нижний Новгород|Калининград|Moscow|Saint Petersburg)\b'
)

_CYRILLIC_RE = re.compile(r'[а-яёА-ЯЁ]')
_ANCHOR_DEF_RE = re.compile(r'\{#([\w-]+)\}')
_ANCHOR_REF_RE = re.compile(r'\(#([\w-]+)\)')
# Ссылка без URL: [текст без закрывающей скобки — признак что LLM удалил ](url)
_BROKEN_LINK_RE = re.compile(r'\[[^\]]{1,200}\](?!\()')
# Сломанная ячейка типа: [`type` без закрывающей ](url) — LLM съел разделитель
_BROKEN_CELL_TYPE_RE = re.compile(r'\[`[^`\n]+`[^(`\]]')
# Мусор от утёкшего плейсхолдера: ]](url) в тексте
_LEAKED_PLACEHOLDER_RE = re.compile(r'\]\]\([^)]+\)')


class StructureValidator:
    def validate(
        self,
        original: str,
        translated: str,
        dictionary: dict[str, str] | None = None,
    ) -> ValidationResult:
        result = ValidationResult()
        orig = self._extract(original)
        trans = self._extract(translated)

        translated_no_code = self._strip_code(translated)

        # --- Структурные проверки ---

        if trans["placeholders"] > 0:
            result.add_error(
                f"В переводе остались незамененные плейсхолдеры: {trans['placeholders']} шт."
            )

        if orig["headings"] != trans["headings"]:
            result.add_error(
                f"Количество заголовков изменилось: {orig['headings']} → {trans['headings']}"
            )

        if orig["tables"] != trans["tables"]:
            result.add_error(
                f"Количество таблиц изменилось: {orig['tables']} → {trans['tables']}"
            )

        if orig["table_rows"] != trans["table_rows"]:
            result.add_error(
                f"Количество строк таблиц изменилось: {orig['table_rows']} → {trans['table_rows']}"
            )

        if orig["table_cell_closers"] != trans["table_cell_closers"]:
            result.add_warning(
                f"Количество || в таблицах изменилось: {orig['table_cell_closers']} → {trans['table_cell_closers']} "
                f"(LLM мог добавить лишние || в многострочные ячейки)"
            )

        if orig["code_blocks"] != trans["code_blocks"]:
            result.add_error(
                f"Количество блоков кода изменилось: {orig['code_blocks']} → {trans['code_blocks']}"
            )

        if orig["bitrix_blocks"] != trans["bitrix_blocks"]:
            result.add_error(
                f"Количество битрикс-блоков изменилось: {orig['bitrix_blocks']} → {trans['bitrix_blocks']}"
            )

        # --- Проверка сломанных ссылок ---
        # Считаем ссылки вида [text](url) в оригинале и переводе (вне кода)
        orig_no_code = self._strip_code(original)
        orig_links = len(re.findall(r'\[[^\]]+\]\(', orig_no_code))
        trans_links = len(re.findall(r'\[[^\]]+\]\(', translated_no_code))
        if trans_links < orig_links:
            result.add_warning(
                f"Возможно сломаны ссылки: в оригинале {orig_links}, в переводе {trans_links}"
            )

        # --- Проверка якорей ---

        orig_anchors = set(_ANCHOR_DEF_RE.findall(original))
        trans_anchors = set(_ANCHOR_DEF_RE.findall(translated))
        missing_anchors = orig_anchors - trans_anchors
        if missing_anchors:
            result.add_error(
                f"Потеряны якоря: {', '.join(f'{{#{a}}}' for a in sorted(missing_anchors))}"
            )

        # Внутренние ссылки (#anchor) должны ссылаться на существующие якоря
        trans_refs = set(_ANCHOR_REF_RE.findall(translated))
        broken_refs = trans_refs - trans_anchors
        if broken_refs:
            result.add_warning(
                f"Ссылки на несуществующие якоря: {', '.join(f'(#{r})' for r in sorted(broken_refs))}"
            )

        # --- Проверка словаря терминов ---

        if dictionary:
            for ru_term, en_term in dictionary.items():
                if not re.search(r'\b' + re.escape(ru_term) + r'\b', original, re.IGNORECASE):
                    continue
                if re.search(r'\b' + re.escape(ru_term) + r'\b', translated_no_code, re.IGNORECASE):
                    result.add_warning(
                        f"Термин не переведён: «{ru_term}» → ожидалось «{en_term}»"
                    )
                elif not re.search(re.escape(en_term), translated_no_code, re.IGNORECASE):
                    result.add_warning(
                        f"Термин переведён неверно: «{ru_term}» → ожидалось «{en_term}»"
                    )

        # --- Проверка артефактов перевода ---

        if _BROKEN_CELL_TYPE_RE.search(translated):
            result.add_warning("Возможно сломана ячейка типа: [`type` без закрывающей ](url)")

        if _LEAKED_PLACEHOLDER_RE.search(translated):
            result.add_warning("Мусор от плейсхолдера: ]](url) в тексте — утечка контента")

        # --- Проверка запрещённого контента ---

        for pattern, message in _FORBIDDEN_PATTERNS:
            if pattern.search(translated_no_code):
                result.add_warning(message)

        if _RUSSIAN_CITIES.search(translated_no_code):
            result.add_warning("Остались российские города/адреса")

        cyrillic_match = _CYRILLIC_RE.search(translated_no_code)
        if cyrillic_match:
            snippet = self._snippet(translated_no_code, cyrillic_match.start())
            result.add_warning(f"В переводе остался кириллический текст: …{snippet}…")

        return result

    def _extract(self, content: str) -> dict:
        no_code = self._strip_code(content)
        return {
            "placeholders": len(re.findall(r'\[\[PROTECTED_\d+\]\]', content)),
            "headings": len(re.findall(r'^#{1,6}\s', content, re.MULTILINE)),
            "tables": len(re.findall(r'^#\|', content, re.MULTILINE)),
            "table_rows": len(re.findall(r'^\|\|', content, re.MULTILINE)),
            "table_cell_closers": len(re.findall(r'\|\|', no_code)),
            "code_blocks": len(re.findall(r'```', content)),
            "bitrix_blocks": len(re.findall(r'\{%', content)),
        }

    def _strip_code(self, content: str) -> str:
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`\n]+`', '', content)
        return content

    def _snippet(self, text: str, pos: int, radius: int = 40) -> str:
        start = max(0, pos - radius)
        end = min(len(text), pos + radius)
        return text[start:end].replace('\n', ' ').strip()