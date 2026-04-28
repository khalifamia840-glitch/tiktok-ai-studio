FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    ca-certificates \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN mkdir -p outputs/audio outputs/media

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
