FROM python:3.10
WORKDIR /app

COPY requirements.txt .
COPY producer.py .

RUN pip install -r requirements.txt
CMD python3 producer.py