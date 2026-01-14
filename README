# AI Career-to-Project Orchestrator (MVP, 1주일)

**옵션 A: 사용자가 JD 텍스트를 붙여넣는 방식**으로 시작하는, **Resume ↔ JD 갭 분석 → 이력서 bullet 개선 → 갭을 메우는 프로젝트 아이디어/설계/1주일 플랜 자동 생성** 멀티에이전트 앱.

---

## 0) 목표와 성공 기준

### 목표
- 사용자가 **이력서 텍스트 + JD 텍스트**를 붙여넣으면
  1) **스킬/키워드 갭**을 정량·정성으로 제시하고
  2) **이력서 bullet 개선안**을 만들어주며
  3) 갭을 메우기 위한 **맞춤형 1주일 프로젝트 아이디어 + 아키텍처 + 태스크(일정)**까지 자동 생성한다.

### 성공 기준(데모 기준)
- 입력 2개(Resume/JD)로 **10~30초 내** 결과 생성
- 결과물에 아래가 **반드시 포함**
  - Missing skills/keywords Top N
  - JD 매칭 점수(간단한 규칙 기반 + LLM 보정)
  - 개선된 Resume bullet 5~10개
  - 맞춤 프로젝트 2안(각각: 가치/기술스택/아키텍처/1주일 일정)
- README에 **LangGraph 사용 이유**가 명확히 설명됨(의존관계/분기/재시도/검증 단계)

---

## 1) 사용자 플로우 (Option A)

1. 사용자는 웹 UI에서
   - Resume 텍스트 붙여넣기
   - JD 텍스트 붙여넣기
   - (선택) 목표 직무/레벨, 선호 스택, 제한(비용 0, 1주일, 팀 2명)
2. [Run] 클릭
3. 결과 페이지에서
   - 갭 분석 요약 카드
   - Resume bullet 개선안
   - 프로젝트 아이디어 2안 + 아키텍처 + 일정
   - (선택) JSON/Markdown Export

---

## 2) 시스템 설계 개요

### 핵심 설계 철학
- **LangGraph**로 단계별 의존관계를 고정하고, 각 단계 결과를 **구조화(JSON Schema)**로 통일
- 단계별로 **검증(validator) 노드**를 두어 출력 품질 유지
- 비용/안정성 위해 **RAG 없이도 동작**하도록 시작(추후 확장)

### 구성 요소
- **Frontend**: Next.js (또는 React) — 입력/결과 UI
- **Backend**: FastAPI — /analyze 엔드포인트
- **Orchestrator**: LangGraph — multi-agent workflow
- **Model**: 로컬 LLM 또는 무료/저가 API(개발 시 환경변수로 교체 가능)
- **Storage(선택)**: 로컬 파일(JSON)로 결과 저장(세션 기반)

---

## 3) LangGraph 워크플로우(노드 설계)

> 목적: “분석 → 개선 → 생성”의 파이프라인을 **끊김 없이 연결**하고, 각 단계 산출물을 다음 단계 입력으로 사용.

### 입력 상태(State)
- resume_text: str
- jd_text: str
- preferences: {role, seniority, constraints}

### 노드(Agents)

#### A. Parsing & Normalization
1) **ResumeParserNode**
- 역할: Resume 텍스트에서 섹션/경험/스킬 후보를 구조화
- 출력: ResumeProfile(JSON)

2) **JDParserNode**
- 역할: JD에서 책임/자격요건/우대사항/키워드 후보 추출
- 출력: JDProfile(JSON)

3) **NormalizeKeywordsNode**
- 역할: 동의어/표기 통일(예: CI/CD vs cicd, PostgreSQL vs PostgresSQL)
- 출력: NormalizedProfile

#### B. Gap & Match
4) **SkillGapNode**
- 역할: JD 요구 스킬과 Resume 보유 스킬 비교
- 출력: missing_skills, partial_matches, strong_matches

5) **MatchScoringNode**
- 역할: 규칙 기반 점수(커버리지) + LLM 보정(중요도 가중)
- 출력: score(0-100), rationale

6) **GapValidatorNode**
- 역할: missing_skills가 실제 JD에 존재하는지, 중복/허상 제거
- 출력: validated_missing_skills

#### C. Resume Improvement
7) **BulletRewriteNode**
- 역할: 기존 bullet을 **정직하게** 개선(키워드 삽입은 “가능한 범위”에서)
- 출력: improved_bullets, before_after_pairs

8) **BulletValidatorNode**
- 역할: 과장/허위 뉘앙스 탐지, 너무 긴 문장/모호 표현 제거
- 출력: final_bullets

#### D. Project Generation
9) **ProjectIdeationNode**
- 역할: missing_skills를 “증명 가능한 포트폴리오”로 바꾸는 프로젝트 2안 생성
- 출력: project_ideas[2]

10) **ArchitectureNode**
- 역할: 각 프로젝트의 시스템 구조(서비스/DB/에이전트/실시간 여부) 설계
- 출력: architecture (Mermaid 가능)

11) **SprintPlanNode**
- 역할: 1주일 일정(D1~D7), 태스크/리스크/정의된 산출물
- 출력: weekly_plan

12) **ExportNode**
- 역할: 결과를 UI 표시용 + Markdown/JSON Export

