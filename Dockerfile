FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TEMPMAILG_URL=https://tempmailg.com/es \
    DB_PATH=/app/data/emails.db \
    CHROME_DRIVER_PATH=/usr/bin/chromedriver \
    CHROME_BINARY=/usr/bin/chromium \
    HEADLESS_MODE=True

# Debian Chromium/Chromedriver are architecture-aware (amd64/arm64), unlike
# the old hard-coded Google Chrome + chromedriver download.
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data /app/screenshots

CMD ["python", "cli.py", "--help"]
