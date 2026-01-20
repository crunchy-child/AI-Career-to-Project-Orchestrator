# apps/api/Dockerfile
FROM python:3.12-slim

# 작업 디렉토리 설정 (cd /app 같은 것)
WORKDIR /app

# Install system dependencies
# Build-essential은 C/C++로 된 코드를 컴파일할 수 있도록 해주는 패키지
# 혹시라도 파이썬 라이브러리중 C기반으로 된 라이브러리(속도면에서 C가 빠른 경우)가 있을 경우를 대비
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files (프로젝트 파일 복사 --> Docker /app)
COPY pyproject.toml .
COPY README.md .
COPY packages/ packages/
COPY apps/ apps/

# Install Python dependencies (파이썬 패키지 설치)
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "apps.api.main:app", "--host", "127.0.0.1", "--port", "8000"]
