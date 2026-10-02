FROM python:3.13-slim

WORKDIR /app

# Install system deps (gcc so any C-extension in requirements compiles)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app
COPY . /app

# Railway sets PORT at runtime; the app reads it from env
ENV PORT=8080
EXPOSE 8080

CMD ["python", "student_server.py"]
