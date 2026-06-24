# StarRailCopilot-Web — Dockerfile
# Python SRC scheduler with Web Gateway device method.
# Connects to webdeck (Go Gateway) + Chrome via HTTP — no Playwright needed.
#
# Build:
#   docker build -t src-web .
#
# Run (requires webdeck + Chrome already running):
#   docker run -v ./config:/app/config src-web

FROM python:3.10-slim-bookworm

WORKDIR /app

# System deps for OpenCV / PaddleOCR / PyAV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    pkg-config libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configure via SRC config files:
#   Emulator_Serial = 'web_gateway'
#   Emulator_ScreenshotMethod = 'WebGateway'
#   Emulator_ControlMethod = 'WebGateway'
#   Emulator_GatewayUrl = 'http://webdeck:8090'

CMD ["python", "src.py"]
