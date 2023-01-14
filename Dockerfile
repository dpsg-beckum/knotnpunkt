FROM nikolaik/python-nodejs:python3.10-nodejs18-slim
EXPOSE 8080

COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn

RUN apt-get update && apt-get install -y cairosvg python3-dev libffi-dev

WORKDIR /app
RUN mkdir /data
ENV KP_DOCKER=1
ENV KP_DATABASE_PATH=/data/knotnpunkt.db 
COPY . /app

RUN yarn install

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--certfile", "cert.pem", "--keyfile", "key.pem", "knotnpunkt.__init__:app"]