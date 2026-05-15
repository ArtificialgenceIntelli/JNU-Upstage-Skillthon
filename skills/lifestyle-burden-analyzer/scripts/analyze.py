#!/usr/bin/env python3
"""
analyze.py — 일정 추출 + 멀티 에이전트 토론 + 조정자 합성
Usage: python analyze.py <file_path_or_text>
  - 인자가 존재하는 파일이면 → Information Extract API로 구조화 추출
  - 인자가 텍스트이면 → Solar LLM 구조화 출력으로 추출
Output: 부담도 분석 리포트를 stdout으로 출력
"""

import sys
import os
import json
import base64
import concurrent.futures
from pathlib import Path

# assets/.env에서 API 키 로드
script_dir = Path(__file__).parent
env_path = script_dir.parent / "assets" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    print("Error: UPSTAGE_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
    sys.exit(1)

from openai import OpenAI

# ── 스키마 ──────────────────────────────────────────────────────────────────

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "description": "문서에 언급된 할 일, 과제, 업무 목록",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "작업명 또는 설명"},
                    "deadline": {"type": "string", "description": "마감일 또는 기한"},
                    "estimated_hours": {"type": "string", "description": "예상 소요 시간"},
                    "importance": {"type": "string", "description": "중요도: high/medium/low"},
                    "category": {"type": "string", "description": "분류: work/study/personal/health/social"},
                },
            },
        },
        "events": {
            "type": "array",
            "description": "고정된 일정, 회의, 수업, 약속",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "이벤트명"},
                    "datetime": {"type": "string", "description": "날짜 및 시간"},
                    "duration": {"type": "string", "description": "소요 시간"},
                    "category": {"type": "string", "description": "분류: class/meeting/appointment/social/exercise"},
                },
            },
        },
        "time_period": {"type": "string", "description": "이 일정이 해당하는 기간"},
        "context_summary": {"type": "string", "description": "스트레스 지표, 개인 제약, 업무 강도 관련 맥락"},
    },
}

SOLAR_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "deadline": {"type": "string"},
                    "estimated_hours": {"type": "string"},
                    "importance": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["name", "deadline", "estimated_hours", "importance", "category"],
                "additionalProperties": False,
            },
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "datetime": {"type": "string"},
                    "duration": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["name", "datetime", "duration", "category"],
                "additionalProperties": False,
            },
        },
        "time_period": {"type": "string"},
        "context_summary": {"type": "string"},
    },
    "required": ["tasks", "events", "time_period", "context_summary"],
    "additionalProperties": False,
}

MIME_MAP = {
    ".pdf": "application/pdf",
    ".hwp": "application/octet-stream",
    ".hwpx": "application/octet-stream",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
}

# ── 전문가 에이전트 페르소나 ────────────────────────────────────────────────

