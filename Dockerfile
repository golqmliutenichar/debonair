# ─── build & runtime in ONE image ─────────────────────────────────
FROM ubuntu:22.04

# 1. system packages -------------------------------------------------
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv nginx supervisor netcat curl mariadb-client && \
    rm -rf /var/lib/apt/lists/*

# 2. python deps -----------------------------------------------------
WORKDIR /srv/app
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 3. copy code & nginx ----------------------------------------------
COPY app/ /srv/app
COPY nginx/nginx.conf   /etc/nginx/nginx.conf

# 4. supervisor to run **both** processes ---------------------------
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD \
 #   curl -fs http://localhost/health || exit 1

EXPOSE 80
HEALTHCHECK CMD curl -f http://localhost/ || exit 1
CMD ["/usr/bin/supervisord","-n"]


#HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
#CMD curl -fs http://localhost/ || exit 1
