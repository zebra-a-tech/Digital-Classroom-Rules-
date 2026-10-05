FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

ARG FORCE_FRESH=1791208063
COPY . /app

ENV PORT=8080
EXPOSE 8080

CMD ["python", "student_server.py"]
