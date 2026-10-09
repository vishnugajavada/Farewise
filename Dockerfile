FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY docs ./docs
RUN pip install --no-cache-dir . && useradd --create-home appuser && mkdir -p data/raw data/processed models && chown -R appuser:appuser /app
USER appuser
EXPOSE 8501
CMD ["streamlit","run","src/farewise/ui/app.py","--server.address=0.0.0.0"]
