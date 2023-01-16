# knotnpunkt
Hier entsteht die Zelte- und Materialverwaltung der [DPSG St. Stephanus Beckum](https://www.dpsg-beckum.de)


## Herunterladen und Testen

### Voraussetzungen:
+ python
+ yarn
+ git

### 1. Repository klonen
```bash 
git clone https://github.com/dpsg-beckum/knotnpunkt.git
cd knotnpunkt
```

### 2. Python-Umgebung vorbereiten
```bash
python -m venv .venv
pip install -r reqirements.txt
. .venv/bin/activate
```

### 3. JavaScript-Bibliotheken installieren
```bash
yarn install 
```

### 5. Flask-Server starten
```bash
flask run
```

## Docker-Container starten

### 1. Repository klonen
```bash 
git clone https://github.com/dpsg-beckum/knotnpunkt.git
cd knotnpunkt
```
### 2. Docker-Image erzeugen:
```
docker build --tag knotnpunkt .
```
#### 3. Docker-Container starten
```
docker run -p 8080:8080 knotnpunkt
```
### Optional: HTTPS aktivieren
```
docker run --rm -it -p 8080:8080 knotnpunkt --certfile /path/to/cert.pem --keyfile /path/to/key.pem
```

Standardbenutzername und Passwort:

Benutzername: admin
Passwort: admin



---
  <a href="https://www.instagram.com/dpsg_beckum">
    <img src="https://img.shields.io/badge/%40dpsg__beckum-Instagram-003056" alt="DPSG Beckum auf Instagram">
  </a>

Verwendete Bibliotheken:
+ [mebjas/html5-qrcode](https://github.com/mebjas/html5-qrcode)