### 분기/재시도(선택)
- GapValidator에서 missing_skills가 너무 많거나(>30) 너무 적으면(<3)
  - NormalizeKeywords를 재호출하거나
  - JDParser를 다시 호출(추출 기준 강화/완화)

---

## 4) 출력 스키마(예시)

### 4.1 GapSummary
```json
{
  "match_score": 78,
  "strong_matches": ["Python", "REST API", "Docker"],
  "missing_skills": ["LangGraph", "Kubernetes", "OAuth 2.0"],
  "recommended_focus": [
    {"skill": "LangGraph", "reason": "JD에서 agent orchestration 요구"},
    {"skill": "Kubernetes", "reason": "배포/운영 역량"}
  ]
}
```

### 4.2 ResumeImprovement
```json
{
  "final_bullets": [
    "Built a FastAPI service integrating ...",
    "Designed a LangGraph workflow to ..."
  ],
  "before_after": [
    {"before": "Worked on API.", "after": "Implemented REST APIs in FastAPI with ..."}
  ]
}
```

### 4.3 ProjectPlan (2안)
```json
{
  "title": "Multi-Agent JD→Project Planner",
  "value": "Turns resume gaps into a shippable portfolio project",
  "tech_stack": ["LangGraph", "LangChain", "FastAPI", "Next.js"],
  "architecture": "mermaid ...",
  "week_plan": {
    "D1": ["repo scaffolding", "schema 정의"],
    "D2": ["parser nodes"],
    "D3": ["gap + scoring"],
    "D4": ["rewrite"],
    "D5": ["project ideation"],
    "D6": ["UI 연결"],
    "D7": ["테스트/README/데모"],
    "deliverables": ["demo video", "README", "sample inputs"],
    "risks": ["LLM hallucination", "keyword normalization"],
    "mitigations": ["validator node", "schema enforcement"]
  }
}
```

---

## 5) 리포지토리 구조(추천)

```
career-orchestrator/
  apps/
    web/                 # Next.js UI
    api/                 # FastAPI
  packages/
    core/                # schemas, utils
    agents/              # prompts, agent nodes
    graph/               # langgraph workflow
  data/
    samples/             # sample resume/jd pairs
  docs/
    architecture.md      # diagrams
  .env.example
  docker-compose.yml     # 선택: 로컬 통합 실행
  README.md
```

### 모듈 책임
- `packages/core`: Pydantic schemas, keyword normalization, scoring utils
- `packages/agents`: 각 Agent 프롬프트 + output parser
- `packages/graph`: LangGraph 정의(노드 연결/분기/재시도)

---

## 6) 1주일 개발 계획(현실적인 컷)

### Day 1 — 제품 스펙 고정 + 스캐폴딩
- repo 생성, FastAPI/Next.js 기본 라우팅
- 입력/출력 스키마(Pydantic) 확정
- LangGraph skeleton(노드 placeholder)

### Day 2 — Parser/Normalizer 완성
- ResumeParser, JDParser 구현
- NormalizeKeywords(동의어/대소문자/표기 통일) 룰 최소 30개

### Day 3 — Gap & Score
- SkillGap + MatchScoring
- GapValidator(중복 제거, JD 근거 문장 링크)

### Day 4 — Bullet Rewrite
- BulletRewrite + Validator
- “정직한 개선” 규칙(허위 금지, 모호 표현 제거)

### Day 5 — Project Ideation
- missing_skills → 프로젝트 2안 생성
- 프로젝트마다 “증명 포인트(what you can demo)” 생성

### Day 6 — Architecture + Week Plan
- Mermaid 아키텍처 생성
- D1~D7 태스크 생성 + deliverables
- UI에서 카드형 결과 렌더링

### Day 7 — Hardening + Storytelling
- 샘플 3세트 넣기(Resume/JD)
- 통합 테스트, edge cases
- README: 문제/해결/아키텍처/데모/GIF

---

## 7) 이력서/링크드인용 문장 템플릿

- **Resume (1줄)**
  - Designed a **LangGraph-based multi-agent workflow** that compares resumes and job descriptions, identifies skill gaps, and generates **tailored portfolio projects and sprint plans**.

- **Resume (성과형)**
  - Automated resume-to-JD alignment by extracting normalized skill taxonomies and producing validated gap reports with structured JSON outputs.

- **LinkedIn (프로젝트 설명)**
  - Multi-agent career assistant that transforms skill gaps into shippable 1-week projects, complete with architecture diagrams and task breakdowns.

---

## 8) MVP 범위(반드시 지키기)

✅ 포함
- Paste Resume / Paste JD
- Gap + Score + Bullet 개선
- 프로젝트 2안 + 아키텍처 + 1주일 플랜
- Export: Markdown

❌ 이번 주 제외(확장 아이템)
- 웹 스크래핑(옵션 B)
- 로그인/계정
- DB 영속화(필요 시 파일 저장만)
- 벡터DB/RAG(추후)

---

## 9) 다음 액션(바로 시작용)

### 지금 당장 해야 할 3가지
1) **스키마 확정**: ResumeProfile / JDProfile / GapSummary / ProjectPlan
2) **LangGraph 노드 목록** 확정(위 12개)
3) 샘플 입력 1세트 만들기(테스트 드리븐)

원하면 다음 메시지에서 바로:
- 스키마(Pydantic) 초안
- LangGraph 코드 뼈대
- 프롬프트 템플릿
을 한 번에 만들어서 개발 시작 상태로 만들어줄게.

