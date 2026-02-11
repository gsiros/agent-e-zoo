FROM python:3.11-slim

# Install only what's needed: Chrome, X11 libs, and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
       | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    # X11 libraries for forwarding the Chrome window
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# Install Playwright browser (chromium channel chrome is already installed above)
RUN playwright install

# Copy application code
COPY . .

# Allow X11 forwarding — DISPLAY is passed at runtime via `docker run -e DISPLAY`
ENV PYTHONUNBUFFERED=1

# API server port
EXPOSE 8000

# Command to run the agent
ENTRYPOINT ["python", "entrypoint.py"]
# Arguments passed to docker run will be passed to entrypoint.py as command-line arguments
CMD []
