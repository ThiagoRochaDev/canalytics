FROM node:22-bookworm-slim AS web
WORKDIR /build
COPY apps/web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CANALYTICS_DATA_DIR=/data
WORKDIR /app
COPY apps/api/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir -r /tmp/requirements.lock && useradd --create-home --uid 10001 canalytics && mkdir /data && chown canalytics:canalytics /data
COPY --chown=canalytics:canalytics apps/api/ /app/apps/api/
COPY --from=web --chown=canalytics:canalytics /build/dist /app/apps/web/dist
COPY LICENSE NOTICE /app/
USER canalytics
EXPOSE 8093
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8093/api/health')"
CMD ["python","-m","uvicorn","canalytics.main:app","--app-dir","apps/api","--host","0.0.0.0","--port","8093","--workers","1","--no-access-log"]
