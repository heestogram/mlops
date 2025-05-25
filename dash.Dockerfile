
# 1. 베이스 이미지 설정
FROM python:3.12.0-slim

# 2. 작업 디렉토리 설정
WORKDIR /home/dash

# 3. 필요한 시스템 패키지 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential wget \
    && rm -rf /var/lib/apt/lists/*

# 4. Python 패키지 설치
RUN pip install --no-cache-dir dash plotly numpy pandas

# 5. Dash 기본 설정 (포트와 설정 파일)
EXPOSE 9101

# 6. 실행 명령어
CMD ["python3", "app_run.py"]
