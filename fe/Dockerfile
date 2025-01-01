FROM python:3.12-slim

COPY requirements.txt /app/requirements.txt
WORKDIR /app
COPY app.py .
COPY templates ./templates
COPY static ./static
COPY wsgi.py .
RUN pip install -r requirements.txt
COPY . .

RUN mkdir -p /app/uploads
#CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]