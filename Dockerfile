FROM python:3.10-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
 && rm -rf /var/lib/apt/lists/*
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
RUN adduser --disabled-password --gecos "" debonair
USER debonair
WORKDIR /home/debonair/app
COPY --chown=debonair:debonair requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY --chown=debonair:debonair . .
EXPOSE 5000
ENTRYPOINT ["python3", "app.py"]
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "workers", "3", "app:app" ]