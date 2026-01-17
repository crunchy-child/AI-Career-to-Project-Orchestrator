# AI Career-to-Project Orchestrator

1. computes a **JD matching score (0–100)** and **validated missing keywords**, then
2. generates **2 portfolio project plans** (architecture + 7-day sprint plan) that help you _prove_ those missing keywords for your target role.

---

## 0) Goals & Success Criteria

### Goals

- Input:
  - `resume_text`, `jd_text` (paste)
  - **`preferences`** (optional): `{ stack_pref, constraints, role }`
- Output:
  - **Match score (0–100)** with rationale
  - **Validated missing keywords**
  - **2 project proposals**, each with:
    - reasoning
    - architecture (Mermaid optional)
    - **7-day plan (D1–D7)**

### Success Criteria (demo-ready)

- End-to-end result in **10–30 seconds**
- Always returns:
  - match score + missing keywords
  - exactly **2** project plans
- Reproducible run with **Docker for API** (web runs locally)

---

## 1) Matching Score Algorithm

We score JD alignment using **keyword-level weighted coverage**.

### 1.1 Base weights (JD category)

- **Required keywords:** base weight = **0.7**
- **Preferred keywords:** base weight = **0.3**

### 1.2 Evidence weights (where the keyword appears in the resume)

For each JD keyword, we assign an evidence multiplier based on where it appears:

| JD category   |                     Found in Resume Experience/Project |                           Found only in Skills section | Not found |
| ------------- | -----------------------------------------------------: | -----------------------------------------------------: | --------: |
| **Required**  | multiplier **1.0** → contribution **0.7 × 1.0 = 0.70** | multiplier **0.6** → contribution **0.7 × 0.6 = 0.42** |   **0.0** |
| **Preferred** | multiplier **0.8** → contribution **0.3 × 0.8 = 0.24** | multiplier **0.3** → contribution **0.3 × 0.3 = 0.09** |   **0.0** |

> Implementation detail: "Experience/Project" means the keyword appears in parsed resume bullets under experience/project sections.

### 1.3 Final score (0–100)

Let `w_i` be the base weight (0.7 or 0.3) and `m_i` be the evidence multiplier for keyword `i`.

- **Weighted covered sum** = `Σ (w_i × m_i)`
- **Max possible sum** = `Σ w_i`
- **Match score** = `100 × (Weighted covered sum / Max possible sum)`

### 1.4 Validated missing keywords

We compute initial missing keywords via set difference, then validate by:

- removing duplicates/alias collisions (normalizing ResumeKeyword based on JDKeyWord)
- ensuring the keyword truly exists in JD text/parsed JD keywords

The result is returned as `validated_missing_keywords`.

---

## 2) System Architecture (2 Agents + Tools)

### Why "multi-agent" here?

We use **two role-specialized agents** with a clear handoff:

1. **Resume Analysis Agent** → computes match score + validated missing keywords (temperature=0)
2. **Project Planner Agent** → generates project blueprints to cover missing keywords (temperature=❤️)

### Orchestration

We use **LangGraph** with `StateGraph` and `MessagesState` to orchestrate the workflow.

```
(resume_text, jd_text, preferences)
   ↓
Resume Analysis Agent (create_react_agent + tools)
   ↓  (validated_missing_keywords + score)
Project Planner Agent 
   ↓
Final Output (JSON + optional Markdown export)
```

### ProjectState (LangGraph State)

```python
class ProjectState(MessagesState):
    # Input
    resume_text: str
    jd_text: str
    # preferences: Optional[Preferences]

    # Resume Analysis Agent outputs
    jd_profile: Optional[JDProfile]
    resume_profile: Optional[ResumeProfile]
    gap_summary: Optional[GapSummary]

    # Project Planner Agent outputs
    project_output: Optional[ProjectOutput]

    # Meta
    error: Optional[list[str]]
    current_step: Optional[str]
```

### Agent Implementation

| Component | Implementation | Description |
|-----------|---------------|-------------|
| **Resume Agent** | `create_react_agent("openai:gpt-4o", tools=[...],)` | ReAct agent with tool calling |
| **JD Parse Tool** | `@tool` + `init_chat_model` + `with_structured_output` | LLM-based structured extraction |
| **Graph** | `StateGraph(ProjectState)` + `START` → `END` | LangGraph workflow |

### Agent tools (functions)

**Resume Analysis Agent tools**

| Tool | Status | Description |
|------|--------|-------------|
| `jd_parse_tool(jd_text) -> JDProfile` | ✅ Implemented | Extract keywords from JD (excludes education/visa requirements) using LLM (model=gpt-4o, temperature=0) |
| `resume_parse_tool(resume_text) -> ResumeProfile` | ⬜ TODO | Extract keywords from resume |
| `normalize_keywords_tool(resume_profile, jd_profile) -> ResumeProfile` | ⬜ TODO | Normalize resume keywords based on JD vocabulary |
| `gap_compute_tool(JDProfile, ResumeProfile) -> GapSummary` | ⬜ TODO | Compute keyword matches and gaps |
| `score_tool(gap_summary) -> GapSummary` | ⬜ TODO | Calculate weighted match score |

**Project Planner Agent tools**

| Tool | Status | Description |
|------|--------|-------------|
| `project_ideation_tool(GapSummary) -> list[ProjectIdea]` | ⬜ TODO | Generate project ideas |
| `architecture_tool(list[ProjectIdea]) -> list[ArchitectureSpec]` | ⬜ TODO | Design architecture |
| `project_plan_tool(...) -> list[ProjectPlan]` | ⬜ TODO | Create 7-day sprint plans |

---

## 3) Data Schemas (v2)

