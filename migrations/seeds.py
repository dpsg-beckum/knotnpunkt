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
from knotnpunkt.database.db import Benutzer, Rechte, Rolle
from knotnpunkt.database.material import (KategorieSpezifisch, KategorieTypen,
                                          Material, Set, SetTypes)

r_benutzer_lesen = Rechte.create_new(
    id=1, name="lesenBenutzer", beschreibung="Benutzer lesen")

r_benutzer_schreiben = Rechte.create_new(
    id=2, name="schreibenBenutzer", beschreibung="Benutzer schreiben")

r_einstellungen_lesen = Rechte.create_new(
    id=3, name="lesenEinstellungen", beschreibung="Einstellungen lesen")

r_einstellungen_schreiben = Rechte.create_new(
    id=4, name="schreibenEinstellungen", beschreibung="Einstellungen schreiben")

r_kalender_lesen = Rechte.create_new(
    id=5, name="lesenKalender", beschreibung="Kalender lesen")

r_kalender_schreiben = Rechte.create_new(
    id=6, name="schreibenKalender", beschreibung="Kalender schreiben")

r_material_lesen = Rechte.create_new(
    id=7, name="lesenMaterial", beschreibung="Material lesen")

r_material_schreiben = Rechte.create_new(
    id=8, name="schreibenMaterial", beschreibung="Material schreiben")

r_auslagen_erstellen = Rechte.create_new(
    id=9, name="erstelleAuslagen", beschreibung="Eigene Auslagen erstellen")

r_auslagen_lesen = Rechte.create_new(
    id=10, name="lesenAlleAuslagen", beschreibung="Alle Auslagen lesen")

r_auslagen_freigeben = Rechte.create_new(
    id=11, name="freigebenAuslagen", beschreibung="Auslagen freigeben")

r_auslagen_schreiben = Rechte.create_new(
    id=12, name="SchreibenAlleAuslagen", beschreibung="Alle Auslagen bearbeiten")


admin = Rolle.create_new(id=1, name="admin")
admin.add_recht(r_benutzer_lesen)
admin.add_recht(r_benutzer_schreiben)
admin.add_recht(r_einstellungen_lesen)
admin.add_recht(r_einstellungen_schreiben)
admin.add_recht(r_kalender_lesen)
admin.add_recht(r_kalender_schreiben)
admin.add_recht(r_material_lesen)
admin.add_recht(r_material_schreiben)
admin.add_recht(r_auslagen_erstellen)
# admin.add_recht(r_auslagen_lesen)
# admin.add_recht(r_auslagen_freigeben)
# admin.add_recht(r_auslagen_schreiben)

Benutzer.create_new(
    benutzername="admin",
    name="Robert Baden-Powell",
    email="test@dpsg.de",
    passwort="admin",
    rolle=admin,
)


stavo = Rolle.create_new(id=2, name="stavo")
stavo.add_recht(r_benutzer_lesen)
stavo.add_recht(r_benutzer_schreiben)
stavo.add_recht(r_einstellungen_lesen)
# stavo.add_recht(r_einstellungen_schreiben)
stavo.add_recht(r_kalender_lesen)
stavo.add_recht(r_kalender_schreiben)
stavo.add_recht(r_material_lesen)
stavo.add_recht(r_material_schreiben)
stavo.add_recht(r_auslagen_erstellen)
stavo.add_recht(r_auslagen_lesen)
stavo.add_recht(r_auslagen_freigeben)
# stavo.add_recht(r_auslagen_schreiben)


leiter = Rolle.create_new(id=3, name="leiter")
# leiter.add_recht(r_benutzer_lesen)
# leiter.add_recht(r_benutzer_schreiben)
# leiter.add_recht(r_einstellungen_lesen)
# leiter.add_recht(r_einstellungen_schreiben)
leiter.add_recht(r_kalender_lesen)
leiter.add_recht(r_kalender_schreiben)
leiter.add_recht(r_material_lesen)
leiter.add_recht(r_material_schreiben)
leiter.add_recht(r_auslagen_erstellen)
# leiter.add_recht(r_auslagen_lesen)
# leiter.add_recht(r_auslagen_freigeben)
# leiter.add_recht(r_auslagen_schreiben)


api = Rolle.create_new(id=4, name="api")
api.add_recht(r_benutzer_lesen)
api.add_recht(r_benutzer_schreiben)
api.add_recht(r_einstellungen_lesen)
api.add_recht(r_einstellungen_schreiben)
api.add_recht(r_kalender_lesen)
api.add_recht(r_kalender_schreiben)
api.add_recht(r_material_lesen)
api.add_recht(r_material_schreiben)
api.add_recht(r_auslagen_erstellen)
api.add_recht(r_auslagen_lesen)
api.add_recht(r_auslagen_freigeben)
api.add_recht(r_auslagen_schreiben)


