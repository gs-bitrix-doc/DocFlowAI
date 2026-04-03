import re


class MarkdownProtector:
    _PATTERNS = [
        # 1. Frontmatter
        re.compile(r'^---\n.*?\n---\n', re.DOTALL),
        # 2. Битрикс-блоки: {% note %}...{% endnote %}, {% list %}...{% endlist %}
        re.compile(r'\{%.*?%}', re.DOTALL),
        # 3. Названия полей API: **TYPE_ID**, **CATEGORY_ID** и т.д.
        re.compile(r'\*\*[A-Z][A-Z0-9_.*]+\*\*'),
        # 4. Якоря: {#deal}, {#anchor-name}
        re.compile(r'\{#[a-z][a-z0-9-]*\}'),
        # 5. Картинки: ![alt](url) — до ссылок, так как начинаются с !
        re.compile(r'!\[.*?]\(.*?\)'),
    ]

    # 6. Инлайн-код: после ссылок, иначе [[PROTECTED_N]] внутри [text](url)
    #    содержит ], что ломает паттерн ссылки
    _INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')

    # 5. Блоки кода — целиком (кириллица внутри переводится отдельным шагом до protect)
    _CODE_BLOCK_PATTERN = re.compile(r'```.*?```', re.DOTALL)

    # 7. Ссылки: только URL защищается, текст остаётся для LLM
    _LINK_PATTERN = re.compile(r'\[([^\]]*?)]\(([^)]*?)\)')

    # 9. Лейблы вкладок {% list tabs %}: строки "- Label" перед блоком с отступом 4 пробела
    _TAB_LABEL_PATTERN = re.compile(r'^- [^\n]+$(?=\n\n[ ]{4})', re.MULTILINE)

    def __init__(self):
        self._blocks: dict[str, str] = {}
        self._counter = 0

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    def protect(self, content: str) -> str:
        self._blocks = {}
        self._counter = 0

        # Блоки кода — первыми, до инлайн-кода (иначе ` съедает тройные бэктики)
        content = self._CODE_BLOCK_PATTERN.sub(self._protect_code_block, content)

        for pattern in self._PATTERNS:
            content = pattern.sub(self._replace, content)

        # Лейблы вкладок — после защиты {%...%} тегов, до ссылок
        content = self._TAB_LABEL_PATTERN.sub(self._replace, content)

        # Ссылки: защищаем только URL, текст оставляем для LLM
        content = self._LINK_PATTERN.sub(self._replace_link, content)

        return content

    def restore(self, content: str) -> str:
        for placeholder, original in reversed(list(self._blocks.items())):
            content = content.replace(placeholder, original)
        return content

    def _replace(self, match: re.Match) -> str:
        placeholder = f"[[PROTECTED_{self._counter}]]"
        self._blocks[placeholder] = match.group(0)
        self._counter += 1
        return placeholder

    def _protect_code_block(self, match: re.Match) -> str:
        return self._replace(match)

    def _replace_link(self, match: re.Match) -> str:
        text = match.group(1)
        url = match.group(2)
        url_placeholder = f"[[PROTECTED_{self._counter}]]"
        self._blocks[url_placeholder] = f"({url})"
        self._counter += 1
        return f"[{text}]{url_placeholder}"