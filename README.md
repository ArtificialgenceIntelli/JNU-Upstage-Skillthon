# JNU & Upstage Skillthon

> 전남대학교 소프트웨어중심대학 × 업스테이지  
> 2026 교내 디지털 경진대회 (SW부문) — AI Agent를 위한 Skill 개발

## Skillthon이란

하나의 명확한 **Skill**을 만드는 대회입니다.  
만든 Skill은 IITP 본선에서 Agent Service의 핵심 부품(module)이 됩니다.

```
Upstage 교육 (5/8)
    → Skillthon 제출 (5/11~15)
        → IITP 본선 Agent Service 확장
```

## 시작하는 방법

### 1. 이 repo를 Fork

GitHub 우측 상단 **Fork** 버튼 클릭

### 2. fork한 repo를 Claude Code로 열기

```bash
git clone https://github.com/[내-username]/JNU-Upstage-Skillthon
cd JNU-Upstage-Skillthon
claude .
```

### 3. solar-skill-creator 스킬 로드

```bash
claude skills add skills/solar-skill-creator
```

### 4. Upstage API 키 설정

1. [developers.upstage.ai](https://developers.upstage.ai) 에서 가입
2. API 키 발급 시 **Referral Code** 입력 (교육 당일 공유)
3. `.env` 파일 생성:

```bash
cp skills/solar-skill-creator/.env.example .env
# .env 파일에 발급받은 API 키 입력
```

### 5. 스킬 만들기

Claude Code에서 solar-skill-creator가 단계별로 안내합니다.  
완성된 스킬이 repo 루트에 생성됩니다.

### 6. 제출

[Google Form 링크] 에서 팀 정보와 GitHub repo URL 제출

---

## 제출 구성

fork된 repo 안에 다음이 있어야 합니다:

```
JNU-Upstage-Skillthon/ (내 fork)
├── [내-스킬-이름]/
│   ├── SKILL.md          # 스킬 명세
│   ├── README.md         # 개발계획서 (평가 기준 6개 섹션)
│   ├── skill/
│   │   └── main.py       # Upstage API 사용 코드
│   ├── examples/         # 실행 예시
│   └── docs/             # 개선 기록
└── skills/               # 변경하지 마세요
```

제출 전 검증:

```bash
python skills/solar-skill-creator/scripts/validate.py [내-스킬-이름]
```

---

## 평가 기준

| 항목 | 배점 |
|------|:----:|
| 창의성 (Upstage API 활용 독창성, 문제 해결 참신성) | 30 |
| 구현 완성도 (실행 가능, Input/Output 명확, Iteration 기록) | 25 |
| 사용자 편의성 (README 보고 실행 가능, 문서화 품질) | 20 |
| 주제 적합성 (라이프스타일 문제 연계, Agent Module 적합성) | 15 |
| 작품 사용 가능성 (IITP 본선 확장 시나리오) | 10 |

---

## 문의

- 담당: 조아라 연구원 (062-530-5364)
- 이메일: sunan4711@jnu.ac.kr
