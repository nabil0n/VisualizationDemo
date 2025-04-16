FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

# Copy project configuration from root directory
COPY . /app/

# Install package in development mode
RUN uv pip install -e .

# No need to separately copy src files as we copied the entire project
# But ensure proper permissions just in case
RUN chmod -R 755 /app/app/src/

EXPOSE 8501

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

CMD ["streamlit", "run", "/app/app/src/streamlit_app.py", "--server.address=0.0.0.0"]