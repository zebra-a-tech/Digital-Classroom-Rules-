FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Changing BUILD_ID on every install busts the layer cache for everything below.
ARG BUILD_ID=20261005155920
ENV BUILD_ID=$BUILD_ID
RUN echo "$BUILD_ID" > /tmp/build_id
COPY . .
CMD ["sh", "-c", "gunicorn student_server:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 60"]
