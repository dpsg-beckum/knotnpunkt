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
from knotnpunkt.database.auslagen import AuslagenKategorie
from knotnpunkt.database.db import Benutzer, Rolle
from knotnpunkt.database.material import (KategorieSpezifisch, KategorieTypen,
                                          Set, SetTypes)

a = Rolle.create_new(
    id=1,
    lesenBenutzer=1,
    lesenEinstellungen=1,
    lesenKalender=1,
    lesenMaterial=1,
    name="admin",
    schreibenBenutzer=1,
    schreibenEinstellungen=1,
    schreibenKalender=1,
    schreibenMaterial=1,
    lesenAlleAuslagen=1,
    freigebenAuslagen=0
)

Benutzer.create_new(
    benutzername="admin",
    name="Robert Baden-Powell",
    email="test@dpsg.de",
    passwort="admin",
    rolle=a,
)

Rolle.create_new(
    id=2,
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
    freigebenAuslagen=1)


Rolle.create_new(
    id=3,
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
)
Rolle.create_new(
    id=4,
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
)
Rolle.create_new(
    id=5,
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

AuslagenKategorie.create_new(
    id=1,
    name="gruppenstunden",
    anzeigeName="Gruppenstunden"
)
AuslagenKategorie.create_new(
    id=2,
    name="leiterrunde",
    anzeigeName="Leiterrunde"
)
AuslagenKategorie.create_new(
    id=3,
    name="sommerlager",
    anzeigeName="Sommerlager"
)
AuslagenKategorie.create_new(
    id=4,
    name="sonstiges",
    anzeigeName="Sonstiges"
)


Set.create_new(0, SetTypes.create_new("0", "Kein Set"))
KategorieSpezifisch.create_new(
    "0", "Keine Kategorie", KategorieTypen.create_new("0", "Keine Kategorie"))
