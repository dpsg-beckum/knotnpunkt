# knotnpunkt
Hier entsteht die Zelte- und Materialverwaltung der [DPSG St. Stephanus Beckum](https://www.dpsg-beckum.de)


## Herunterladen und Testen

### Python
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd knotnpunkt

pip install -r reqirements.txt

cd webapp

python app.py
```

### Docker
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd knotnpunkt

docker build -t knotnpunkt:latest .

docker run -d --name knotnpunkt -p 5000:5000 knotnpunkt:latest
```
Standardbenutzername und Passwort:
```
Benutzername: admin
Passwort: admin
```


---
  <a href="https://www.instagram.com/dpsg_beckum">
    <img src="https://img.shields.io/badge/%40dpsg__beckum-Instagram-003056" alt="DPSG Beckum auf Instagram">
  </a>

Verwendete Bibliotheken:
+ [mebjas/html5-qrcode](https://github.com/mebjas/html5-qrcode)