AGENT_PERSONAS = {
    "수면 우선 에이전트": (
        "당신은 수면 과학자이자 인지 성과 전문가입니다.\n"
        "핵심 신념: 7-9시간 수면은 협상 불가능한 기본이며, 수면 부채는 장기적으로 "
        "모든 판단력·창의력·면역력을 망친다. 밤샘 작업은 다음 날 이틀치 손해를 낳는다.\n\n"
        "주어진 일정을 수면 관점에서 분석하고, 다음을 한국어로 작성하세요:\n"
        "1. 현재 일정이 수면에 미치는 위험 (2문장)\n"
        "2. 수면을 지키면서 일정을 소화하는 구체적 방법 (2-3가지, 요일/시간 포함)"
    ),
    "업무 우선 에이전트": (
        "당신은 결과 중심의 성과 코치입니다.\n"
        "핵심 신념: 마감 달성과 단기 집중이 최우선이다. 중요한 시기에는 일시적으로 "
        "개인 시간을 희생하는 것도 올바른 전략이며, 성과가 쌓이면 여유가 생긴다.\n\n"
        "주어진 일정을 업무 성과 관점에서 분석하고, 다음을 한국어로 작성하세요:\n"
        "1. 가장 중요한 마감/성과 위험 요소 (2문장)\n"
        "2. 성과를 극대화하는 구체적 시간 배분 전략 (2-3가지, 요일/시간 포함)"
    ),
    "삶의 균형 에이전트": (
        "당신은 웰빙 상담사이자 번아웃 예방 전문가입니다.\n"
        "핵심 신념: 지속 가능한 삶의 리듬과 사회적 연결이 장기 성공의 열쇠다. "
        "번아웃 한 번이면 몇 달을 잃는다. 지금의 무리는 나중의 붕괴를 낳는다.\n\n"
        "주어진 일정을 워라벨 관점에서 분석하고, 다음을 한국어로 작성하세요:\n"
        "1. 번아웃 위험 신호와 회복 시간 부족 현황 (2문장)\n"
        "2. 균형을 되찾는 구체적 방법 (2-3가지, 요일/시간 포함)"
    ),
    "건강 우선 에이전트": (
        "당신은 스포츠 의학 전문가이자 운동 생리학자입니다.\n"
        "핵심 신념: 신체 건강(운동, 영양, 회복)이 정신 건강과 모든 인지 성과의 기반이다. "
        "운동 없는 공부는 뇌에 산소를 공급하지 않는 것과 같다.\n\n"
        "주어진 일정을 신체 건강 관점에서 분석하고, 다음을 한국어로 작성하세요:\n"
        "1. 현재 일정에서 신체·정신 건강 위험 요소 (2문장)\n"
        "2. 건강을 유지하면서 일정을 소화하는 구체적 방법 (2-3가지, 요일/시간 포함)"
    ),
    "집중 우선 에이전트": (
        "당신은 딥워크 방법론 전문가이자 인지 생산성 연구자입니다.\n"
        "핵심 신념: 방해 없는 깊은 집중 블록만이 진짜 성과를 만든다. "
        "멀티태스킹과 잦은 전환은 모든 것을 겉핥기로 만들고, 진입 장벽이 생겨 시간을 2배 낭비한다.\n\n"
        "주어진 일정을 집중력·딥워크 관점에서 분석하고, 다음을 한국어로 작성하세요:\n"
        "1. 현재 일정에서 집중을 방해하는 구조적 문제 (2문장)\n"
        "2. 딥워크 블록을 확보하는 구체적 방법 (2-3가지, 요일/시간 포함)"
    ),
}

# ── 조정자 프롬프트 ──────────────────────────────────────────────────────────

MODERATOR_PROMPT = """당신은 공정한 조정자이자 라이프스타일 설계 전문가입니다.
5명의 전문가(수면·업무·삶의균형·건강·집중)가 사용자의 일정에 대해 각자의 가치관으로 의견을 제출했습니다.

당신의 역할:
1. 각 전문가 의견에서 가장 설득력 있는 핵심을 파악한다
2. 공통으로 지적된 위험과 핵심 갈등 지점을 식별한다
3. 생활 패턴별 부담도를 종합 평가한다 (0-100점, 높을수록 부담)
4. 모든 관점을 절충한 균형 잡힌 최종 계획을 제시한다

항상 한국어로 답변하세요. 다음 형식을 정확히 따르세요:

---

현재 [업무/학업/개인] 작업 밀도가 [높음/보통/낮음]입니다.

특히 [구체적인 시간대나 요일]에 [작업 유형] 작업이 집중되어 있으며,
[일정에서 드러나는 구조적 문제 1-2가지].

## 전문가 토론 요약

**수면 우선**: [핵심 주장 1문장]
**업무 우선**: [핵심 주장 1문장]
**삶의 균형**: [핵심 주장 1문장]
**건강 우선**: [핵심 주장 1문장]
**집중 우선**: [핵심 주장 1문장]

공통 우려: [전문가들이 공통으로 지적한 점]
핵심 갈등: [전문가들 간 가장 큰 의견 차이]

## 생활 패턴별 시뮬레이션

### 수면 우선형
| 지표 | 점수 | 해석 |
|---|---|---|
| 생산성 저하 | XX/100 | 한 줄 설명 |
| 시간 압박 | XX/100 | 한 줄 설명 |
| 인지 부하 | XX/100 | 한 줄 설명 |
| 피로도 | XX/100 | 한 줄 설명 |

### 업무 우선형
| 지표 | 점수 | 해석 |
|---|---|---|
| 생산성 저하 | XX/100 | 한 줄 설명 |
| 시간 압박 | XX/100 | 한 줄 설명 |
| 인지 부하 | XX/100 | 한 줄 설명 |
| 피로도 | XX/100 | 한 줄 설명 |

### 운동 균형형
| 지표 | 점수 | 해석 |
|---|---|---|
| 생산성 저하 | XX/100 | 한 줄 설명 |
| 시간 압박 | XX/100 | 한 줄 설명 |
| 인지 부하 | XX/100 | 한 줄 설명 |
| 피로도 | XX/100 | 한 줄 설명 |

### 워라벨 중심형
| 지표 | 점수 | 해석 |
|---|---|---|
| 생산성 저하 | XX/100 | 한 줄 설명 |
| 시간 압박 | XX/100 | 한 줄 설명 |
| 인지 부하 | XX/100 | 한 줄 설명 |
| 피로도 | XX/100 | 한 줄 설명 |

## 조정자 결론

[전문가들의 토론을 반영해 어떤 가치관들을 절충했는지 설명하는 2-3문장]

추천:
- [구체적인 요일/시간대 포함 행동 1]
- [구체적인 요일/시간대 포함 행동 2]
- [구체적인 요일/시간대 포함 행동 3]"""


