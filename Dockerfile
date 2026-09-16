FROM python:3.12-slim

# Prevent python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOME=/home/user \
    HF_HOME=/home/user/.cache/huggingface \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# Create non-root user for Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user && \
    mkdir -p /app /home/user/.cache/huggingface && \
    chown -R user:user /app /home/user

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files and set ownership
COPY . .
RUN chown -R user:user /app

# Switch to non-root user
USER user

# Expose server port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Run FastAPI app with uvicorn (binds to $PORT if set, or 7860)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