- `resume.py` → `ResumeProfile`
  - `raw_text`
  - `keywords`
  - `normalized`, `normalization_notes`, `normalization_map_applied`
  - `validated_keywords_set`
- `jd.py` → `JDProfile`
  - `raw_text`
  - `keywords` (category: required/preferred/responsibility/other)
  - `role_title`
  - `company`
- `gap.py` → `GapSummary`
  - `match_score`
  - `keyword_matches`
  - `missing_keywords`, `validated_missing_keywords`
  - `notes`
- `project.py` → `ProjectOutput`
  - `project_ideas`
  - `notes`

---

## 4) Repository Structure

```
career-orchestrator/
  apps/
    web/                   # Next.js UI (runs locally)
    api/                   # FastAPI (Dockerized)
  packages/
    core/
      schemas/             
        __init__.py
        resume.py
        jd.py
        gap.py
        project.py
        keyword_base.py
        utils.py
    tools/                 # LangChain tools (@tool decorator)
      jd_parse.py          ✅ Implemented
      resume_parse.py      ⬜ TODO
      keyword_normalize.py ⬜ TODO
      gap_compute.py       ⬜ TODO
      score.py             ⬜ TODO
      project_ideation.py  ⬜ TODO
      architecture.py      ⬜ TODO
      sprint_plan.py       ⬜ TODO
    agents/                # LangGraph agents (create_react_agent)
      resume_agent.py      ✅ Implemented
      project_agent.py     ⬜ TODO
    graph/                 # LangGraph workflow (StateGraph)
      main.py              ✅ Implemented
  data/
    samples/               # sample resume/jd pairs
  docs/
  test_graph.py            ✅ Test script
  pyproject.toml
  .env.example
  docker-compose.yml       # API-only compose
```

---

## 5) Running Locally

### 5.1 Quick Test (Minimal Cycle)

```bash
# 1. Move to project directory
cd career-orchestrator

# 2. Install dependencies
pip install -e .

# 3. Set OpenAI API key (if not already set)
export OPENAI_API_KEY=sk-...

# 4. Run test
python test_graph.py
```

### 5.2 API (Docker)

- Build & run:
  - `docker compose up --build`
- API should expose:
  - `POST /run` (or `/analyze`) – main entry
  - `GET /health` – health check

### 5.3 Web (Local)

- Run Next.js locally and point it to the API base URL.

---

## 6) Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | OpenAI GPT-4o via `init_chat_model("gpt-4o")` |
| **Agent Framework** | LangGraph `create_react_agent` |
| **State Management** | LangGraph `StateGraph` + `MessagesState` |
| **Tool Definition** | LangChain `@tool` + `with_structured_output` |
| **API** | FastAPI |
| **Validation** | Pydantic v2 |

---

## 7) Output Example (short)

```json
{
  "GapSummary": {
    "match_score": 78,
    "keyword_matches": [
      {
        "keyword_pair": [
          {
            "keyword_text": "python",
            "category": "skills",
            "evidence": "Skills section: Python"
          },
          {
            "keyword_text": "python",
            "category": "required",
            "evidence": "JD: Required Python experience",
            "importance": 5
          }
        ],
        "match_type": "partial"
      }
    ],
    "missing_keywords": [
      {
        "keyword_text": "terraform",
        "category": "required",
        "evidence": "JD: Required Infrastructure as Code (Terraform)",
        "importance": 5
      }
    ],
    "validated_missing_keywords": [
      {
        "keyword_text": "terraform",
        "category": "required",
        "evidence": "JD: Required Infrastructure as Code (Terraform)",
        "importance": 5
      }
    ],
    "notes": "필수 키워드는 대부분 충족되었으나 Terraform 경험이 부족합니다."
  },
  "ProjectOutput": {
    "project_ideas": [
      {
        "idea": {
          "title": "Terraform 기반 인프라 자동화",
          "one_liner": "Terraform으로 AWS 인프라를 프로비저닝하고 자동 배포 파이프라인을 구성",
          "reasoning": "JD의 핵심 결손 키워드인 Terraform을 실증할 수 있음",
          "covers_keywords": ["terraform", "ci/cd"],
          "constraints": ["1주일", "1인", "비용 0"],
          "tech_stack": ["Terraform", "GitHub Actions", "AWS"]
        },
        "architecture": {
          "summary": "Terraform으로 인프라 구성 후 CI/CD로 배포 자동화",
          "components": ["Terraform modules", "GitHub Actions", "K8s cluster"],
          "data_flow": "Push -> CI build/test -> Terraform apply -> K8s deploy"
        },
        "weekly_plan": [
          { "day": 1, "goals": ["Terraform 프로젝트 초기화"], "tasks": ["Provider 설정"] },
          { "day": 2, "goals": ["K8s 클러스터 구성"], "tasks": ["클러스터 리소스 정의"] },
          { "day": 3, "goals": ["CI/CD 파이프라인 구축"], "tasks": ["workflow 작성"] },
          { "day": 4, "goals": ["샘플 서비스 배포"], "tasks": ["K8s manifest 작성"] },
          { "day": 5, "goals": ["환경 분리"], "tasks": ["tfvars 분리"] },
          { "day": 6, "goals": ["모니터링 추가"], "tasks": ["로그/모니터링 적용"] },
          { "day": 7, "goals": ["문서화/데모 준비"], "tasks": ["README 작성"] }
        ]
      }
    ],
    "notes": "프로젝트 1은 IaC/배포 중심."
  }
}
```

---

## 8) Notes

- This MVP assumes **paste-in JD** (no scraping).
- Keyword normalization is applied to the resume based on JD vocabulary (aliases/formatting).
- JD parsing **excludes** education/degree requirements and visa/work authorization requirements.
