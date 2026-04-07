import re


class MarkdownProtector:
    _PATTERNS = [
        # 1. Frontmatter
        re.compile(r'^---\n.*?\n---\n', re.DOTALL),
        # 2. Битрикс-блоки без заголовка: {% list %}, {% if %}, {% endif %}, {% endnote %} и т.д.
        #    Теги с заголовком (note/cut) обрабатываются отдельно — см. _NOTE_TAG_PATTERN
        re.compile(r'\{%(?!\s*(?:note|cut)\s+[^"]*").*?%}', re.DOTALL),
        # 3. Названия полей API: **TYPE_ID**, **CATEGORY_ID** и т.д.
        re.compile(r'\*\*[A-Z][A-Z0-9_.*]+\*\*'),
        # 4. Якоря: {#deal}, {#anchor-name}
        re.compile(r'\{#[a-z][a-z0-9-]*\}'),
        # 5. Картинки: ![alt](url) — до ссылок, так как начинаются с !
        re.compile(r'!\[.*?]\(.*?\)'),
        # 6. Авто-заголовки [{#T}](url) — спецсинтаксис YFM, переводить нечего
        re.compile(r'\[\{#T\}]\([^)]*?\)'),
    ]

    # Теги с заголовком: {% note tip "Title" %}, {% cut "Title" %}
    # Синтаксис защищается, заголовок остаётся видимым для LLM —
    # аналогично тому как ссылки защищают URL, оставляя текст
    _NOTE_TAG_PATTERN = re.compile(
        r'(\{%\s*(?:note\s+\w+|cut)\s+")(.*?)("\s*%\})'
    )

    # Маркер обязательного поля ^*^ — защищаем до инлайн-кода,
    # иначе * внутри путает модель и она добавляет лишние звёздочки
    _REQUIRED_MARKER_PATTERN = re.compile(r'\^\*\^')

    # (?<!\[) исключает `тип` внутри [`тип`](url) — такие ссылки защищаются целиком ниже.
    _INLINE_CODE_PATTERN = re.compile(r'(?<!\[)`[^`\n]+`')

    # Блоки кода — целиком (кириллица внутри переводится отдельным шагом до protect)
    _CODE_BLOCK_PATTERN = re.compile(r'```.*?```', re.DOTALL)

    # YFM-таблица: [`тип`](url) | или [`т1`](u1) \| [`т2`](u2) | — защищаем тип + разделитель колонки.
    # Модель видит только описание; разделитель | никогда не путается с union-пайпами \|.
    # Должен применяться ДО _INLINE_CODE_LINK_PATTERN, чтобы перехватить эти ссылки первым.
    _YFM_CELL_TYPE_PATTERN = re.compile(
        r'^\[`[^`\n]+`\]\([^)\n]+\)(?:[ \t]*\\\|[ \t]*\[`[^`\n]+`\]\([^)\n]+\))*[ \t]*\|(?!\|)',
        re.MULTILINE,
    )

    # Ссылки: только URL защищается, текст остаётся для LLM
    # Исключение: [`тип`](url) вне таблиц — текст целиком инлайн-код, защищаем всю ссылку.
    # Иначе шаг 10 защитит `тип` внутри [...], получим [[[PROT_M]]][[PROT_N]] —
    # вложенные плейсхолдеры с ] внутри, которые LLM разрушает.
    _INLINE_CODE_LINK_PATTERN = re.compile(r'\[`[^`]+`\]\([^)]*?\)')
    _LINK_PATTERN = re.compile(r'\[([^\]]*?)]\(([^)]*?)\)')

    # Лейблы вкладок {% list tabs %}: строки "- Label" перед блоком с отступом 4 пробела
    _TAB_LABEL_PATTERN = re.compile(r'^- [^\n]+$(?=\n\n[ ]{4})', re.MULTILINE)

    def __init__(self):
        self._blocks: dict[str, str] = {}
        self._counter = 0
        self._type_urls: dict[str, str] = {}  # тип → URL из YFM-ячеек, для ремонта

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    def protect(self, content: str) -> str:
        self._blocks = {}
        self._counter = 0
        self._type_urls = {}

        # 1. Блоки кода — первыми (иначе ` съедает тройные бэктики)
        content = self._CODE_BLOCK_PATTERN.sub(self._protect_code_block, content)

        # 2. Теги с заголовком (note/cut) — до общего {%...%} паттерна
        #    Синтаксис защищается, заголовок остаётся для LLM
        content = self._NOTE_TAG_PATTERN.sub(self._replace_note_tag, content)

        # 3-7. Frontmatter, битрикс-блоки, API-поля, якоря, картинки, [{#T}](url)
        for pattern in self._PATTERNS:
            content = pattern.sub(self._replace, content)

        # 7. Лейблы вкладок — после {%...%} тегов
        content = self._TAB_LABEL_PATTERN.sub(self._replace, content)

        # 8. Инлайн-код — ДО ссылок (иначе `тип` внутри [`тип`](url) защитится раньше ссылки)
        content = self._INLINE_CODE_PATTERN.sub(self._replace, content)

        # 9. Ссылки: YFM-ячейки → только URL, [`тип`](url) вне таблиц → целиком, остальные → только URL
        content = self._YFM_CELL_TYPE_PATTERN.sub(self._replace_type_cell, content)
        content = self._INLINE_CODE_LINK_PATTERN.sub(self._replace, content)
        content = self._LINK_PATTERN.sub(self._replace_link, content)

        # 10. Маркер обязательного поля ^*^ — после инлайн-кода
        content = self._REQUIRED_MARKER_PATTERN.sub(self._replace, content)

        return content

    # Модель иногда добавляет лишние скобки вокруг текста ссылки: [[text]](url) → [text](url)
    _DOUBLE_BRACKET_LINK_RE = re.compile(r'\[\[([^\[\]]+)\]\](\([^)]*\))')

    # Сломанная ячейка типа: [`тип`] без (url) перед разделителем | или \|
    # Модель «знает» паттерн YFM и пишет [`string`| из памяти, теряя URL из плейсхолдера
    _BROKEN_CELL_LINK_RE = re.compile(
        r'\[`([^`\n]+)`\](?!\()([ \t]*(?:\\\||(?<!\|)\|(?!\|)))'
    )

    def restore(self, content: str) -> str:
        for placeholder, original in reversed(list(self._blocks.items())):
            content = content.replace(placeholder, original)
        content = self._DOUBLE_BRACKET_LINK_RE.sub(r'[\1]\2', content)
        content = self._repair_broken_cell_links(content)
        return content

    def _repair_broken_cell_links(self, content: str) -> str:
        """Восстанавливает [`тип`](url) если модель потеряла URL из плейсхолдера."""
        if not self._type_urls:
            return content

        def _fix(m: re.Match) -> str:
            url = self._type_urls.get(m.group(1))
            if url:
                return f'[`{m.group(1)}`]({url}){m.group(2)}'
            return m.group(0)

        return self._BROKEN_CELL_LINK_RE.sub(_fix, content)

    def _replace_type_cell(self, match: re.Match) -> str:
        """В YFM-ячейках защищает только URL: [`тип`](url) → [`тип`][[PROTECTED_N]].

        Оставляет [`тип`] и | видимыми для модели — понятная структура ссылки,
        модели незачем достраивать содержимое из памяти.
        Запоминает тип→URL для _repair_broken_cell_links на случай потери плейсхолдера.
        """
        full = match.group(0)
        for m in re.finditer(r'`([^`\n]+)`\]\(([^)\n]+)\)', full):
            self._type_urls[m.group(1)] = m.group(2)

        def _protect_url(m: re.Match) -> str:
            ph = f"[[PROTECTED_{self._counter}]]"
            self._blocks[ph] = m.group(0)  # сохраняем "(url)" с скобками
            self._counter += 1
            return ph

        return re.sub(r'\([^)\n]+\)', _protect_url, full)

    def _replace(self, match: re.Match) -> str:
        placeholder = f"[[PROTECTED_{self._counter}]]"
        self._blocks[placeholder] = match.group(0)
        self._counter += 1
        return placeholder

    def _protect_code_block(self, match: re.Match) -> str:
        return self._replace(match)

    def _replace_note_tag(self, match: re.Match) -> str:
        """Защищает синтаксис тега, оставляя заголовок видимым для LLM.

        {% note tip "Title" %}  →  [[PROTECTED_N]]Title[[PROTECTED_M]]

        При пустом заголовке ("") защищаем тег целиком — нечего переводить.
        """
        prefix, title, suffix = match.group(1), match.group(2), match.group(3)
        if not title.strip():
            return self._replace(match)
        prefix_ph = f"[[PROTECTED_{self._counter}]]"
        self._blocks[prefix_ph] = prefix
        self._counter += 1
        suffix_ph = f"[[PROTECTED_{self._counter}]]"
        self._blocks[suffix_ph] = suffix
        self._counter += 1
        return f"{prefix_ph}{title}{suffix_ph}"

    # Домены .ru в URL → .com (замена до защиты, LLM ссылку не видит)
    _RU_URL_RE = re.compile(r'(://[^/?#\s)]+)\.ru\b')

    def _replace_link(self, match: re.Match) -> str:
        text = match.group(1)
        url = self._RU_URL_RE.sub(r'\1.com', match.group(2))
        url_placeholder = f"[[PROTECTED_{self._counter}]]"
        self._blocks[url_placeholder] = f"({url})"
        self._counter += 1
        return f"[{text}]{url_placeholder}"