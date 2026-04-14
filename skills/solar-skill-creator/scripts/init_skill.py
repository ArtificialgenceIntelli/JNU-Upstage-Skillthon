"""
solar-skill-creator: Skill initializer
Scaffolds a new Upstage Solar skill directory at the repo root.

Usage:
    python skills/solar-skill-creator/scripts/init_skill.py <skill-name>

Example:
    python skills/solar-skill-creator/scripts/init_skill.py summarize-receipt
"""
import re
import sys
from pathlib import Path


def validate_name(name: str) -> str | None:
    """Return error string if name is invalid, else None."""
    if not name:
        return "스킬 이름을 입력해주세요."
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return (
            f"스킬 이름이 잘못되었습니다: '{name}'\n"
            "  소문자, 숫자, 하이픈만 사용 가능합니다 (예: summarize-receipt)"
        )
    if len(name) > 64:
        return f"스킬 이름이 64자를 초과합니다 ({len(name)}자)"
    return None


SKILL_MD = """\
---
name: {name}
description: >
  TODO: 이 스킬이 무엇을 하는지 한 문장으로 설명하세요.
  TODO: 어떤 Agent가 언제 이 스킬을 사용하면 좋은지 한 문장으로 추가하세요.
  (최대 1024자, WHAT + WHEN 모두 포함)
---

# {title}

## 해결하는 문제

TODO: 어떤 라이프스타일 문제를 해결하는가 — 1~3문장

## Instructions

Agent가 이 스킬을 실행할 때 따를 단계:

1. TODO: 첫 번째 단계
2. TODO: 두 번째 단계
3. Upstage API(`UPSTAGE_API_KEY`)를 사용하여 TODO: 어떤 작업을 수행한다
4. 결과를 TODO: 어떤 형식으로 반환한다

## Input / Output

**Input:**

| 파라미터 | 타입 | 설명 | 필수 |
|---------|------|------|:----:|
| `param1` | string | TODO: 설명 | ✓ |

**Output:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `result` | string | TODO: 설명 |

## Examples

### 예시 1

**Input:**
```json
{{
  "param1": "TODO: 예시 입력값"
}}
```

**Output:**
```json
{{
  "result": "TODO: 예시 출력값"
}}
```
"""

MAIN_PY = """\
\"\"\"
Skill: {name}
Description: TODO: 스킬 설명
Upstage API: TODO: Solar LLM / Document Parse / Embedding 중 선택

Upstage API Docs: https://developers.upstage.ai
\"\"\"
import os
from openai import OpenAI

_client = None


def _get_client() -> OpenAI:
    \"\"\"API 키를 확인하고 클라이언트를 반환합니다 (지연 초기화).\"\"\"
    global _client
    if _client is None:
        api_key = os.environ.get("UPSTAGE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.\\n"
                "  export UPSTAGE_API_KEY='your-key'  후 다시 실행하세요.\\n"
                "  API 키 발급: https://developers.upstage.ai"
            )
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1",
        )
    return _client


def run(input_data: dict) -> dict:
    \"\"\"
    스킬 실행 함수.

    Args:
        input_data: {{
            "param1": str,  # TODO: 설명 (필수)
        }}

    Returns:
        {{
            "result": str,    # TODO: 설명
            "metadata": dict, # 부가 정보
        }}
    \"\"\"
    param1 = input_data.get("param1", "")
    if not param1:
        raise ValueError("'param1'은 필수 입력값입니다.")

    client = _get_client()

    # TODO: Upstage API 호출 구현
    # Solar LLM 예시:
    response = client.chat.completions.create(
        model="solar-pro",
        messages=[
            {{"role": "system", "content": "TODO: 시스템 프롬프트를 작성하세요."}},
            {{"role": "user", "content": param1}},
        ],
    )

    result_text = response.choices[0].message.content

    return {{
        "result": result_text,
        "metadata": {{
            "model": response.model,
            "usage": {{
                "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                "completion_tokens": response.usage.completion_tokens if response.usage else None,
            }},
        }},
    }}


if __name__ == "__main__":
    # 예시 실행 후 결과를 README의 '실행 결과 예시' 섹션에 붙여넣으세요
    example_input = {{
        "param1": "TODO: 테스트 입력값",
    }}

    print("=== 입력 ===")
    print(example_input)
    print("\\n=== 출력 ===")
    result = run(example_input)
    print(result)
"""

