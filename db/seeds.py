# This file should contain records you want created when you run flask db seed.
#
# Example:
#...
from knotnpunkt.models import Ausleihe, Kategorie, Material, Rolle, Benutzer, Adresse, db

from datetime import datetime as dt

rollen = [
{"name": "admin","schreibenKalender":1,"lesenKalender":1,"schreibenBenutzer":1,"lesenBenutzer":1,"schreibenMaterial":1,"lesenMaterial":1,"schreibenEinstellungen":1,"lesenEinstellungen":1},
{"name": "stavo","schreibenKalender":1,"lesenKalender":1,"schreibenBenutzer":1,"lesenBenutzer":1,"schreibenMaterial":1,"lesenMaterial":1,"schreibenEinstellungen":0,"lesenEinstellungen":1},
{"name": "leiter","schreibenKalender":1,"lesenKalender":1,"schreibenBenutzer":0,"lesenBenutzer":1,"schreibenMaterial":1,"lesenMaterial":1,"schreibenEinstellungen":0,"lesenEinstellungen":0},
{"name": "api","schreibenKalender":0,"lesenKalender":0,"schreibenBenutzer":0,"lesenBenutzer":0,"schreibenMaterial":1,"lesenMaterial":1,"schreibenEinstellungen":0,"lesenEinstellungen":0}]
for r in rollen:
    if Rolle.query.get(r["name"]) is None:
        db.session.add(Rolle(**r))
        db.session.commit()

adressen = [
{"straße":"Musterstr", "hausnummer": 33, "postleitzahl": 12345, "ort": "Musterhausen"},
{"straße":"Hammer Str", "hausnummer": 23, "postleitzahl": 67890, "ort": "Bad Mustereifel"}]
for a in adressen:
    db.session.add(Adresse(**a))
    db.session.commit()

benutzer = [
{"benutzername":"mmuster", "name": "Max Musterman", "emailAdresse":"muster@dpsg.de", "passwort": "muster", "idRolle": 3},
{"benutzername":"admin", "name": "Robert Baden-Powell", "emailAdresse":"test@dpsg.de", "passwort": "admin","idRolle": 1}]
for b in benutzer:
    if Benutzer.query.get(b['benutzername']) is None:
        db.session.add(Benutzer(**b))
        db.session.commit()
        pass


kategorien = [
{"name": "Zelte", "istZaehlbar": 0,},
{"name": "Zubehoer", "istZaehlbar": 1,},
{"name": "Werkzeug", "istZaehlbar": 1,}
]
for kat in kategorien:
    db.session.add(Kategorie(**kat))
    db.session.commit()

materialien = [
{"name": "8er Jurte", "eigenschaften": '{"verfuegbar": true, "zaehlbar": false, "zuletztGescannt": "2021-12-05 10:10", "farbe": "Blau", "beschreibung": "Große Jurte, 2016 gekauft, inklusive Abspannseilen"}',	"kategorie": 1},
{"name": "Hering groß", "eigenschaften": '{"verfuegbar": 3, "anzahl": 12, "zaehlbar": true, "zuletztGescannt": "2021-11-13 10:10"}', "kategorie": 2},
{"name": "Sudan I", "eigenschaften": '{"verfuegbar": true, "zaehlbar": false, "zuletztGescannt": "2021-12-05 10:10", "farbe": "weiß"}', "kategorie": 1}
]
for mat in materialien:
    db.session.add(Material(**mat))
    db.session.commit()

ausleihen = [
{"ersteller_benutzername": "admin", "empfaenger": "Person A", "ts_erstellt":dt.strptime("2022-01-08 12:40:32", "%Y-%m-%d %H:%M:%S"), "ts_beginn":dt.strptime("2022-01-08", "%Y-%M-%d"), "ts_ende":dt.strptime("2022-01-18", "%Y-%m-%d"), "beschreibung": "", "materialien": "1,2,3"},
{"ersteller_benutzername": "admin", "empfaenger": "Person A", "ts_erstellt":dt.strptime("2021-11-08 06:40:32", "%Y-%m-%d %H:%M:%S"), "ts_beginn":dt.strptime("2021-11-08", "%Y-%M-%d"), "ts_ende":dt.strptime("2021-12-08", "%Y-%m-%d"), "beschreibung": "", "materialien": "1,3"}
]
for au in ausleihen:
    db.session.add(Ausleihe(**au))
    db.session.commit()