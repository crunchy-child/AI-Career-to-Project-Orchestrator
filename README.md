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

> Implementation detail: “Experience/Project” means the keyword appears in parsed resume bullets under experience/project sections.

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
Project Planner Agent 
   ↓
Final Output (JSON + optional Markdown export)
```

### Agent tools (functions)

**Resume Analysis Agent tools**

- `jd_parse_tool(jd_text) -> JDProfile`
- `resume_parse_tool(resume_text) -> ResumeProfile`
- `normalize_keywords_tool(resume_profile, jd_profile) -> ResumeProfile` (normalize resume based on JD vocabulary)
- `gap_compute_tool(JDProfile, ResumeProfile) -> GapSummary`
- `score_tool(gap_summary) -> GapSummary`

**Project Planner Agent tools**

- `project_ideation_tool(GapSummary) -> list[ProjectIdea]`
- `architecture_tool(list[ProjectIdea]) -> list[ArchitectureSpec]`
- `project_plan_tool(list[ProjectIdea], list[ArchitectureSpec]) -> list[ProjectPlan]`

---

## 3) Data Schemas (v2)

- `resume.py` → `ResumeProfile`
  - `raw_text`
  - `keywords`
  - `normalized`, `normalization_notes`, `normalization_map_applied`
  - `validated_keywords_set`
- `jd.py` → `JDProfile`
  - `raw_text`
  - `keywords`
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
      },
      {
        "keyword_pair": [
          {
            "keyword_text": "ci/cd",
            "category": "entries",
            "evidence": "Built CI/CD pipeline in project"
          },
          {
            "keyword_text": "ci/cd",
            "category": "preferred",
            "evidence": "JD: Preferred CI/CD experience",
            "importance": 3
          }
        ],
        "match_type": "partial"
      },
      {
        "keyword_pair": [
          {
            "keyword_text": "terraform",
            "category": "skills",
            "evidence": null
          },
          {
            "keyword_text": "terraform",
            "category": "required",
            "evidence": "JD: Required Infrastructure as Code (Terraform)",
            "importance": 5
          }
        ],
        "match_type": "missing"
      }
    ],
    "missing_keywords": [
      {
        "keyword_text": "terraform",
        "category": "required",
        "evidence": "JD: Required Infrastructure as Code (Terraform)",
        "importance": 5
      },
      {
        "keyword_text": "airflow",
        "category": "preferred",
        "evidence": "JD: Preferred Airflow experience",
        "importance": 3
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
          "covers_keywords": [
            {
              "keyword_text": "terraform",
              "category": "required",
              "evidence": "프로젝트 결과물로 IaC 적용 증명",
              "importance": 5
            },
            {
              "keyword_text": "ci/cd",
              "category": "preferred",
              "evidence": "GitHub Actions 기반 배포 자동화",
              "importance": 3
            }
          ],
          "constraints": [
            "1주일",
            "1인",
            "비용 0"
          ],
          "tech_stack": [
            "Terraform",
            "GitHub Actions",
            "AWS",
            "Kubernetes"
          ]
        },
        "architecture": {
          "summary": "Terraform으로 인프라 구성 후 CI/CD로 배포 자동화",
          "components": [
            "Terraform modules",
            "GitHub Actions",
            "Kubernetes cluster",
            "Container registry"
          ],
          "data_flow": "Push -> CI build/test -> Terraform apply -> K8s deploy",
          "mermaid": "flowchart TD\nA[Push]-->B[CI]\nB-->C[Terraform Apply]\nC-->D[K8s Deploy]\n"
        },
        "weekly_plan": [
          {
            "day": 1,
            "goals": ["Terraform 프로젝트 초기화"],
            "tasks": ["Provider 설정", "기본 VPC 모듈 작성"],
            "deliverables": ["terraform init 완료", "VPC 모듈"]
          },
          {
            "day": 2,
            "goals": ["K8s 클러스터 구성"],
            "tasks": ["EKS/GKE 선택", "클러스터 리소스 정의"],
            "deliverables": ["클러스터 생성 스크립트"]
          },
          {
            "day": 3,
            "goals": ["CI/CD 파이프라인 구축"],
            "tasks": ["GitHub Actions workflow 작성"],
            "deliverables": ["workflow.yml"]
          },
          {
            "day": 4,
            "goals": ["샘플 서비스 배포"],
            "tasks": ["이미지 빌드", "K8s manifest 작성"],
            "deliverables": ["배포 결과 캡처"]
          },
          {
            "day": 5,
            "goals": ["환경 분리"],
            "tasks": ["dev/stage/prod 변수 분리"],
            "deliverables": ["tfvars 분리"]
          },
          {
            "day": 6,
            "goals": ["모니터링 추가"],
            "tasks": ["로그/모니터링 적용"],
            "deliverables": ["로그/모니터링 캡처"]
          },
          {
            "day": 7,
            "goals": ["문서화/데모 준비"],
            "tasks": ["README 작성", "데모 시나리오 정리"],
            "deliverables": ["README", "데모 영상 링크"]
          }
        ],
        "downside": ["클라우드 비용 발생 가능", "Terraform 러닝커브"],
        "workaround": ["Free tier 사용", "최소 리소스 구성"]
      },
      {
        "idea": {
          "title": "Airflow 기반 ETL 파이프라인",
          "one_liner": "Airflow로 ETL 파이프라인을 구성하고 데이터 품질 검증을 추가",
          "reasoning": "JD에 필요한 Airflow 경험을 프로젝트로 증명 가능",
          "covers_keywords": [
            {
              "keyword_text": "airflow",
              "category": "preferred",
              "evidence": "DAG 설계 및 스케줄링 구현"
            },
            {
              "keyword_text": "postgresql",
              "category": "required",
              "evidence": "ETL 결과 적재"
            }
          ],
          "constraints": [
            "1주일",
            "1인",
            "비용 0"
          ],
          "tech_stack": [
            "Apache Airflow",
            "Python",
            "PostgreSQL",
            "Docker"
          ]
        },
        "architecture": {
          "summary": "Airflow DAG로 수집-가공-적재 파이프라인 구현",
          "components": [
            "Airflow scheduler",
            "ETL scripts",
            "PostgreSQL",
            "Data quality checks"
          ],
          "data_flow": "Raw data -> ETL -> Postgres -> QA checks",
          "mermaid": "flowchart LR\nA[Raw]-->B[ETL]\nB-->C[Postgres]\nC-->D[QA]\n"
        },
        "weekly_plan": [
          {
            "day": 1,
            "goals": ["Airflow 환경 세팅"],
            "tasks": ["Docker Compose 구성"],
            "deliverables": ["Airflow UI 실행"]
          },
          {
            "day": 2,
            "goals": ["ETL 설계"],
            "tasks": ["데이터 소스 선정", "ETL 스크립트 작성"],
            "deliverables": ["ETL 스크립트"]
          },
          {
            "day": 3,
            "goals": ["DAG 연결"],
            "tasks": ["DAG 등록 및 스케줄 설정"],
            "deliverables": ["동작하는 DAG"]
          },
          {
            "day": 4,
            "goals": ["데이터 적재"],
            "tasks": ["테이블 설계", "적재 검증"],
            "deliverables": ["Postgres 테이블"]
          },
          {
            "day": 5,
            "goals": ["품질 검사 추가"],
            "tasks": ["결측/중복 검사"],
            "deliverables": ["QA task"]
          },
          {
            "day": 6,
            "goals": ["리포트 생성"],
            "tasks": ["요약 통계 및 시각화"],
            "deliverables": ["리포트 결과"]
          },
          {
            "day": 7,
            "goals": ["문서화/데모"],
            "tasks": ["README 작성", "데모 시나리오 정리"],
            "deliverables": ["README", "데모 링크"]
          }
        ],
        "downside": ["초기 설정 복잡", "ETL 데이터 품질 리스크"],
        "workaround": ["공식 Compose 사용", "테스트 데이터로 검증"]
      }
    ],
    "notes": "프로젝트 1은 IaC/배포 중심, 프로젝트 2는 데이터 파이프라인 중심."
  }
}
```

---

## 7) Notes

- This MVP assumes **paste-in JD** (no scraping).
- Keyword normalization is applied to the resume based on JD vocabulary (aliases/formatting).
