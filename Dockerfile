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
# RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
#     -subj "/C=DE/ST=Denial/L=Germany/O=DPSG Beckum/CN=knotnpunkt" \
#     -keyout key.pem  -out cert.pem

# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--certfile", "cert.pem", "--keyfile", "key.pem", "knotnpunkt.__init__:app"]
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "knotnpunkt.__init__:app"]