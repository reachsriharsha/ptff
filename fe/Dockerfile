FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates ./templates
COPY static ./static
COPY wsgi.py .

RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn
COPY . .

#CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]