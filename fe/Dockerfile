FROM python:3.12-slim

COPY ./fe/requirements.txt /app/requirements.txt
WORKDIR /app
COPY ./fe/app.py .
COPY ./fe/templates ./templates
COPY ./fe/static ./static
COPY ./fe/wsgi.py .
RUN pip install -r requirements.txt
COPY . .

RUN mkdir -p /app/uploads
#CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]