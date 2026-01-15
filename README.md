# AI Career-to-Project Orchestrator

**Option A (Paste JD Text):** Users paste **Resume text + Job Description (JD) text**, and the system:

1. computes a **JD matching score (0–100)** and **validated missing keywords**, then
2. generates **2 portfolio project plans** (architecture + 7-day sprint plan) that help you _prove_ those missing keywords for your target role.

> **Scope note (v2):** We **do not rewrite/improve the resume itself** in this MVP. The output is a **project blueprint** that helps you build evidence to match your target job.

---

## 0) Goals & Success Criteria

### Goals

- Input:
  - `resume_text`, `jd_text` (paste)
  - **`preferences`** (optional): `{ stack_pref, constraints, role }`
- Output:
  - **Match score (0–100)** with rationale
  - **Validated missing keywords** (Top N)
  - **2 project proposals**, each with:
    - value & proof points
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

> Implementation detail: “Experience/Project” means the keyword appears in parsed resume bullets under experience/project sections.

### 1.3 Final score (0–100)

Let `w_i` be the base weight (0.7 or 0.3) and `m_i` be the evidence multiplier for keyword `i`.

- **Weighted covered sum** = `Σ (w_i × m_i)`
- **Max possible sum** = `Σ w_i`
- **Match score** = `100 × (Weighted covered sum / Max possible sum)`

### 1.4 Validated missing keywords

We compute initial missing keywords via set difference, then validate by:

- removing duplicates/alias collisions
- ensuring the keyword truly exists in JD text/parsed JD keywords

The result is returned as `validated_missing_keywords`.

---

## 2) System Architecture (2 Agents + Tools)

### Why “multi-agent” here?

We use **two role-specialized agents** with a clear handoff:

1. **Resume Analysis Agent** → computes match score + validated missing keywords
2. **Project Planner Agent** → generates project blueprints to cover missing keywords

### Orchestration

We use **LangGraph** to orchestrate the handoff and optional retry branches.

```text
(resume_text, jd_text, preferences)
   ↓
Resume Analysis Agent
   ↓  (validated_missing_keywords + score)
Project Planner Agent (uses preferences)
   ↓
Final Output (JSON + optional Markdown export)
```

### Agent tools (functions)

**Resume Analysis Agent tools**

- `jd_parse_tool(jd_text) -> JDProfile`
- `resume_parse_tool(resume_text) -> ResumeProfile`
- `normalize_keywords_tool(resume_profile, jd_profile) -> ResumeProfile` (normalize resume based on JD vocabulary)
- `extract_sets_tool(jd_profile, resume_profile) -> jd_sets, resume_sets`
- `gap_compute_tool(jd_sets, resume_sets) -> GapSummary`
- `score_tool(gap_summary, jd_sets) -> match_score, rationale`

**Project Planner Agent tools**

- `project_ideation_tool(validated_missing_keywords, role, constraints) -> 2 ideas`
- `architecture_tool(ideas, stack_pref) -> architecture (+ optional mermaid)`
- `sprint_plan_tool(ideas, constraints) -> 7-day plan`

---

## 3) Data Schemas (v2)

- `resume.py` → `ResumeProfile`
- `jd.py` → `JDProfile`
- `gap.py` → `GapSummary`
  - `match_score`
  - `strong_matches`, `partial_matches`
  - `missing_keywords`, `validated_missing_keywords`
- `project.py` → `ProjectOutput`
  - exactly **2** project plans
  - each includes `architecture` + `weekly_plan (D1–D7)`

---

## 4) Repository Structure

```
career-orchestrator/
  apps/
    web/                   # Next.js UI (runs locally)
    api/                   # FastAPI (Dockerized)
  packages/
    core/
      schemas/             # resume.py, jd.py, gap.py, project.py
      utils/               # normalization, scoring, text utils
    tools/                 # parsing/normalization/gap/score/export tools
    agents/                # resume_agent.py, project_agent.py (tool-calling)
    graph/                 # workflow.py (LangGraph: 2 nodes)
  data/
    samples/               # sample resume/jd pairs
  docs/
  .env.example
  docker-compose.yml       # API-only compose
  README.md
```

---

## 5) Running Locally

### 5.1 API (Docker)

- Build & run:
  - `docker compose up --build`
- API should expose:
  - `POST /run` (or `/analyze`) – main entry
  - `GET /health` – health check

### 5.2 Web (Local)

- Run Next.js locally and point it to the API base URL.

---

## 6) Output Example (short)

```json
{
  "analysis": {
    "match_score": 78,
    "strong_matches": ["Python", "REST API"],
    "partial_matches": ["CI/CD"],
    "missing_keywords": ["Kubernetes", "OAuth 2.0", "LangGraph"],
    "validated_missing_keywords": ["Kubernetes", "OAuth 2.0", "LangGraph"],
    "notes": "Required coverage weighted higher than preferred."
  },
  "projects": {
    "project_ideas": [
      { "title": "...", "architecture": "...", "weekly_plan": "..." },
      { "title": "...", "architecture": "...", "weekly_plan": "..." }
    ]
  }
}
```

---

## 7) Notes

- This MVP assumes **paste-in JD** (no scraping).
- Keyword normalization is applied to the resume based on JD vocabulary (aliases/formatting).
