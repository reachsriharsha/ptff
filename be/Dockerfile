FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "3", "--port", "8000"]