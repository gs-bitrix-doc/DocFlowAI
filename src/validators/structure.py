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

        if dictionary:
            for ru_term, en_term in dictionary.items():
                ru_present = ru_term.lower() in translated.lower()
                en_present = en_term.lower() in translated.lower()

                if ru_present:
                    result.add_warning(
                        f"Термин не переведён: «{ru_term}» → ожидалось «{en_term}»"
                    )
                elif not en_present:
                    result.add_warning(
                        f"Возможно неверный перевод: «{ru_term}» → ожидалось «{en_term}»"
                    )

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
