FROM python:3.8
WORKDIR /app

COPY requirements.txt .
COPY ./consumer.py ./.

RUN pip install -r requirements.txt
CMD python3 consumer.py
