FROM python:3.10-alpine

# Update alpine packages
RUN apk --no-cache update \
&& apk upgrade

# Install Backend dependencies. Encapsulated in one step to minimize Image size
COPY requirements.txt  .
RUN apk add --no-cache cairo python3-dev libffi-dev libart-lgpl freetype freetype-dev py3-reportlab gcc libc-dev \
&& python -m pip install --upgrade pip setuptools \
&& python -m pip install --no-cache-dir -r requirements.txt \
&& python -m pip install --no-cache-dir gunicorn \
&& apk del --quiet gcc libc-dev

# Copy app files
WORKDIR /app
COPY . /app
RUN mkdir /data \
&& chmod o+rw /data \
&& chmod o+r /app

# Install frontend dependencies using yarn
RUN apk add --no-cache npm \
&& npm install --global yarn \
&& yarn install \
&& apk del --quiet npm nodejs

# Create user
RUN adduser -D kp-user
USER kp-user

# Config
EXPOSE 8080
HEALTHCHECK --start-period=5s \  
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1   
ENV KP_DOCKER=1
ENV KP_INSTANCE_PATH=/data

# Run server
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "knotnpunkt:create_app()"]
CMD []

# OpenSSL example command for TLS certificates
# RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
#     -subj "/C=DE/ST=Denial/L=Germany/O=DPSG Beckum/CN=knotnpunkt" \
#     -keyout key.pem  -out cert.pem
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--certfile", "cert.pem", "--keyfile", "key.pem", "knotnpunkt.__init__:app"]
