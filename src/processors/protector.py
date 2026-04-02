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
        # 5. Блоки кода: ```...```
        re.compile(r'```.*?```', re.DOTALL),
        # 6. Картинки: ![alt](url) — до ссылок, так как начинаются с !
        re.compile(r'!\[.*?]\(.*?\)'),
        # 7. Ссылки: [text](url) — до инлайн-кода, чтобы не путаться с [[PROTECTED_N]]
        re.compile(r'\[.*?]\(.*?\)'),
        # 8. Инлайн-код: `code`
        re.compile(r'`[^`]+`'),
    ]

    def __init__(self):
        self._blocks: dict[str, str] = {}
        self._counter = 0

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    def protect(self, content: str) -> str:
        self._blocks = {}
        self._counter = 0

        for pattern in self._PATTERNS:
            content = pattern.sub(self._replace, content)

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
