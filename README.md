# knotnpunkt
Hier entsteht die Zelte- und Materialverwaltung der [DPSG St. Stephanus Beckum](https://www.dpsg-beckum.de)


## Herunterladen und Testen

### Python
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd knotnpunkt/webapp

python app.py
```

### Docker
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd knotnpunkt/webapp

docker build -t knotnpunkt:latest .

docker run -p 5000:5000 -n knotnpunkt -d knotnpunkt:latest
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

