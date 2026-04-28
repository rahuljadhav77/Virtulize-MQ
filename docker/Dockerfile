FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pymqi and psycopg2
RUN apt-get update && apt-get install - libaio1 libpq-dev gcc -y && rm -rf /var/lib/apt/lists/*

# Install IBM MQ Client (Requires manual download in real scenario, here we mock the dependency)
# In a real production Dockerfile, you would COPY the IBM MQ Client libs here.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
