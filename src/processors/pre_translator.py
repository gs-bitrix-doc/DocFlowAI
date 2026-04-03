import json
import re
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "pre_translator"


def _load(filename: str) -> dict:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


INCLUDE_LABELS: dict = _load("include_labels.json")
NOTE_TITLES: dict = _load("note_titles.json")
SECTION_HEADINGS: dict = _load("section_headings.json")
STATIC_TERMS: dict = _load("static_terms.json")

_TYPE_ELEMENT_HEADING_PATTERN = re.compile(
    r'^(#{1,6})\s+Тип элемента\s+(\S+)',
    re.MULTILINE,
)
_INCLUDE_PATTERN = re.compile(r'(\{%\s*include(?:\s+notitle)?\s*)\[([^\]]+)](\([^)]+\)\s*%\})')
_NOTE_TITLE_PATTERN = re.compile(r'(\{%\s*note\s+\w+\s+")([^"]+)(".*?%\})')
_TABLE_HEADER_PATTERN = re.compile(r'\|\| \*\*Название\*\*\n`тип` \| \*\*Описание\*\* \|\|')
_TYP_PATTERN = re.compile(r'`тип`')
_ALT_TEXT_PATTERN = re.compile(r'(!\[)alt-текст(])')
_SECTION_HEADING_PATTERN = re.compile(
    r'^(#+)\s+(' + '|'.join(re.escape(k) for k in SECTION_HEADINGS) + r')\s*$',
    re.MULTILINE,
)
_STATIC_TERMS_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in sorted(STATIC_TERMS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)


class PreTranslator:
    def translate(self, content: str) -> str:
        content = _TYPE_ELEMENT_HEADING_PATTERN.sub(r'\1 item \2 type', content)
        content = _INCLUDE_PATTERN.sub(self._replace_include, content)
        content = _NOTE_TITLE_PATTERN.sub(self._replace_note_title, content)
        content = _TABLE_HEADER_PATTERN.sub('|| **Name**\n`type` | **Description** ||', content)
        content = _TYP_PATTERN.sub('`type`', content)
        content = _ALT_TEXT_PATTERN.sub(r'\1alt text\2', content)
        content = _SECTION_HEADING_PATTERN.sub(self._replace_section_heading, content)
        content = _STATIC_TERMS_PATTERN.sub(self._replace_term, content)
        return content

    def _replace_include(self, match: re.Match) -> str:
        prefix, label, suffix = match.group(1), match.group(2), match.group(3)
        filename_match = re.search(r'([^/]+\.md)', suffix)
        if filename_match:
            english_label = INCLUDE_LABELS.get(filename_match.group(1), label)
        else:
            english_label = label
        return f"{prefix}[{english_label}]{suffix}"

    def _replace_term(self, match: re.Match) -> str:
        return STATIC_TERMS.get(match.group(1).lower(), match.group(1))

    def _replace_note_title(self, match: re.Match) -> str:
        prefix, title, suffix = match.group(1), match.group(2), match.group(3)
        english_title = NOTE_TITLES.get(title, title)
        return f"{prefix}{english_title}{suffix}"

    def _replace_section_heading(self, match: re.Match) -> str:
        hashes, title = match.group(1), match.group(2)
        return f"{hashes} {SECTION_HEADINGS.get(title, title)}"