FROM python:3.13-alpine

# Service Port
ENV SPEEDTEST_PORT=9798
ENV SPEEDTEST_TIMEOUT=90
ENV NUM_WORKERS=4

# Expose port
EXPOSE ${SPEEDTEST_PORT}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Speedtest CLI Version
ARG SPEEDTEST_VERSION=1.2.0

# Install system dependencies
RUN apk add --no-cache \
    ca-certificates \
    curl \
    wget \
    && rm -rf /var/cache/apk/*

# Install Speedtest CLI
RUN ARCHITECTURE=$(uname -m) && \
    if [ "$ARCHITECTURE" = 'armv7l' ]; then ARCHITECTURE="armhf"; fi && \
    wget -nv -O /tmp/speedtest.tgz "https://install.speedtest.net/app/cli/ookla-speedtest-${SPEEDTEST_VERSION}-linux-${ARCHITECTURE}.tgz" && \
    tar zxvf /tmp/speedtest.tgz -C /tmp && \
    cp /tmp/speedtest /usr/local/bin && \
    chmod +x /usr/local/bin/speedtest && \
    rm -rf /tmp/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

WORKDIR /app
COPY ./speedtest-exporter-app /app/speedtest-exporter-app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Add metadata
LABEL org.opencontainers.image.source="https://github.com/jimmydoh/speedtest-exporter"
LABEL org.opencontainers.image.description="Prometheus Exporter for Speedtest"

# Setup Healtheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q -O - http://localhost:$SPEEDTEST_PORT/ || exit 1

# Start gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$SPEEDTEST_PORT --timeout $SPEEDTEST_TIMEOUT --workers $NUM_WORKERS speedtest-exporter-app.webapp:app"]
