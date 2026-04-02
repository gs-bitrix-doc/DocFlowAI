import requests


class Translator:
    def __init__(self, api_key: str, base_url: str, model: str, prompt: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.prompt = prompt

    def translate(self, content: str) -> str:
        if not self.api_key or not self.base_url:
            raise ValueError("API_KEY и BASE_URL должны быть заполнены в .env")

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": content},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
