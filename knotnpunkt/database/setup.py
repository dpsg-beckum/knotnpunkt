from .db import (
    Benutzer,
    Rolle,
    Label,
    Kategorie,
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
            schreibenMaterial=1
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
            schreibenMaterial=1
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
            schreibenMaterial=1
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
            schreibenMaterial=1
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
    ]
}
