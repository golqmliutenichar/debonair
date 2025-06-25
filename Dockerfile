# ── build + runtime in ONE stage ──────────────────────────────
FROM ubuntu:22.04

# 1. system deps
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv nginx supervisor netcat curl && \
    rm -rf /var/lib/apt/lists/*

# 2. python deps
WORKDIR /srv/app
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 3. copy code + nginx
COPY app/          /srv/app
COPY nginx/nginx.conf  /etc/nginx/nginx.conf
COPY docker/supervisord.conf  /etc/supervisor/conf.d/supervisord.conf

# 4. HEALTHCHECK → ping DB *and* Flask
HEALTHCHECK CMD nc -z $DB_HOST $DB_PORT || exit 1

EXPOSE 80 443
CMD ["/usr/bin/supervisord","-n"]
