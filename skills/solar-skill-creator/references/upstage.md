# Upstage Solar API Reference

Source: https://console.upstage.ai/docs

## Authentication & Base URL

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1"
)
```

Required env var: `UPSTAGE_API_KEY`
Copy `assets/.env.example` to `.env` and fill in the key.

---

## 1. Chat (Solar LLM)

**Endpoint:** `POST https://api.upstage.ai/v1/chat/completions`

### Available Models (use aliases — they auto-update)

| Alias | Description | RPM / TPM |
|-------|-------------|-----------|
| `solar-pro3` | Most capable, 102B MoE | 100 / 50,000 |
| `solar-pro2` | Balanced performance | 100 / 50,000 |
| `solar-mini` | Fast, lightweight | 100 / 50,000 |
| `syn-pro` | Synthesis specialist | 100 / 50,000 |

### Single-turn

```python
response = client.chat.completions.create(
    model="solar-pro3",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

### Multi-turn (Stateless Pattern)

```python
def run(input_data: dict) -> dict:
    messages = input_data.get("messages", [])
    user_text = input_data["text"]
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="solar-pro3",
        messages=messages
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return {"reply": reply, "messages": messages}
```

### System Prompt Pattern (recommended for skills)

```python
response = client.chat.completions.create(
    model="solar-pro3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that..."},
        {"role": "user", "content": user_input}
    ]
)
```

### Streaming

```python
stream = client.chat.completions.create(
    model="solar-pro3",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## 2. Embeddings

**Endpoint:** `POST https://api.upstage.ai/v1/embeddings`

### Available Models

| Alias | Use case | RPM / TPM |
|-------|----------|-----------|
| `embedding-query` | For search queries | 100 / 300,000 |
| `embedding-passage` | For documents/passages | 100 / 300,000 |

> Use `embedding-query` for the search query, `embedding-passage` for the corpus.

### Single text

```python
response = client.embeddings.create(
    model="embedding-query",
    input="What is the weather today?"
)
vector = response.data[0].embedding  # list[float], normalized
```

### Batch (up to 100 texts, 204,800 tokens)

```python
passages = ["Text one", "Text two", "Text three"]
result = client.embeddings.create(
    model="embedding-passage",
    input=passages
)
vectors = [d.embedding for d in result.data]
```

### Cosine Similarity (dot product on normalized vectors)

```python
import numpy as np

def most_similar(query: str, passages: list[str]) -> str:
    q_vec = client.embeddings.create(
        model="embedding-query", input=query
    ).data[0].embedding
    p_vecs = [
        d.embedding for d in client.embeddings.create(
            model="embedding-passage", input=passages
        ).data
    ]
    scores = [np.dot(q_vec, p) for p in p_vecs]
    return passages[int(np.argmax(scores))]
```

---

## 3. Document Parsing

**Endpoint:** `POST https://api.upstage.ai/v1/document-ai/document-parse`

```python
import requests

def parse_document(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.upstage.ai/v1/document-ai/document-parse",
            headers={"Authorization": f"Bearer {os.environ['UPSTAGE_API_KEY']}"},
            files={"document": f},
            data={"output_formats": '["text", "html", "markdown"]'}
        )
    return response.json()
```

Supported formats: PDF, PNG, JPG, TIFF, BMP, DOCX, PPTX, XLSX

---

## Skill `run()` Boilerplate

```python
from openai import OpenAI
import os

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("UPSTAGE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.\n"
                "  cp assets/.env.example .env  # 그 후 키 입력"
            )
        _client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
    return _client


def run(input_data: dict) -> dict:
    """
    Args:
        input_data: {"text": str, ...}
    Returns:
        {"result": str, ...}
    """
    client = _get_client()
    text = input_data.get("text", "")
    if not text:
        raise ValueError("input_data['text'] is required")

    response = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return {"result": response.choices[0].message.content}
```
