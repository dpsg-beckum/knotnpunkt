# <center>knotnpunkt</center>
![GitHub last commit](https://img.shields.io/github/last-commit/dpsg-beckum/knotnpunkt)
![GitHub](https://img.shields.io/github/license/dpsg-beckum/knotnpunkt)
![Plattformen](https://img.shields.io/badge/platform-python%20%7C%20docker-003056)

Eine Webapp die zur Verwaltung von Stammesmaterial verwendet werden kann. Entwickelt von der [DPSG St. Stephanus Beckum](https://www.dpsg-beckum.de)


## Installation mit Docker

```bash
docker run -p 8080:8080 dpsgbeckum/knotnpunkt
```
### Optional: HTTPS aktivieren
```bash
docker run --rm -it -p 8080:8080 dpsgbeckum/knotnpunkt --certfile /path/to/cert.pem --keyfile /path/to/key.pem
```
### Optional: Speichern der Datenbankdatei in einem Volume
```bash
docker run --rm -it -p 8080:8080 -v knotnpunkt_data:/data knotnpunkt
```
### Docker-Image lokal erstellen:

### 1. Repository klonen
```bash 
git clone https://github.com/dpsg-beckum/knotnpunkt.git
cd knotnpunkt
```
### 2. Docker-Image erzeugen:
```bash
docker build --tag local-knotnpunkt .
```
#### 3. Docker-Container starten
```bash
docker run -p 8080:8080 local-knotnpunkt
```
### Standardbenutzername und Passwort:

Benutzername: `admin`

Passwort: `admin`

## Funktionen

- [x] Anlegen von Material mit Kategorie, Bild, etc.
- [x] Ausleihen/Auschecken von Material
- [x] Identifikation von Material durch integrierten QR-Code-Scanner
- [x] Einreichen von Kostenbelegen



## [WIP] Contributing

+ Um zu erfahren, wie du bei knotnpunkt mithelfen kannst, lies bitte in der Datei [CONTRIBUTING.md](.github/CONTRIBUTING.md) nach 
+ Um die Entwicker*innenversion zu starten, befolge diese Schritte:

### Voraussetzungen:
+ Python
+ NodeJS + yarn
+ Git

### 1. Repository klonen
```PowerShell
git clone https://github.com/dpsg-beckum/knotnpunkt.git
cd knotnpunkt
```

### 2. Python-Umgebung vorbereiten
```PowerShell
python -m venv .venv
.venv/Scripts/activate
pip install -r reqirements.txt
```

### 3. JavaScript-Bibliotheken installieren
```PowerShell
yarn install 
```

### 5. Flask-Server starten
```PowerShell
flask run
```


## Acknowledgements
+ [flask Framework](https://github.com/pallets/flask)
+ [Bootstrap](https://github.com/twbs/bootstrap)
+ [fontawesome](https://github.com/FortAwesome/Font-Awesome)
+ [fullcalender](https://github.com/fullcalendar/fullcalendar)
+ [html5-qrcode](https://github.com/mebjas/html5-qrcode)
+ [DPSG](https://dpsg.de/de/vorlagen)

---
[![Instagram](https://img.shields.io/badge/Instagram-%40dpsg__beckum-003056)](https://www.instagram.com/dpsg_beckum)
