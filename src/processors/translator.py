import logging
import time

import requests


class Translator:
    def __init__(self, api_key: str, base_url: str, model: str, prompt: str, logger: logging.Logger | None = None):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.prompt = prompt
        self._log = logger or logging.getLogger(__name__)

    _RETRY_DELAYS = [5, 15, 30]

    def translate(self, content: str, system_prompt: str | None = None) -> str:
        if not self.api_key or not self.base_url:
            raise ValueError("API_KEY и BASE_URL должны быть заполнены в .env")

        prompt = system_prompt or self.prompt
        self._log.info(f"  → LLM запрос: {len(content)} симв. в тексте, {len(prompt)} симв. в промпте, модель: {self.model}")

        last_exc: Exception | None = None
        for attempt, delay in enumerate([0] + self._RETRY_DELAYS):
            if delay:
                self._log.warning(f"  Повтор через {delay} сек. (попытка {attempt + 1})...")
                time.sleep(delay)
            try:
                t0 = time.monotonic()
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": content},
                        ],
                    },
                    timeout=90,
                )
                elapsed = time.monotonic() - t0
                response.raise_for_status()
                result = response.json()["choices"][0]["message"]["content"]
                if not result or not result.strip():
                    raise ValueError("API вернул пустой ответ")
                self._log.info(f"  ← LLM ответ: {len(result)} симв., {elapsed:.1f} сек.")
                return result.replace('\u00a0', ' ')
            except requests.HTTPError as e:
                if e.response.status_code < 500:
                    raise
                last_exc = e
                self._log.warning(f"  HTTP {e.response.status_code}: {e}")
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exc = e
                self._log.warning(f"  Сетевая ошибка: {e}")

        raise RuntimeError(f"LLM недоступен после {len(self._RETRY_DELAYS) + 1} попыток") from last_exc