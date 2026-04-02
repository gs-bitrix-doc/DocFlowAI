import re

# Метки include-блоков: имя файла → английская метка
INCLUDE_LABELS = {
    "required.md": "Note on parameters",
    "examples.md": "Note on examples",
    "error-info.md": "Error handling",
    "error-info-v3.md": "Error handling",
    "system-errors.md": "System errors",
    "events-index.md": "Server availability",
    "auth-params-in-events.md": "Auth parameters in events",
    "rest-result.md": "Result format",
    "result-common-data.md": "Common result data",
    "widget_crm.md": "Widget in CRM",
}

# Заголовки битрикс-нот: русский → английский
NOTE_TITLES = {
    "Развитие метода остановлено": "Method development has been halted",
    "Связанные методы и темы": "Related methods and topics",
    "Внимание": "Attention",
    "Внимание!": "Attention!",
    "Важно": "Important",
    "Совет": "Tip",
    "Примечание": "Note",
    "Устаревшие поля": "Deprecated fields",
    "Ограничение": "Limit",
}

_INCLUDE_PATTERN = re.compile(r'(\{%\s*include(?:\s+notitle)?\s*)\[([^\]]+)](\([^)]+\)\s*%\})')
_NOTE_TITLE_PATTERN = re.compile(r'(\{%\s*note\s+\w+\s+")([^"]+)(".*?%\})')
_TYP_PATTERN = re.compile(r'`тип`')


class PreTranslator:
    def translate(self, content: str) -> str:
        content = _INCLUDE_PATTERN.sub(self._replace_include, content)
        content = _NOTE_TITLE_PATTERN.sub(self._replace_note_title, content)
        content = _TYP_PATTERN.sub('`type`', content)
        return content

    def _replace_include(self, match: re.Match) -> str:
        prefix, label, suffix = match.group(1), match.group(2), match.group(3)
        # извлекаем имя файла из пути вида (../../_includes/required.md)
        filename_match = re.search(r'([^/]+\.md)', suffix)
        if filename_match:
            english_label = INCLUDE_LABELS.get(filename_match.group(1), label)
        else:
            english_label = label
        return f"{prefix}[{english_label}]{suffix}"

    def _replace_note_title(self, match: re.Match) -> str:
        prefix, title, suffix = match.group(1), match.group(2), match.group(3)
        english_title = NOTE_TITLES.get(title, title)
        return f"{prefix}{english_title}{suffix}"