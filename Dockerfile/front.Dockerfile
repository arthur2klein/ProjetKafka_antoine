FROM nginx:alpine
WORKDIR /app

COPY requirements.txt .
COPY front.html .

CMD nginx 