FROM python:3.12-slim

COPY ./be/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

#RUN pip install fastapi uvicorn
COPY . .
RUN mkdir -p /app/uploads
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "3", "--port", "8000"]