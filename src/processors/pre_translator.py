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

# Требуем латинский идентификатор после "Тип элемента" / "Тип" / "Параметр",
# чтобы не ломать заголовки вида "### Тип использования шаблона"
_TYPE_ELEMENT_HEADING_PATTERN = re.compile(
    r'^(#{1,6})\s+Тип элемента\s+([a-zA-Z][a-zA-Z0-9._\[\]]*)',
    re.MULTILINE,
)
_TYPE_HEADING_PATTERN = re.compile(
    r'^(#{1,6})\s+Тип\s+([a-zA-Z][a-zA-Z0-9._\[\]]*)',
    re.MULTILINE,
)
_PARAMETER_HEADING_PATTERN = re.compile(
    r'^(#{1,6})\s+Параметр\s+([a-zA-Z][a-zA-Z0-9._\[\]]*)',
    re.MULTILINE,
)
_INCLUDE_PATTERN = re.compile(r'(\{%\s*include(?:\s+notitle)?\s*)\[([^\]]+)](\([^)]+\)\s*%\})')
# note и cut — оба используют заголовок в кавычках внутри тега
_NOTE_TITLE_PATTERN = re.compile(r'(\{%\s*(?:note\s+\w+|cut)\s+")([^"]+)(".*?%\})')
_TABLE_HEADER_PATTERN = re.compile(r'\|\| \*\*Название\*\*\n`тип` \| \*\*Описание\*\* \|\|')
# Названия колонок таблиц в жирном — заменяем независимо от количества и порядка колонок
_TABLE_COLUMN_NAMES = {
    'Код': 'Code',
    'Описание': 'Description',
    'Значение': 'Value',
    'Статус': 'Status',
}
_TABLE_COLUMN_PATTERN = re.compile(
    r'\*\*(' + '|'.join(_TABLE_COLUMN_NAMES.keys()) + r')\*\*'
)
_TYP_PATTERN = re.compile(r'`тип`')
_ALT_TEXT_PATTERN = re.compile(r'(!\[)alt-текст(])')
_HTTP_STATUS_PATTERN = re.compile(r'HTTP-статус:', re.IGNORECASE)

# Локализация: телефоны, города, локаль
_PHONE_RU_RE = re.compile(r'\+7([\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})')
_LOCALE_RU_RE = re.compile(r"(['\"])ru\1")
_RUSSIAN_CITY_MAP = {
    'Москва': 'New York',
    'Санкт-Петербург': 'Los Angeles',
    'Новосибирск': 'Chicago',
    'Екатеринбург': 'Houston',
    'Казань': 'Phoenix',
    'Нижний Новгород': 'Philadelphia',
    'Калининград': 'San Antonio',
    'Moscow': 'New York',
    'Saint Petersburg': 'Los Angeles',
}
_RUSSIAN_CITY_RE = re.compile(r'\b(' + '|'.join(map(re.escape, _RUSSIAN_CITY_MAP)) + r')\b')

# Специфические замены доменов — детерминированно, до защиты плейсхолдерами
_URL_REPLACEMENTS = [
    ('repos.1c-bitrix.ru/webhook/app.json', 'dl.bitrix24.com/webhook/app-world.json'),
    ('1c-bitrix.ru', 'bitrixsoft.com'),
    ('oauth.bitrix24.tech', 'oauth.bitrix.info'),
    ('marta.bitrix24.tech', 'marta.bitrix.info'),
    ('rtc-cloud-ms1.bitrix24.tech', 'rtc-cloud-ms1.bitrix.info'),
    ('api.bitrix24.tech/api/v1/', 'api.bitrix24.com/api/v1/'),
    ('mcp-dev.bitrix24.tech/mcp', 'mcp-dev.bitrix24.com/mcp'),
]
# [ \t]*$ вместо \s*$ — не захватываем \n после заголовка (иначе съедается пустая строка)
_SECTION_HEADING_PATTERN = re.compile(
    r'^(#+)\s+(' + '|'.join(re.escape(k) for k in SECTION_HEADINGS) + r')[ \t]*$',
    re.MULTILINE,
)
_STATIC_TERMS_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in sorted(STATIC_TERMS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)


class PreTranslator:
    def translate(self, content: str) -> str:
        content = _TYPE_ELEMENT_HEADING_PATTERN.sub(r'\1 \2 item type', content)
        content = _TYPE_HEADING_PATTERN.sub(r'\1 \2 type', content)
        content = _PARAMETER_HEADING_PATTERN.sub(r'\1 Parameter \2', content)
        content = _INCLUDE_PATTERN.sub(self._replace_include, content)
        content = _NOTE_TITLE_PATTERN.sub(self._replace_note_title, content)
        content = _TABLE_HEADER_PATTERN.sub('|| **Name**\n`type` | **Description** ||', content)
        content = _TABLE_COLUMN_PATTERN.sub(self._replace_column_name, content)
        content = _HTTP_STATUS_PATTERN.sub('HTTP status:', content)
        content = _TYP_PATTERN.sub('`type`', content)
        content = _ALT_TEXT_PATTERN.sub(r'\1alt text\2', content)
        content = _SECTION_HEADING_PATTERN.sub(self._replace_section_heading, content)
        content = _STATIC_TERMS_PATTERN.sub(self._replace_term, content)
        for old, new in _URL_REPLACEMENTS:
            content = content.replace(old, new)
        content = _PHONE_RU_RE.sub(r'+1\1', content)
        content = _RUSSIAN_CITY_RE.sub(lambda m: _RUSSIAN_CITY_MAP[m.group(1)], content)
        content = _LOCALE_RU_RE.sub(lambda m: m.group(1) + 'de' + m.group(1), content)
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

    def _replace_column_name(self, match: re.Match) -> str:
        return f"**{_TABLE_COLUMN_NAMES[match.group(1)]}**"

    def _replace_section_heading(self, match: re.Match) -> str:
        hashes, title = match.group(1), match.group(2)
        return f"{hashes} {SECTION_HEADINGS.get(title, title)}"