# AI Career-to-Project Orchestrator

> 변경사항 반영: **Agent 2개만**(Resume 분석/점수 Agent, Project 설계 Agent) + 나머지는 **Agent Tool(함수)**로 구현. **레주메 문장/불릿 개선은 범위에서 제외**. 최종 목표는 **원하는 직업(JD)에 맞는 레주메를 만들기 위한 “프로젝트 구성안”을 생성**하는 것.

---

## 0) 최종 목표 & 성공 기준

### 최종 목표
- 사용자가 **Resume 텍스트 + JD 텍스트**를 붙여넣으면
  1) JD 대비 **현재 레주메의 매칭 점수/커버리지**를 보여주고
  2) JD 기준 **부족한 키워드(Validated Missing Keywords)**를 뽑은 뒤
  3) 그 키워드를 **“증명 가능한 포트폴리오 프로젝트”**로 채울 수 있는
     - 프로젝트 2안
     - 시스템 구조(아키텍처)
     - 1주일 실행 계획(D1~D7)
    을 생성한다.

### 성공 기준(데모 기준)
- 입력 2개(Resume/JD)로 **10~30초 내** 결과 생성
- 결과물에 아래가 반드시 포함
  - JD 매칭 점수(0~100) + 간단 근거
  - Validated Missing Keywords Top N (예: 10~20개)
  - 프로젝트 2안(각각: 가치/기술스택/아키텍처/1주일 플랜)
  - Export: Markdown (선택)

---

## 1) 사용자 플로우 (Option A: JD 붙여넣기)

1. 사용자는 웹 UI에서
   - Resume 텍스트 붙여넣기
   - JD 텍스트 붙여넣기
   - (선택) 제약: 비용 0, 1주일, 팀 2명, 선호 스택(React/FastAPI 등)
2. [Run] 클릭
3. 결과 페이지에서
   - 매칭 점수 / 커버리지 요약
   - 부족한 키워드 리스트(Validated)
   - 추천 프로젝트 2안 + 아키텍처 + 1주일 플랜
   - (선택) Markdown/JSON Export

---

## 2) 아키텍처 개요 (2 Agents + Tools)

### 핵심 철학
- **LLM 판단/생성은 2개의 Agent**만 담당
- 나머지는 반복/검증/형식 변환/규칙 비교 → **Tool(함수)로 분리**
- LangGraph는 **Agent 간 오케스트레이션 + 재시도 분기**만 담당

### 구성 요소
- Frontend: Next.js (또는 React)
- Backend: FastAPI — /run 엔드포인트
- Orchestrator: LangGraph — (ResumeAgent → ProjectAgent)
- Tools: 파싱/정규화/비교/검증/스코어링/익스포트

---

## 3) LangGraph 워크플로우(v2)

### 입력 State
- resume_text: str
- jd_text: str
- preferences: {role, seniority, constraints, stack_preference}

### 그래프 노드(단 2개)
1) **ResumeAnalysisAgentNode**
- 목적: Resume/JD를 분석하고 **점수 + 부족 키워드(Validated)**를 만든다.

2) **ProjectPlannerAgentNode**
- 목적: Validated Missing Keywords를 기반으로 **프로젝트 2안 + 아키텍처 + 1주일 플랜**을 생성한다.

3) (선택) **ExportToolNode**
- 목적: 결과를 Markdown/JSON으로 변환

---

## 4) Agent 내부 구성: “Agent Tools” 목록

> 아래 Tool들은 LangGraph 노드가 아니라, **각 Agent가 호출하는 함수/유틸**이다.

### 4.1 ResumeAnalysisAgent가 호출하는 Tools
- `jd_parse_tool(jd_text) -> JDProfile`
- `resume_parse_tool(resume_text) -> ResumeProfile`
- `normalize_keywords_tool(resume: ResumeProfile, jd: JDProfile) -> ResumeProfile`
  - **JDProfile 기준으로 ResumeProfile을 정규화**하여 반환(동의어/표기 통일)
- `extract_jd_skill_sets_tool(jd: JDProfile) -> {required, preferred, all, weights}`
- `extract_resume_skill_set_tool(resume: ResumeProfile) -> set[str]`
- `gap_compute_tool(jd_sets, resume_set) -> GapSummary`
  - strong/partial/missing + validated_missing_keywords 포함
- `score_tool(jd_sets, gap) -> (match_score, rationale)`
- (선택) `gap_sanity_check_tool(gap, jd_profile)`

> **주의**: v2에서는 Resume bullet rewrite 관련 tool/스키마는 제외.

### 4.2 ProjectPlannerAgent가 호출하는 Tools
- `project_ideation_tool(missing_keywords, role, constraints) -> 2 ideas`
- `architecture_tool(ideas, stack_preference) -> architecture(+mermaid)`
- `sprint_plan_tool(ideas, constraints) -> D1~D7 plan`

