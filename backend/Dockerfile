# --- Tadna Insta backend (FastAPI + instaloader) ---
FROM python:3.12-slim

# Liara Iranian PyPI mirror — the default PyPI is unreliable on this network.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple/ \
    PIP_TRUSTED_HOST=package-mirror.liara.ir \
    PIP_TIMEOUT=120 \
    PIP_RETRIES=8 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so the layer is cached across code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App source.
COPY . .

# Persisted data (SQLite DB + cached Instagram sessions) lives here and is
# mounted as a volume by docker-compose so it survives rebuilds.
RUN mkdir -p /app/data

EXPOSE 8000

# Production command (no --reload). The dev override adds --reload.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
