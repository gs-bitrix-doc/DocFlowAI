# DocFlow AI

Инструмент для автоматического перевода `.md` файлов документации с сохранением структуры.

## Как запустить

**1. Установить зависимости:**
```bash
uv add requests python-dotenv click mistune
```

**2. Заполнить `.env`** (скопировать из `.env.example`):
```env
API_KEY=your_api_key_here
BASE_URL=https://litellm.i.bitrix24.ru/v1
MODEL=gpt-oss-120b
```

**3. Запустить:**

```bash
# Перевести один файл
python main.py input/crm-deal-get.md

# Перевести всю папку
python main.py --dir input/

# Проверить пайплайн без перевода (без API ключа)
python main.py input/crm-deal-get.md --dry-run
python main.py --dir input/ --dry-run
```

Результат сохраняется в `output/` с суффиксом `.en.md`:
```
input/crm-deal-get.md → output/crm-deal-get.en.md
```

---

## Архитектура

```
DocFlowAI/
├── input/                      # .md файлы для перевода
├── output/                     # переведённые файлы (.en.md)
├── logs/                       # логи работы скрипта
├── data/
│   ├── prompt.txt              # системный промпт для LLM
│   ├── dictionary.json         # словарь терминов RU → EN (промпт + валидатор)
│   ├── glossary.json           # расширенный словарь 903 термина (только валидатор)
│   └── pre_translator/         # статичные замены для PreTranslator
│       ├── include_labels.json     # метки {% include %} блоков
│       ├── note_titles.json        # заголовки {% note %} блоков
│       ├── section_headings.json   # заголовки разделов
│       └── static_terms.json       # термины с нестабильным переводом
├── src/
│   ├── pipeline.py             # оркестрация пайплайна
│   ├── processors/
│   │   ├── parser.py           # чтение .md файла
│   │   ├── pre_translator.py   # статичные замены до защиты
│   │   ├── code_translator.py  # перевод строк внутри кодблоков
│   │   ├── protector.py        # плейсхолдеры и восстановление
│   │   ├── translator.py       # интеграция с Bitrix GPT
│   │   └── writer.py           # сохранение результата
│   ├── validators/
│   │   └── structure.py        # проверка структуры после перевода
│   └── fixers/                 # автоисправление (в разработке)
├── main.py                     # точка входа, CLI
├── config.py                   # настройки, логирование, промпт
├── .env                        # API ключ
├── .env.example                # шаблон .env
└── .gitignore
```

## Пайплайн

```
Файл → Parser → PreTranslator → CodeTranslator → Protector → Translator → Protector.restore → Validator → Writer
```

## Модули

### `src/processors/parser.py` — MarkdownParser

Читает `.md` файл, проверяет что файл существует и имеет расширение `.md`.

---

### `src/processors/pre_translator.py` — PreTranslator

Выполняет статичные замены **до** того, как Protector скроет текст от LLM.
Работает без обращения к API. Все словари загружаются из `data/pre_translator/*.json`.

**Что заменяет:**

| Что | Пример | Почему статично |
|---|---|---|
| Метки include-блоков | `[Сноска о параметрах]` → `[Note on parameters]` | Определяется по имени файла |
| Заголовки битрикс-нот | `"Развитие метода остановлено"` → `"Method development has been halted"` | Стандартные шаблоны |
| Заголовки разделов | `## Продолжите изучение` → `## Continue learning` | LLM переводит нестабильно |
| Заголовок YFM-таблицы | `Название / тип` → `Name / type` | LLM схлопывал строки |
| `` `тип` `` | → `` `type` `` | Всегда одно и то же |
| `![alt-текст]` | → `![alt text]` | Placeholder без смыслового содержания |
| Термины из `static_terms.json` | `элемент` → `item`, `смарт-процесс` → `SPA` | LLM игнорирует словарь для этих слов |

---

### `src/processors/code_translator.py` — CodeTranslator

Отдельный LLM-вызов **до** Protector. Находит кириллические строковые значения внутри кодблоков, батчит их в один запрос и переводит. Код-блоки после этого защищаются целиком как обычно — структура не страдает.

---

### `src/processors/protector.py` — MarkdownProtector

Защищает элементы которые нельзя переводить — заменяет их на плейсхолдеры `[[PROTECTED_N]]` перед переводом и восстанавливает после.

**Порядок защиты (важен — сначала многострочные блоки, потом инлайн):**

| Приоритет | Что защищаем | Пример |
|---|---|---|
| 1 | Frontmatter | `---\ntitle: ...\n---` |
| 2 | Битрикс-блоки | `{% note %}...{% endnote %}` |
| 3 | Названия полей API | `**TYPE_ID**`, `**CATEGORY_ID**` |
| 4 | Якоря | `{#deal}`, `{#anchor-name}` |
| 5 | Блоки кода | ` ```js\ncode\n``` ` |
| 6 | Лейблы вкладок | `- cURL (OAuth)`, `- JS` внутри `{% list tabs %}` |
| 7 | Картинки | `![alt](url)` |
| 8 | Ссылки | `[текст](url)` |
| 9 | Инлайн-код | `` `crm.deal.get` `` |

---

### `src/processors/translator.py` — Translator

Отправляет текст в Bitrix GPT (LiteLLM-совместимый API) и возвращает перевод.
После получения ответа заменяет NBSP (`\u00a0`) на обычные пробелы.

**Модели:**
- `gpt-oss-120b` — ризонер, выше качество
- `bitrixgpt-5.5` — быстрее

---

### `src/processors/writer.py` — MarkdownWriter

Сохраняет результат в папку `output/` с суффиксом `.en.md`.

---

### `src/validators/structure.py` — StructureValidator

Сравнивает структуру оригинала и перевода после обработки.

**Что проверяет:**

| Проверка | Тип |
|---|---|
| Плейсхолдеры восстановлены | error |
| Количество заголовков `##` | error |
| Количество таблиц `#\|` / `\|#` | error |
| Строки таблиц `\|\|` | error |
| Блоки кода ` ``` ` | error |
| Битрикс-блоки `{% %}` | error |
| Термины из словаря переведены | warning |

Термины словаря проверяются по точным границам слова (`\b`), не по подстроке.
При ошибках файл всё равно сохраняется, в лог пишется предупреждение.

---

## Настройки перевода

- Направление: **RU → EN**
- Промпт: `data/prompt.txt` — редактируется без изменения кода
- Основной словарь: `data/dictionary.json` — попадает в промпт LLM и используется валидатором
- Расширенный словарь: `data/glossary.json` — 903 термина, только для валидатора
- Статичные замены: `data/pre_translator/*.json` — редактируются без изменения кода