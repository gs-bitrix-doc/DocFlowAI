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

# Российские города
_RUSSIAN_CITIES = re.compile(
    r'\b(Москва|Санкт-Петербург|Новосибирск|Екатеринбург|Казань|Нижний Новгород|Калининград|Moscow|Saint Petersburg)\b'
)


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

        if orig["code_blocks"] != trans["code_blocks"]:
            result.add_error(
                f"Количество блоков кода изменилось: {orig['code_blocks']} → {trans['code_blocks']}"
            )

        if orig["bitrix_blocks"] != trans["bitrix_blocks"]:
            result.add_error(
                f"Количество битрикс-блоков изменилось: {orig['bitrix_blocks']} → {trans['bitrix_blocks']}"
            )

        # --- Проверка словаря терминов ---

        if dictionary:
            translated_no_code = self._strip_code(translated)
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

        # --- Проверка запрещённого контента ---

        translated_no_code = self._strip_code(translated)

        for pattern, message in _FORBIDDEN_PATTERNS:
            if pattern.search(translated_no_code):
                result.add_warning(message)

        if _RUSSIAN_CITIES.search(translated_no_code):
            result.add_warning("Остались российские города/адреса")

        if self._has_cyrillic(translated):
            result.add_warning("В переводе остался кириллический текст")

        return result

    def _extract(self, content: str) -> dict:
        return {
            "placeholders": len(re.findall(r'\[\[PROTECTED_\d+\]\]', content)),
            "headings": len(re.findall(r'^#{1,6}\s', content, re.MULTILINE)),
            "tables": len(re.findall(r'^#\|', content, re.MULTILINE)),
            "table_rows": len(re.findall(r'^\|\|', content, re.MULTILINE)),
            "code_blocks": len(re.findall(r'```', content)),
            "bitrix_blocks": len(re.findall(r'\{%', content)),
        }

    def _strip_code(self, content: str) -> str:
        """Убирает блоки кода и инлайн-код чтобы не проверять их содержимое."""
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]+`', '', content)
        return content

    def _has_cyrillic(self, text: str) -> bool:
        return bool(re.search(r'[а-яёА-ЯЁ]', text))