kassenwart = Rolle.create_new(id=5, name="kassenwart")
# kassenwart.add_recht(r_benutzer_lesen)
# kassenwart.add_recht(r_benutzer_schreiben)
# kassenwart.add_recht(r_einstellungen_lesen)
# kassenwart.add_recht(r_einstellungen_schreiben)
kassenwart.add_recht(r_kalender_lesen)
kassenwart.add_recht(r_kalender_schreiben)
kassenwart.add_recht(r_material_lesen)
kassenwart.add_recht(r_material_schreiben)
kassenwart.add_recht(r_auslagen_erstellen)
kassenwart.add_recht(r_auslagen_lesen)
# kassenwart.add_recht(r_auslagen_freigeben)
kassenwart.add_recht(r_auslagen_schreiben)


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

# TODO Demo
if True:
    t8 = SetTypes.create_new("8", "Achter")
    t6 = SetTypes.create_new("6", "Sechser")
    tG6 = SetTypes.create_new("G6", "Geknüpfter Sechser")
    tK = SetTypes.create_new("K", "Khote")
    tS = SetTypes.create_new("S", "Sudan")
    tI = SetTypes.create_new("I", "Igel")
    tC = SetTypes.create_new("C", "Küche")

    Set.create_new(number=1,
                   name="Neue Jurte",
                   description="Eine nagelneue Jurte",
                   setType=t8)
    Set.create_new(number=2, setType=t8)
    Set.create_new(number=1, setType=t6)
    Set.create_new(number=2, setType=t6)
    Set.create_new(number=1, setType=tG6)
    Set.create_new(number=1, setType=tK)
    Set.create_new(number=1, setType=tS)
    Set.create_new(number=1, setType=tI)
    Set.create_new(number=1, setType=tC)

    k = KategorieTypen.create_new("S", "Seitenbahn")
    KategorieSpezifisch.create_new("E", "Einzel", k)
    KategorieSpezifisch.create_new("D", "Doppel", k)
    k = KategorieTypen.create_new("F", "Fensterbahn")
    KategorieSpezifisch.create_new("E", "Einzel", k)
    KategorieSpezifisch.create_new("D", "Doppel", k)
    k = KategorieTypen.create_new("E", "Erdbahn")
    KategorieSpezifisch.create_new("E", "Einzel", k)
    KategorieSpezifisch.create_new("D", "Doppel", k)
    k = KategorieTypen.create_new("D", "Dreiecksbahn")
    KategorieSpezifisch.create_new("O", "Ohne", k)
    KategorieSpezifisch.create_new("K", "Kurz", k)
    KategorieSpezifisch.create_new("M", "Mittel", k)
    KategorieSpezifisch.create_new("L", "Lang", k)
    k = KategorieTypen.create_new("B", "Bodenplane")
    KategorieSpezifisch.create_new("I", "Igel", k)
    KategorieSpezifisch.create_new("S", "Sudan", k)
    KategorieSpezifisch.create_new("J", "Jurte", k)
    KategorieSpezifisch.create_new("K", "Khote", k)
    KategorieSpezifisch.create_new("P", "Pfusch", k)
    k = KategorieTypen.create_new("P", "Stange")
    KategorieSpezifisch.create_new("M", "Mittelstange", k)
    KategorieSpezifisch.create_new("S", "Seitenstange", k)
    KategorieSpezifisch.create_new("E", "Eingangsstange", k)
    KategorieSpezifisch.create_new("V", "Igel-Eingang", k)
    k = KategorieTypen.create_new("K", "Komplettdach")
    KategorieSpezifisch.create_new("6", "6er Dach", k)
    KategorieSpezifisch.create_new("8", "8er Dach", k)
    k = KategorieTypen.create_new("T", "Teaterbahn")
    KategorieSpezifisch.create_new("-", "-", k)

    s = Set.get_via_code("1-8")
    ks = KategorieSpezifisch.get_via_code("S-D")
    for i in range(2):
        Material.create_new("", ks, None, "Testmaterial", s)

    ks = KategorieSpezifisch.get_via_code("P-S")
    for i in range(1):
        Material.create_new("", ks, None, "Testmaterial", s)

    ks = KategorieSpezifisch.get_via_code("P-M")
    for i in range(1):
        Material.create_new("", ks, None, "Testmaterial", s)

    ks = KategorieSpezifisch.get_via_code("K-8")
    for i in range(1):
        Material.create_new("", ks, None, "Testmaterial", s)
