---
name: lifestyle-burden-analyzer
description: Analyze a user's schedule from documents, screenshots, or conversational text to simulate how 4 lifestyle patterns (수면 우선, 업무 우선, 운동 균형, 워라벨 중심형) would handle their commitments, then score future burden on 4 dimensions (생산성 저하, 시간 압박, 인지 부하, 피로도) with a 0-100 score and a one-line explanation each. Use this skill whenever the user asks "뭐부터 해야 할까?", "일정을 어떻게 구성해야 할까?", "이번 주 어떻게 살면 될까?", "요즘 너무 바쁜데", or shares a schedule-related file (PDF, HWP, HWPX) or screenshot. Trigger even if the user doesn't explicitly ask for a simulation — any workload or priority question is an invitation to use this skill.
---

# 라이프스타일 부담도 분석기

사용자의 캡처·문서·대화에서 일정과 작업 맥락을 추출하고, 4가지 생활 패턴으로 시뮬레이션한 뒤 각 패턴의 부담도를 점수와 한 줄 해석으로 제시한다.

## 입력 유형과 처리 방법

| 입력 유형 | 처리 방법 |
|---|---|
| PDF / HWP / HWPX 파일 | `scripts/parse_document.py <파일경로>` 실행 → 텍스트 추출 |
| 이미지 (스크린샷, 캡처) | `scripts/parse_document.py <파일경로>` 실행 (OCR 자동 적용) |
| 대화 복사본 / 직접 입력 텍스트 | 파싱 없이 바로 분석 단계로 |

## 실행 순서

### 1단계: 문서 파싱 (파일 입력 시만)

```bash
python <SKILL_DIR>/scripts/parse_document.py <파일경로>
```

stdout으로 마크다운 텍스트를 받는다. 오류 시 stderr를 확인한다.

### 2단계: 멀티 에이전트 분석

파싱된 텍스트 또는 직접 입력 텍스트를 `scripts/analyze.py`에 넘긴다.

```bash
python <SKILL_DIR>/scripts/analyze.py "<텍스트_또는_파일경로>"
```

스크립트 내부 흐름:
1. 일정 추출 (파일이면 Information Extract, 텍스트면 Solar LLM 구조화 출력)
2. **5개 전문가 에이전트 병렬 호출** — 각자 가치관으로 의견 제출
   - 수면 우선 / 업무 우선 / 삶의 균형 / 건강 우선 / 집중 우선
3. **조정자 에이전트** — 5개 의견 수집 후 공통점·갈등 식별 → 절충안 합성 (`reasoning_effort="medium"`)

### 3단계: 결과 제시

스크립트 출력을 그대로 사용자에게 보여준다. 필요하면 특정 전문가 관점을 더 깊이 설명한다.

## 출력 형식 (참고용)

```
현재 [업무/학업] 작업 밀도가 높습니다.

특히 [요일/시간대]에 [작업 유형]이 집중되어 있으며,
[일정에서 드러나는 구조적 문제].

## 생활 패턴별 시뮬레이션

### 수면 우선형
| 지표 | 점수 | 해석 |
|---|---|---|
| 생산성 저하 | XX/100 | 한 줄 설명 |
...

(업무 우선형 / 운동 균형형 / 워라벨 중심형 동일 형식)

추천:
- [구체적인 요일/시간 포함 행동 1]
- [구체적인 요일/시간 포함 행동 2]
```

## 4가지 생활 패턴 정의

| 패턴 | 특징 |
|---|---|
| 수면 우선형 | 7-9시간 수면 보장, 밤 12시 이후 업무 금지, 낮 시간 집중 |
| 업무 우선형 | 가능한 모든 시간을 업무에 투자, 휴식 최소화, 마감 중심 |
| 운동 균형형 | 하루 1시간 운동 시간 확보, 운동 전후로 업무 배치 |
| 워라벨 중심형 | 오전 9시-오후 6시 업무, 주말 보호, 야근 없음 |

## API 키 설정

`UPSTAGE_API_KEY`가 필요하다. `./assets/.env`에 저장하거나 환경 변수로 설정한다.

의존성 설치:
```bash
pip install openai requests python-dotenv
```
