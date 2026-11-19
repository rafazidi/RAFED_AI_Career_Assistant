FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/tmp/huggingface

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY knowledge_base /app/knowledge_base
COPY do_ingest.py /app/do_ingest.py

EXPOSE 7860

CMD ["sh", "-c", "python do_ingest.py && uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 7860"]