### 4.3 공용 Tools
- `export_markdown_tool(final_result) -> markdown`

---

## 5) 스키마(v2) — 최소만 유지

### 유지
- `resume.py`: ResumeProfile
- `jd.py`: JDProfile
- `gap.py`: GapSummary (match_score, strong/partial, missing_keywords, validated_missing_keywords, notes)
- `project.py`: ProjectOutput (project_ideas[2], architecture, weekly_plan)

### 제거/범위 제외
- `bullet_rewrite.py`: v2에서는 사용하지 않음(레주메 자체 개선은 목표 아님)

---

## 6) Gap 비교 방식(v2)

1) **JDProfile에서 키워드 세트 구성**
- required/preferred/all sets + weights

2) **ResumeProfile에서 skill set 구성**
- resume.skills 중심(추후 bullets에서 추가 추출 가능)

3) **정규화**
- NormalizeKeywordsTool이 JD 기준 용어로 resume를 통일

4) **set 비교로 strong/partial/missing 산출**
- strong = intersection
- missing = JD(required 중심) - resume
- partial = (선택) fuzzy/alias 매칭

5) **validated_missing_keywords**
- JD raw_text/keywords에 실제 존재하는지 검증
- 중복/너무 일반적인 단어 제거

6) **점수 계산**
- req coverage + pref coverage
- 예: 100 * (0.7 * req_cov + 0.3 * pref_cov)

---

## 7) 리포지토리 구조(v2 추천)

```
career-orchestrator/
  apps/
    web/                   # Next.js UI
    api/                   # FastAPI
  packages/
    core/
      schemas/             # resume.py, jd.py, gap.py, project.py
      utils/               # normalization, scoring, text utils
    tools/                 # agent tools(파싱/정규화/갭/점수/익스포트)
    agents/                # resume_agent.py, project_agent.py (tool-calling)
    graph/                 # workflow.py (2 nodes)
  data/
    samples/
  docs/
    architecture.md
  .env.example
  README.md
```

### 파일 책임(핵심만)
- `packages/agents/resume_agent.py`: ResumeAnalysisAgent (tools 호출 + 결과 스키마로 정리)
- `packages/agents/project_agent.py`: ProjectPlannerAgent (tools 호출 + 프로젝트 2안/플랜 생성)
- `packages/tools/*.py`: 파싱/정규화/갭/스코어 등 순수 함수
- `packages/graph/workflow.py`: LangGraph에서 2개의 agent 노드를 연결 + 재시도 분기

---

## 8) 1주일 개발 계획(v2)

### Day 1 — 스키마 확정 + API/Graph 뼈대
- schemas(resume/jd/gap/project)
- FastAPI `/run`
- LangGraph: ResumeAgentNode → ProjectAgentNode

### Day 2 — Tools: 파싱 + 정규화
- jd_parse_tool, resume_parse_tool (LLM JSON 추출 or 룰 기반)
- normalize_keywords_tool (사전+치환+중복 제거)

### Day 3 — Tools: gap + score + validation
- extract sets
- gap_compute_tool + validated_missing
- score_tool

### Day 4 — ProjectPlannerAgent + 아이디어 생성
- project_ideation_tool (2안 고정)

### Day 5 — architecture + sprint plan
- architecture_tool (mermaid 선택)
- sprint_plan_tool (D1~D7 + deliverables/risks)

### Day 6 — Web UI 연결
- paste inputs, 결과 카드 렌더
- export 버튼(선택)

### Day 7 — 데모/README/샘플
- sample 3세트
- 통합 테스트
- README: 문제/해결/아키텍처/데모

---

## 9) 출력 예시(v2)

### AnalysisResult
```json
{
  "match_score": 78,
  "strong_matches": ["Python", "REST API"],
  "partial_matches": ["CI/CD"],
  "missing_keywords": ["Kubernetes", "OAuth 2.0", "LangGraph"],
  "validated_missing_keywords": ["Kubernetes", "OAuth 2.0", "LangGraph"],
  "notes": "Required coverage 0.75, preferred coverage 0.50"
}
```

### ProjectOutput (2안)
```json
{
  "project_ideas": [
    {"title": "...", "architecture": "...", "weekly_plan": "..."},
    {"title": "...", "architecture": "...", "weekly_plan": "..."}
  ]
}
```

---

## 10) 범위 체크(v2)

✅ 포함
- Resume/JD 붙여넣기
- 점수 + 부족 키워드(Validated)
- 부족 키워드 기반 프로젝트 2안 + 구조 + 1주일 플랜

❌ 제외
- Resume bullet 개선/리라이트
- 웹 스크래핑
- 로그인/DB 영속화

