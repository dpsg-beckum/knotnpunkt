# This file should contain records you want created when you run flask db seed.
#
# Example:
# from yourapp.models import User


# initial_user = {
#     'username': 'superadmin'
# }
# if User.find_by_username(initial_user['username']) is None:
#     User(**initial_user).save()

# from knotnpunkt import app
from knotnpunkt.database.db import (
    Benutzer,
    Rolle,
    Label,
    Kategorie,
    AuslagenKategorie,
    db,
)

initial_data = {
    "Benutzer": [
        Benutzer(
            benutzername="admin",
            name="Robert Baden-Powell",
            emailAdresse="test@dpsg.de",
            passwort="admin",
            idRolle=1,)

    ],
    "Rolle": [
        Rolle(
            idRolle=1,
            lesenBenutzer=1,
            lesenEinstellungen=1,
            lesenKalender=1,
            lesenMaterial=1,
            name="admin",
            schreibenBenutzer=1,
            schreibenEinstellungen=1,
            schreibenKalender=1,
            schreibenMaterial=1,
            lesenAlleAuslagen=0,
            freigebenAuslagen=0
        ),
        Rolle(
            idRolle=2,
            lesenBenutzer=1,
            lesenEinstellungen=1,
            lesenKalender=1,
            lesenMaterial=1,
            name="stavo",
            schreibenBenutzer=1,
            schreibenEinstellungen=0,
            schreibenKalender=1,
            schreibenMaterial=1,
            lesenAlleAuslagen=1,
            freigebenAuslagen=1
        ),
        Rolle(
            idRolle=3,
            lesenBenutzer=1,
            lesenEinstellungen=0,
            lesenKalender=1,
            lesenMaterial=1,
            name="leiter",
            schreibenBenutzer=0,
            schreibenEinstellungen=0,
            schreibenKalender=1,
            schreibenMaterial=1,
            lesenAlleAuslagen=0,
            freigebenAuslagen=0
        ),
        Rolle(
            idRolle=4,
            lesenBenutzer=0,
            lesenEinstellungen=0,
            lesenKalender=0,
            lesenMaterial=1,
            name="api",
            schreibenBenutzer=0,
            schreibenEinstellungen=0,
            schreibenKalender=0,
            schreibenMaterial=1,
            lesenAlleAuslagen=0,
            freigebenAuslagen=0
        ),
        Rolle(
            idRolle=5,
            lesenBenutzer=1,
            lesenEinstellungen=0,
            lesenKalender=1,
            lesenMaterial=1,
            name="kassenwart",
            schreibenBenutzer=0,
            schreibenEinstellungen=0,
            schreibenKalender=1,
            schreibenMaterial=1,
            lesenAlleAuslagen=1,
            freigebenAuslagen=0
        )
    ],
    "Label": [
        Label(
            datentyp="bool",
            idLabel=1,
            name="verfuegbar"
        )
    ],
    "Kategorie": [
        Kategorie(
            idKategorie=1,
            istZaehlbar=0,
            name="Zelte"
        ),
        Kategorie(
            idKategorie=2,
            istZaehlbar=1,
            name="Zubehoer"
        ),
        Kategorie(
            idKategorie=3,
            istZaehlbar=1,
            name="Werkzeug"
        )
    ],
    "AuslagenKategorie":[
        AuslagenKategorie(
            idAuslKateg=1,
            name="gruppenstunden",
            anzeigeName="Gruppenstunden"
        ),
        AuslagenKategorie(
            idAuslKateg=2,
            name="leiterrunde",
            anzeigeName="Leiterrunde"
        ),
        AuslagenKategorie(
            idAuslKateg=3,
            name="sommerlager",
            anzeigeName="Sommerlager"
        )
    ]
}

for i in initial_data.get('Rolle'):
    if not Rolle.query.get(i.idRolle):
        db.session.add(i)
        db.session.commit()
for i in initial_data.get('Label'):
    if not Label.query.get(i.idLabel):
        db.session.add(i)
        db.session.commit()
for i in initial_data.get('Kategorie'):
    if not Kategorie.query.get(i.idKategorie):
        db.session.add(i)
        db.session.commit()
for i in initial_data.get('Benutzer'):
    if not Benutzer.query.get(i.benutzername):
        db.session.add(i)
        db.session.commit()
for i in initial_data.get('AuslagenKategorie'):
    if not AuslagenKategorie.query.get(i.idAuslKateg):
        db.session.add(i)
        db.session.commit()
