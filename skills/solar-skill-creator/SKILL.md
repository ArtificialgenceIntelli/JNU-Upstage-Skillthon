---
name: solar-skill-creator
description: Create a new Upstage Solar-powered agent skill for the JNU Skillthon competition. Use when a student wants to build a skill using the Upstage API — guides through problem definition, then generates SKILL.md, skill code, examples, and README (development plan) in the current repo.
---

# Solar Skill Creator

A skill for creating Upstage Solar-powered agent skills that meet the JNU Skillthon submission requirements.

## About This Skill

Agent skills are modular, self-contained packages that extend an agent's capabilities.
A Skillthon skill is a single, clearly scoped function that:
- Accepts defined inputs and produces defined outputs
- Uses the Upstage Solar API as its core intelligence
- Can later become a module inside a larger IITP 본선 Agent Service

## When to Use

Use this skill when a student wants to:
- Create a new Skillthon submission from scratch
- Understand what to build and how to structure it
- Generate all required files for competition submission

Do NOT use this skill to edit an already-completed skill — use direct file editing instead.

## Skill Creation Process

Follow these steps in order. Skip a step only with a clear reason.

### Step 1: Understand the Skill with Concrete Examples

To create an effective skill, first understand what problem the student wants to solve.

Ask one question at a time:

1. "어떤 라이프스타일 문제를 해결하고 싶으신가요? 구체적인 상황을 예로 들어주세요."
2. "이 스킬을 쓰는 사람은 누구인가요? 그 사람이 어떤 입력을 주고 어떤 결과를 받게 되나요?"
3. "Upstage API 중 어떤 것이 이 문제에 가장 맞을 것 같으신가요?" — If unsure, recommend:
   - 텍스트 생성/분석/질답 → Solar LLM (`solar-pro`)
   - PDF·문서 파싱 → Document Parse
   - 의미 기반 검색/유사도 → Embedding

Conclude when the skill's input, output, and API choice are clear.

### Step 2: Plan the Skill Contents

Analyze the concrete examples to identify reusable resources:

1. Plan `skill/main.py` — the `run(input_data: dict) -> dict` function using Upstage API
2. Plan `examples/` — 2–3 concrete input/output pairs for testing
3. Plan `README.md` sections — map to the 5 evaluation criteria

### Step 3: Initialize the Skill

Run the initialization script to scaffold all required files:

```bash
python skills/solar-skill-creator/scripts/init_skill.py <skill-name>
```

The script creates `<skill-name>/` at the repo root with:
- `SKILL.md` — frontmatter template + instruction sections
- `README.md` — development plan template (6 sections mapped to rubric)
- `skill/__init__.py` and `skill/main.py` — Upstage API boilerplate
- `examples/example_01.md` — input/output example template
- `docs/iteration.md` — improvement history template
- `requirements.txt` — openai + pyyaml + python-dotenv

Skill name rules:
- Lowercase, hyphen-separated only (e.g., `summarize-receipt`, `extract-schedule`)
- Max 64 characters
- Describes the action and domain

### Step 4: Edit the Skill

After scaffolding, fill in the generated files. Write in imperative/infinitive form throughout — not second person.

#### Fill in SKILL.md

Answer these questions to complete SKILL.md:
1. What does this skill do? (1 sentence — becomes `description`)
2. When should an agent use this skill? (trigger conditions — appended to `description`)
3. What are the step-by-step instructions for the skill? (body: ## Instructions)
4. What are example inputs and outputs? (body: ## Examples)

`description` must state both WHAT the skill does AND WHEN to use it. Max 1024 characters.

#### Fill in skill/main.py

Implement the `run()` function:

```python
from openai import OpenAI
import os

_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("UPSTAGE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "UPSTAGE_API_KEY 환경변수가 필요합니다.\n"
                "  export UPSTAGE_API_KEY='your-key'"
            )
        _client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
    return _client

def run(input_data: dict) -> dict:
    # Validate required inputs
    # Call Upstage API
    # Return structured output
```

#### Fill in README.md

The README replaces the 10-page development plan. Each section maps to an evaluation criterion:

| Section | Evaluation Criterion | Points |
|---------|---------------------|:------:|
| 1. 해결하려는 라이프스타일 문제 | 주제 적합성 | 15 |
| 2. 스킬 개요 및 아이디어 | 창의성 | 30 |
| 3. 기술 스택 및 실행 방법 | 구현 완성도 | 25 |
| 4. 개선 과정 (Iteration) | 구현 완성도 | 25 |
| 5. 사용 방법 | 사용자 편의성 | 20 |
| 6. 확장 계획 | 작품 사용 가능성 | 10 |

### Step 5: Validate

Run the validation script before submission:

```bash
python skills/solar-skill-creator/scripts/validate.py <skill-name>
```

Fix all errors before submitting. Warnings are optional improvements.

### Step 6: Iterate

After testing the skill with real inputs:

1. Run `python <skill-name>/skill/main.py` with example inputs
2. Record results in `docs/iteration.md` and the README Iteration table
3. Identify failures or weak outputs
4. Improve `skill/main.py` (prompt, parameters, parsing)
5. Repeat until satisfied — aim for at least 2 iterations

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "SKILL.md description은 간단히 써도 된다" | description이 없으면 Agent가 이 스킬을 언제 쓸지 모른다. WHAT + WHEN 모두 포함해야 한다 |
| "코드는 나중에 채우면 된다" | 실행 결과 없이 제출하면 구현 완성도 0점이다. 반드시 실행해서 결과를 README에 붙여야 한다 |
| "Iteration은 한 번이면 충분하다" | 처음 시도가 최선인 경우는 없다. 최소 2회 개선 후 제출하라 |
| "Upstage API 안 써도 된다" | Skillthon은 Upstage API 사용이 필수다. OpenAI/Claude API만 쓴 제출물은 자격 미달이다 |
| "README를 계획서처럼 거창하게 쓸 필요 없다" | README = 개발계획서다. 평가위원은 README로 점수를 매긴다 |

## Verification

After completing the skill creation process, confirm:

- [ ] `python skills/solar-skill-creator/scripts/validate.py <skill-name>` → ✅ 검증 통과
- [ ] `python <skill-name>/skill/main.py` → 에러 없이 실행 완료
- [ ] README에 실제 실행 결과(출력 로그 또는 스크린샷) 포함
- [ ] `docs/iteration.md`에 최소 2회 개선 기록
- [ ] SKILL.md `name`이 디렉토리 이름과 일치
- [ ] `.env` 파일이 `.gitignore`에 포함 (API 키 노출 방지)