README_MD = """\
# {title}

> **팀명**: TODO: 팀명
> **Upstage API**: TODO: Solar LLM / Document Parse / Embedding
> **GitHub**: TODO: 이 repo URL

---

## 1. 해결하려는 라이프스타일 문제

> 평가 항목: 주제 적합성 (15점)

### 문제 정의

TODO: 해결하고자 하는 라이프스타일 문제를 구체적으로 설명하세요.

### 기존 해결 방법과 한계

TODO: 현재 존재하는 해결책과 그 한계를 분석하세요.

### 해결 필요성 및 기대효과

TODO: 왜 이 문제가 해결되어야 하는지, 이 스킬로 무엇이 달라지는지 설명하세요.

---

## 2. 스킬 개요 및 아이디어

> 평가 항목: 창의성 (30점)

### 스킬 핵심 기능

TODO: 한 문장으로 이 스킬이 하는 것

- **Input**: TODO: 무엇을 받는가
- **Output**: TODO: 무엇을 돌려주는가

### Upstage API 활용 방식

TODO: Solar LLM / Document Parse / Embedding 중 어떤 것을, 어떻게 활용하는지 설명하세요.

### 기존 방식 대비 차별점

TODO: Upstage API를 활용함으로써 무엇이 달라지는가.

---

## 3. 기술 스택 및 실행 방법

> 평가 항목: 구현 완성도 (25점)

### 기술 스택

- **AI API**: Upstage TODO: Solar / Document Parse / ...
- **언어**: Python TODO: 버전
- **주요 라이브러리**: TODO: 목록

### 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API 키 설정
cp ../../skills/solar-skill-creator/.env.example .env
# .env 파일에 UPSTAGE_API_KEY 입력

# 3. 실행
python skill/main.py
```

### 실행 결과 예시

```
TODO: python skill/main.py 실행 후 실제 출력을 여기에 붙여넣으세요
```

---

## 4. 개선 과정 (Iteration)

> 평가 항목: 구현 완성도 (25점)

| 회차 | 시도한 것 | 결과 / 문제점 | 다음 개선 방향 |
|:----:|----------|--------------|--------------|
| 1 | 초기 구현 | TODO | TODO |
| 2 | TODO | TODO | TODO |

---

## 5. 사용 방법

> 평가 항목: 사용자 편의성 (20점)

### 다른 개발자가 이 스킬을 사용하는 방법

```python
from skill.main import run

result = run({{
    "param1": "TODO: 입력값"
}})
print(result)
```

---

## 6. 확장 계획 — 어떤 Agent의 부품이 되는가

> 평가 항목: 작품 사용 가능성 (10점)

### 이 스킬이 통합될 Agent 시나리오

TODO: 이 Skill이 어떤 라이프스타일 Agent Service의 핵심 부품이 될 수 있는지 구체적으로 설명하세요.

```
[사용자 입력] → [이 Skill: {name}] → [다른 Skill] → [Agent 응답]
```

### IITP 본선 확장 방향

TODO: 교내 예선 이후 IITP 본선에서 이 Skill을 어떤 Agent Service로 발전시킬 것인가.

---

## 팀 정보

| 이름 | 학과 | 학번 | 학년 | 역할 |
|------|------|------|:----:|------|
| | | | | |
| | | | | |
| | | | | |

지도교수: TODO: 성명 / TODO: 소속 학과
"""

EXAMPLE_MD = """\
# 예시 1: TODO 예시 이름

## 입력

```json
{{
  "param1": "TODO: 예시 입력값"
}}
```

## 출력

```json
{{
  "result": "TODO: 예시 출력값",
  "metadata": {{
    "model": "solar-pro"
  }}
}}
```

## 설명

TODO: 이 예시가 어떤 상황을 시연하는지 설명하세요.
"""

ITERATION_MD = """\
# Iteration 기록

개선 과정을 날짜와 함께 기록하세요.
README Iteration 표의 상세 버전입니다.

---

## Iteration 1 — TODO: 날짜

### 시도한 것
TODO: 무엇을 구현했는가

### 결과
TODO: 어떻게 동작했는가, 어떤 문제가 있었는가

### 배운 것
TODO: 이 시도에서 무엇을 알게 되었는가

---

## Iteration 2 — TODO: 날짜

### 시도한 것

### 결과

### 배운 것
"""

REQUIREMENTS_TXT = """\
openai>=1.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
"""


def create_skill(name: str, repo_root: Path) -> None:
    title = name.replace("-", " ").title()
    skill_dir = repo_root / name

    if skill_dir.exists():
        print(f"오류: '{skill_dir}' 디렉토리가 이미 존재합니다.")
        sys.exit(1)

    files = {
        "SKILL.md": SKILL_MD.format(name=name, title=title),
        "README.md": README_MD.format(name=name, title=title),
        "skill/__init__.py": "from .main import run\n\n__all__ = ['run']\n",
        "skill/main.py": MAIN_PY.format(name=name),
        "examples/example_01.md": EXAMPLE_MD,
        "docs/iteration.md": ITERATION_MD,
        "requirements.txt": REQUIREMENTS_TXT,
    }

    for rel_path, content in files.items():
        target = skill_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  생성: {name}/{rel_path}")

    print(f"\n✅ '{name}' 스킬 디렉토리가 생성되었습니다.")
    print(f"\n다음 단계:")
    print(f"  1. {name}/SKILL.md  — 스킬 명세 작성 (TODO 항목 채우기)")
    print(f"  2. {name}/skill/main.py — Upstage API 구현")
    print(f"  3. python {name}/skill/main.py — 실행 테스트")
    print(f"  4. {name}/README.md — 개발계획서 작성")
    print(f"  5. python skills/solar-skill-creator/scripts/validate.py {name} — 제출 검증")


def main():
    if len(sys.argv) < 2:
        print("사용법: python skills/solar-skill-creator/scripts/init_skill.py <skill-name>")
        print("예시:   python skills/solar-skill-creator/scripts/init_skill.py summarize-receipt")
        sys.exit(1)

    name = sys.argv[1].strip()
    error = validate_name(name)
    if error:
        print(f"오류: {error}")
        sys.exit(1)

    # Run from repo root
    repo_root = Path(__file__).resolve().parents[3]
    print(f"스킬 초기화 중: {name}")
    print(f"위치: {repo_root / name}\n")
    create_skill(name, repo_root)


if __name__ == "__main__":
    main()
