# ---- Python API (FastAPI + PostgreSQL client) ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安裝依賴 (先複製 requirements 以利用 layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

# uvicorn 啟動，--host 0.0.0.0 讓容器外可連入
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
