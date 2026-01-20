# Apps 폴더 가이드 (Frontend + Backend)

> 백엔드 개발자도 이해할 수 있는 프론트엔드 & Docker 설명서

## 목차
1. [전체 구조](#1-전체-구조)
2. [Backend (FastAPI)](#2-backend-fastapi)
3. [Frontend (React)](#3-frontend-react)
4. [Docker 설정](#4-docker-설정)
5. [실행 방법](#5-실행-방법)
6. [데이터 흐름](#6-데이터-흐름)

---

## 1. 전체 구조

```
apps/
├── api/                 # Backend (Python FastAPI)
│   ├── __init__.py
│   ├── main.py          # API 엔드포인트 정의
│   └── Dockerfile       # Docker 이미지 빌드 설정
│
└── web/                 # Frontend (React + TypeScript)
    ├── src/
    │   ├── components/  # UI 컴포넌트들
    │   ├── lib/         # 유틸리티 함수
    │   └── types/       # TypeScript 타입 정의
    ├── package.json     # npm 의존성 (Python의 requirements.txt와 비슷)
    └── vite.config.ts   # 빌드 도구 설정
```

---

## 2. Backend (FastAPI)

### 2.1 `main.py` 핵심 구조

```python
# FastAPI 앱 생성 (Flask와 비슷)
app = FastAPI(title="Career Orchestrator API")

# CORS 설정 - 프론트엔드에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 개발 서버 주소
)

# 엔드포인트 정의
@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    # Resume와 JD를 분석하고 결과 반환
    ...
```

### 2.2 CORS가 뭐야?

브라우저 보안 정책상, `localhost:5173` (프론트엔드)에서 `localhost:8000` (백엔드)로 직접 요청하면 **차단**됩니다.

CORS 설정은 "이 주소에서 오는 요청은 허용해줘"라고 백엔드에 알려주는 것입니다.

```
[브라우저 localhost:5173] --요청--> [백엔드 localhost:8000]
                                         │
                              CORS 설정이 없으면 차단!
                              CORS 설정이 있으면 허용!
```

---

## 3. Frontend (React)

### 3.1 Python 개발자를 위한 React 개념 매핑

| Python/Flask | React/TypeScript |
|--------------|------------------|
| `requirements.txt` | `package.json` |
| `pip install` | `npm install` |
| `python app.py` | `npm run dev` |
| Jinja 템플릿 | JSX (HTML + JS 혼합) |
| 함수 | 컴포넌트 (함수형) |
| 클래스 | TypeScript interface |

### 3.2 핵심 파일 설명

#### `src/App.tsx` - 메인 진입점
```tsx
// Python의 if __name__ == "__main__": 같은 역할
function App() {
  return (
    <div>
      <AnalyzeForm />  {/* 컴포넌트 = 재사용 가능한 UI 조각 */}
    </div>
  );
}
```

#### `src/components/` - UI 컴포넌트들

| 파일 | 역할 |
|------|------|
| `ResumeInput.tsx` | Resume 텍스트 입력 영역 |
| `JDInputItem.tsx` | JD 한 개 입력 (카테고리 선택 + 텍스트) |
| `JDInputList.tsx` | JD 입력 목록 관리 + "추가" 버튼 |
| `AnalyzeForm.tsx` | 전체 폼 조합 + API 호출 + 결과 표시 |

#### `src/lib/api.ts` - API 호출 함수
```typescript
// Python의 requests.post()와 동일한 역할
export async function analyzeResume(request: AnalyzeRequest) {
  const response = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),  // Python: json.dumps()
  });
  return response.json();  // Python: response.json()
}
```

#### `src/types/index.ts` - 타입 정의
```typescript
// Python의 Pydantic BaseModel과 동일한 역할
interface JDInput {
  id: string;
  category: "required" | "preferred" | "responsibility" | "context";
  text: string;
}

interface AnalyzeRequest {
  resume_text: string;
  jd_inputs: JDInput[];
}
```

### 3.3 컴포넌트 계층 구조

```
App.tsx
└── AnalyzeForm.tsx (상태 관리 + API 호출)
    ├── ResumeInput.tsx (Resume 입력)
    └── JDInputList.tsx (JD 목록)
        └── JDInputItem.tsx (개별 JD 입력) × N개
```

### 3.4 상태(State)란?

React에서 **상태**는 "변할 수 있는 데이터"입니다.

```tsx
// Python 변수와의 차이점
name = "John"      # Python: 값 변경해도 화면 안 바뀜
const [name, setName] = useState("John")  # React: setName() 호출하면 화면 자동 업데이트
```

`AnalyzeForm.tsx`의 상태들:
```tsx
const [resumeText, setResumeText] = useState("");     // Resume 텍스트
const [jdInputs, setJdInputs] = useState([...]);      // JD 입력 목록
const [isLoading, setIsLoading] = useState(false);    // 로딩 중 여부
const [result, setResult] = useState(null);           // API 결과
```

---

## 4. Docker 설정

### 4.1 Dockerfile 설명

```dockerfile
# 베이스 이미지 (Python 3.12가 설치된 가벼운 Linux)
FROM python:3.12-slim

# 작업 디렉토리 설정 (cd /app 같은 것)
WORKDIR /app

# 시스템 패키지 설치 (일부 Python 패키지 빌드에 필요)
RUN apt-get update && apt-get install -y build-essential

# 프로젝트 파일 복사
COPY pyproject.toml .
COPY README.md .
COPY packages/ packages/
COPY apps/ apps/

# Python 패키지 설치
RUN pip install -e .

# 포트 노출 (문서용, 실제 동작에 영향 없음)
EXPOSE 8000

# 컨테이너 시작 시 실행할 명령
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 docker-compose.yml 설명

```yaml
services:
  api:
    build:
      context: .                    # 빌드 컨텍스트 (프로젝트 루트)
      dockerfile: apps/api/Dockerfile
    ports:
      - "8000:8000"                 # 호스트:컨테이너 포트 매핑
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}  # 환경변수 전달
    volumes:
      - ./packages:/app/packages:ro  # 코드 변경 시 자동 반영 (개발용)
      - ./apps:/app/apps:ro
```

### 4.3 Docker 명령어

```bash
# 이미지 빌드 + 컨테이너 실행
docker compose up --build

# 백그라운드 실행
docker compose up -d --build

# 컨테이너 중지
docker compose down

# 로그 확인
docker compose logs -f
```

---

## 5. 실행 방법

### 5.1 Backend 실행 (Docker)

```bash
# 프로젝트 루트에서
cd /path/to/AI-Career-to-Project-Orchestrator

# 환경변수 설정 (이미 ~/.zshrc에 있으면 생략)
export OPENAI_API_KEY=sk-your-key

# Docker로 실행
docker compose up --build
```

**확인:** http://localhost:8000/health 접속 → `{"status": "healthy"}` 표시되면 성공

### 5.2 Frontend 실행 (로컬)

```bash
# web 폴더로 이동
cd apps/web

# 의존성 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

**확인:** http://localhost:5173 접속 → UI 표시되면 성공

---

## 6. 데이터 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (localhost:5173)                 │
├─────────────────────────────────────────────────────────────┤
│  1. 사용자가 Resume 텍스트 입력                              │
│  2. 사용자가 JD 섹션들 입력 (카테고리 선택)                   │
│  3. "Analyze" 버튼 클릭                                      │
│                         │                                    │
│                         ▼                                    │
│  4. analyzeResume() 함수가 POST 요청 전송                    │
└─────────────────────────│────────────────────────────────────┘
                          │
                          │ POST /analyze
                          │ { resume_text, jd_inputs }
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (localhost:8000)                   │
├─────────────────────────────────────────────────────────────┤
│  5. Request 유효성 검사 (Pydantic)                           │
│  6. resume_parse_tool 호출 → Resume 키워드 추출              │
│  7. jd_parse_tool 호출 → JD 키워드 추출                      │
│  8. Gap 분석 & 점수 계산                                     │
│  9. Response 반환                                            │
└─────────────────────────│────────────────────────────────────┘
                          │
                          │ { gap_summary: { match_score, missing_keywords, ... } }
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (결과 표시)                      │
├─────────────────────────────────────────────────────────────┤
│  10. match_score 표시 (예: 75%)                              │
│  11. missing_keywords 목록 표시                              │
│  12. 사용자가 결과 확인                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 자주 묻는 질문

### Q: npm이 뭐야?
**A:** Python의 `pip` 같은 패키지 관리자입니다. `package.json`은 `requirements.txt`와 같은 역할입니다.

### Q: TypeScript가 뭐야?
**A:** JavaScript에 타입을 추가한 언어입니다. Python의 타입 힌트(`def foo(x: int) -> str`)와 비슷하지만, 컴파일 시점에 타입 체크를 합니다.

### Q: Vite가 뭐야?
**A:** 프론트엔드 빌드 도구입니다. 개발 서버 실행, 코드 번들링(여러 파일을 하나로 합침), Hot Reload(코드 변경 시 자동 새로고침) 등을 담당합니다.

### Q: shadcn/ui가 뭐야?
**A:** 미리 만들어진 UI 컴포넌트 라이브러리입니다. Button, Select, Card 같은 컴포넌트를 직접 안 만들어도 됩니다. Bootstrap이나 Material UI 같은 것이지만, 코드를 직접 프로젝트에 복사해서 커스터마이징이 쉽습니다.

### Q: 왜 Frontend는 Docker로 안 띄워?
**A:** 개발 중에는 Hot Reload (코드 변경 시 자동 새로고침) 기능이 중요한데, Docker 안에서는 이게 잘 안 됩니다. 배포할 때는 Frontend도 Docker로 띄울 수 있습니다.

---

## 문제 해결

### Backend 연결 안 됨
1. Docker가 실행 중인지 확인: `docker ps`
2. http://localhost:8000/health 접속해서 응답 확인
3. CORS 에러면 `main.py`의 `allow_origins` 확인

### Frontend 빌드 에러
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules
npm install
```

### Docker 빌드 실패
```bash
# 캐시 없이 새로 빌드
docker compose build --no-cache
```
