# knotnpunkt
Hier entsteht die Zelte- und Materialverwaltung der [DPSG St. Stephanus Beckum](https://www.dpsg-beckum.de)
<center>
[![Instagram](https://img.shields.io/badge/%40dpsg__beckum-Instagram-003056)](https://www.instagram.com/dpsg_beckum)
</center>

## Herunterladen und Testen

### Python
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd /knotnpunkt/webapp

python app.py
```

### Docker
```
git clone https://github.com/dpsg-beckum/knotnpunkt.git

cd /knotnpunkt/webapp

docker build -t knotnpunkt:latest .

docker run -p 5000:5000 -n knotnpunkt -d knotnpunkt:latest
```