import requests
import os

LLM_URL = os.getenv("LLM_URL", "http://host.docker.internal:1234/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma-3-1b-it")


def call_llm(question: str) -> str:
    body = {
        "model": LLM_MODEL,
        "messages":[
            {"role": "user", "content": question}
        ]
    }         # same dict you used in Postman, with question as the user message
    response = requests.post(LLM_URL, json=body, timeout=60)
    data = response.json()
    return data["choices"][0]["message"]["content"]           # the reply text, found inside data