# ── API 호출 함수 ────────────────────────────────────────────────────────────

def _make_client(base_url: str = "https://api.upstage.ai/v1") -> OpenAI:
    return OpenAI(api_key=UPSTAGE_API_KEY, base_url=base_url)


def extract_from_file(file_path: str) -> dict:
    """Information Extract API로 파일에서 직접 구조화된 일정 추출."""
    ext = Path(file_path).suffix.lower()
    mime = MIME_MAP.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    client = _make_client("https://api.upstage.ai/v1/information-extraction")
    resp = client.chat.completions.create(
        model="information-extract",
        messages=[{
            "role": "user",
            "content": [{"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}],
        }],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "schedule_extraction", "schema": EXTRACT_SCHEMA},
        },
    )
    return json.loads(resp.choices[0].message.content)


def extract_from_text(text: str) -> dict:
    """Solar LLM 구조화 출력으로 텍스트에서 일정 추출."""
    client = _make_client()
    resp = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": "한국어 텍스트에서 일정, 할 일, 이벤트를 추출하는 전문가입니다. 언급되지 않은 필드는 빈 문자열로 채우세요."},
            {"role": "user", "content": f"다음 텍스트에서 일정과 작업 정보를 추출해주세요:\n\n{text}"},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "schedule_extraction", "strict": True, "schema": SOLAR_SCHEMA},
        },
    )
    return json.loads(resp.choices[0].message.content)


def get_specialist_opinion(agent_name: str, persona: str, schedule_data: dict, original_text: str) -> tuple:
    """전문가 에이전트 한 명의 의견을 Solar LLM으로 가져온다."""
    client = _make_client()
    resp = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": (
                f"일정 데이터:\n{json.dumps(schedule_data, ensure_ascii=False, indent=2)}\n\n"
                f"원본 텍스트 (추가 맥락):\n{original_text[:1500]}"
            )},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return agent_name, resp.choices[0].message.content


def debate_and_moderate(schedule_data: dict, original_text: str) -> str:
    """5개 전문가 에이전트를 병렬 호출하고, 조정자 에이전트가 절충안을 합성한다."""

    # 1단계: 전문가 에이전트 병렬 호출
    print("[멀티 에이전트 토론 시작 — 5명 병렬 호출 중...]", file=sys.stderr)
    opinions: dict[str, str] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(get_specialist_opinion, name, persona, schedule_data, original_text): name
            for name, persona in AGENT_PERSONAS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            name, opinion = future.result()
            opinions[name] = opinion
            print(f"  ✓ {name} 의견 수집", file=sys.stderr)

    # 2단계: 조정자 에이전트 합성 (reasoning_effort=medium)
    print("[조정자 에이전트: 절충안 합성 중...]", file=sys.stderr)
    opinions_block = "\n\n".join(
        f"### {name}\n{opinion}" for name, opinion in opinions.items()
    )

    client = _make_client()
    resp = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": MODERATOR_PROMPT},
            {"role": "user", "content": (
                f"## 일정 데이터\n{json.dumps(schedule_data, ensure_ascii=False, indent=2)}\n\n"
                f"## 전문가 의견\n{opinions_block}"
            )},
        ],
        reasoning_effort="medium",
        max_tokens=2500,
    )
    return resp.choices[0].message.content


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <file_path_or_text>", file=sys.stderr)
        sys.exit(1)

    input_arg = " ".join(sys.argv[1:])

    if Path(input_arg).is_file():
        print(f"[Information Extract: {input_arg}]", file=sys.stderr)
        schedule_data = extract_from_file(input_arg)
        original_text = f"[파일 입력: {input_arg}]"
    else:
        print("[Solar LLM: 텍스트에서 일정 추출 중...]", file=sys.stderr)
        original_text = input_arg
        schedule_data = extract_from_text(input_arg)

    print("\n[추출된 일정]", file=sys.stderr)
    print(json.dumps(schedule_data, ensure_ascii=False, indent=2), file=sys.stderr)

    report = debate_and_moderate(schedule_data, original_text)
    print(report)


if __name__ == "__main__":
    main()
