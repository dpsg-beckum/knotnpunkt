import base64
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import DATETIME
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Aktivitaet(db.Model):
    __tablename__ = 'Aktivitaet'
    idAktivitaet = db.Column(db.Integer, primary_key=True)
    MaterialId = db.Column(db.ForeignKey(
        'Material.idMaterial'), nullable=False)
    ausgecheckt = db.Column('ausgecheckt', db.DateTime, nullable=False)
    eingecheckt = db.Column('eingecheckt', db.DateTime, nullable=True)
    menge = db.Column('menge', db.Integer, nullable=False, default=1)
    ersteller_benutzername = db.Column('ersteller_benutzername', db.String(
        45), db.ForeignKey('Benutzer.benutzername'), nullable=False)
    bemerkung = db.Column('bemerkung', db.String(), nullable=True)
    Material = relationship('Material')
    Ersteller = relationship('Benutzer')

    def __init__(self, mat_id, ts_ausgecheckt, menge, benutzer, bemerkung) -> None:
        super().__init__()
        self.MaterialId = mat_id
        self.ausgecheckt = ts_ausgecheckt
        self.menge = menge
        self.ersteller_benutzername = benutzer
        self.bemerkung = bemerkung


class Ausleihe(db.Model):
    __tablename__ = 'Ausleihe'

    idAusleihe = db.Column(db.Integer, primary_key=True)
    ersteller_benutzername = db.Column('Benutzer_benutzername', db.String(
        45), db.ForeignKey('Benutzer.benutzername'), nullable=False, index=True)
    empfaenger = db.Column('empfaenger', db.String(45), nullable=True)
    ts_erstellt = db.Column('ts_erstellt', db.DateTime, nullable=False)
    ts_von = db.Column('ts_von', db.Date, nullable=False)
    ts_bis = db.Column('ts_bis', db.Date, nullable=False)
    beschreibung = db.Column('beschreibung', db.String(), nullable=True)
    materialien = db.Column('materialien', db.String(), nullable=False)
    Ersteller = relationship('Benutzer')

    def __repr__(self) -> str:
        props = {k: v for k, v in self.__dict__.items(
        ) if k in self.__table__.columns.keys()}
        return f"<Ausleihe {props}>"


class Adresse(db.Model):
    __tablename__ = 'Adresse'

    idAdresse = db.Column(db.Integer, primary_key=True)
    straße = db.Column(db.String(45), nullable=False)
    hausnummer = db.Column(db.String(45))
    postleitzahl = db.Column(db.String(45))
    ort = db.Column(db.String(45), nullable=False)

    def __str__(self):
        return f"<Adresse {id}>"


class Kategorie(db.Model):
    __tablename__ = 'Kategorie'

    idKategorie = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    istZaehlbar = db.Column(db.String(45), nullable=False)


class Label(db.Model):
    __tablename__ = 'Label'

    idLabel = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    datentyp = db.Column(db.String(45), nullable=False)


class Benutzer(db.Model):
    __tablename__ = 'Benutzer'

    benutzername = db.Column(db.String(45), primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    emailAdresse = db.Column(db.String(45), nullable=False, unique=True)
    passwort = db.Column(db.String(45), nullable=False)
    iban = db.Column(db.String(25), nullable=True)
    adresseRef = db.Column(db.ForeignKey(
        'Adresse.idAdresse'), nullable=False, index=True)
    rolleRef = db.Column('RolleRef', db.ForeignKey(
        'Rolle.idRolle'), nullable=False, index=True)
    eingeloggt = db.Column(db.Boolean, nullable=False, default=False)
    Adresse = relationship('Adresse')
    Rolle = relationship('Rolle')

    def __init__(self, benutzername, name, emailAdresse, passwort, idRolle, hashPassword=False) -> None:
        super().__init__()
        self.benutzername = benutzername
        self.name = name
        self.emailAdresse = emailAdresse
        self.adresseRef = 1
        self.rolleRef = idRolle
        self.eingeloggt = False
        self.passwort = passwort
        if hashPassword:
            self.passwort = generate_password_hash(passwort)

    def check_passwort(self, pwd: str) -> bool:
        return check_password_hash(self.passwort, pwd)

    def set_passwort(self, neues_passwort: str) -> None:
        self.passwort = generate_password_hash(neues_passwort)

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.eingeloggt

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.benutzername

    def views(self):
        rechte = [key for key, value in self.rechte().items() if value == True]
        ansichten = []
        for r in rechte:
            if "kalender" in r:
                ansichten.append(('Kalender'))
            if "benutzer" in r:
                ansichten.append('Benutzer')
            if "material" in r:
                ansichten.append("Material")
            if "einstellungen" in r:
                ansichten.append("Einstellungen")
        return list(dict.fromkeys(ansichten))

    def rechte(self):
        return {
            'benutzerSchreiben': self.Rolle.schreibenBenutzer,
            'benutzerLesen': self.Rolle.lesenBenutzer,
            'materialSchreiben': self.Rolle.schreibenMaterial,
            'materialLesen': self.Rolle.lesenMaterial,
            'kalenderSchreiben': self.Rolle.schreibenKalender,
            'kalenderLesen': self.Rolle.lesenKalender,
            'einstellungenSchreiben': self.Rolle.schreibenEinstellungen,
            'einstellungenLesen': self.Rolle.lesenEinstellungen}

    def __repr__(self):
        return f"<User {self.benutzername} {self.Rolle.schreibenEinstellungen}>"


class Standarteigenschaft(db.Model):
    __tablename__ = 'Standarteigenschaft'

    Kategorie_idKategorie = db.Column(db.ForeignKey(
        'Kategorie.idKategorie'), primary_key=True, nullable=False, index=True)
    Label_idLabel = db.Column(db.ForeignKey(
        'Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = db.Column(db.String(45))
    wertString = db.Column(db.String(45))
    wertBool = db.Column(db.String(45))

    Kategorie = relationship('Kategorie')
    Label = relationship('Label')


class Aktion(db.Model):
    __tablename__ = 'Aktion'

    idAktion = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    beginn = db.Column(DATETIME(fsp=4), nullable=False)
    ende = db.Column(DATETIME(fsp=4), nullable=False)
    ansprechpartnerRef = db.Column(db.ForeignKey(
        'Benutzer.benutzername'), nullable=False, index=True)
    Adresse_idAdresse = db.Column(db.ForeignKey(
        'Adresse.idAdresse'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')


class Lager(db.Model):
    __tablename__ = 'Lager'

    idLager = db.Column(db.Integer, primary_key=True)
    adresseRef = db.Column(db.ForeignKey(
        'Adresse.idAdresse'), nullable=False, index=True)
    ansprechpartnerRef = db.Column(db.ForeignKey(
        'Benutzer.benutzername'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')


class Material(db.Model):
    __tablename__ = 'Material'
    idMaterial = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    Eigenschaften = db.Column(db.JSON, nullable=True)
    Kategorie_idKategorie = db.Column(db.ForeignKey(
        'Kategorie.idKategorie'), nullable=False, index=True)
    Kategorie = relationship('Kategorie')

    def __init__(self, name, kategorie, eigenschaften) -> None:
        super().__init__()
        self.name = name if name != '' else 'Unbennantes Material'
        self.Kategorie_idKategorie = kategorie
        self.Eigenschaften = eigenschaften


class Rolle(db.Model):
    __tablename__ = 'Rolle'

    idRolle = db.Column("idRolle", db.Integer(), primary_key=True)
    name = db.Column('name', db.String(45), nullable=False, unique=True)
    schreibenKalender = db.Column(
        'schreibenKalender', db.Boolean(), default=False)
    lesenKalender = db.Column('lesenKalender', db.Boolean(), default=False)
    schreibenBenutzer = db.Column(
        'schreibenBenutzer', db.Boolean(), default=False)
    lesenBenutzer = db.Column('lesenBenutzer', db.Boolean(), default=False)
    schreibenMaterial = db.Column(
        'schreibenMaterial', db.Boolean(), default=False)
    lesenMaterial = db.Column('lesenMaterial', db.Boolean(), default=False)
    schreibenEinstellungen = db.Column(
        'schreibenEinstellungen', db.Boolean(), default=False)
    lesenEinstellungen = db.Column(
        'lesenEinstellungen', db.Boolean(), default=False)
    lesenAlleAuslagen = db.Column(
        'lesenAlleAuslagen', db.Boolean(), default=False)
    freigebenAuslagen = db.Column(
        'freigebenAuslagen', db.Boolean(), default=False)

    def __str__(self):
        return f"<Rolle {self.name}>"


class Eigenschaft(db.Model):
    __tablename__ = 'Eigenschaft'

    Material_idMaterial = db.Column(db.ForeignKey(
        'Material.idMaterial'), primary_key=True, nullable=False, index=True)
    Label_idLabel = db.Column(db.ForeignKey(
        'Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = db.Column(db.String(45))
    wertString = db.Column(db.String(45))
    wertBool = db.Column(db.String(45))

    Label = relationship('Label')
    Material = relationship('Material')


class Img(db.Model):
    img_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Material_idMaterial = db.Column(db.ForeignKey(
        'Material.idMaterial'), nullable=False, index=True)
    img = db.Column(db.String(), nullable=False)
    mimetype = db.Column(db.String(), nullable=False)

class AuslagenKategorie(db.Model):
    __tablename__ = "AuslagenKategorie"
    idAuslKateg = db.Column("idAuslKateg", db.Integer(), primary_key=True)
    name = db.Column('name', db.String(45), nullable=False, unique=True)
    anzeigeName = db.Column("anzeigeName", db.String(), nullable=False)


class AuslagenBild(db.Model):
    __tablename__ = "AuslagenBild"
    img_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Auslage_id = db.Column(db.ForeignKey('Auslage.idAuslage'), nullable=False)
    img = db.Column(db.String(), nullable=False)
    mimetype = db.Column(db.String(), nullable=False)

    Auslage = relationship('Auslage', back_populates="Bild")

    @property
    def img_base64(self):
        """Embedding an image file into SVG needs the image base64 coded

        Returns:
            str: Base64 code of the img attribute
        """
        return base64.encodebytes(self.img).decode('utf-8')


class Auslage(db.Model):
    __tablename__ = "Auslage"
    idAuslage = db.Column("idAuslage", db.Integer(), primary_key=True)
    titel = db.Column("titel", db.String(45), nullable=False)
    betrag = db.Column("betrag", db.Float(), nullable=False)
    iban = db.Column("iban", db.String(22), nullable=False)
    bic = db.Column("bic", db.String(11), nullable=False)
    kontoinhaber = db.Column("kontoinhaber", db.String(45), nullable=False)
    grund = db.Column("grund", db.String(), nullable=False)
    eingereicht_zeit = db.Column("eingereicht_zeit", db.DateTime(), nullable=False)
    freigabe_zeit = db.Column("freigabe_zeit", db.DateTime(), nullable=True)
    erstellerBenutzername = db.Column('Ersteller_benutzername', db.String(
        45), db.ForeignKey('Benutzer.benutzername'), nullable=False)
    freigabeDurchBenutzername = db.Column('Freigabe_benutzername', db.String(
        45), db.ForeignKey('Benutzer.benutzername'), nullable=True)
    erledigtZeit = db.Column("erledigt_zeit", db.DateTime(), nullable=True)
    erledigtDurchNutzer = db.Column('Erledigt_benutzername', db.String(
        45), db.ForeignKey('Benutzer.benutzername'), nullable=True)
    kategorieId = db.Column('AuslagenKategorie_idAuslKateg', db.Integer(), db.ForeignKey('AuslagenKategorie.idAuslKateg'))

    Ersteller = relationship('Benutzer', foreign_keys=erstellerBenutzername, backref="Auslagen")
    Freigebende = relationship('Benutzer', foreign_keys=freigabeDurchBenutzername)
    ErledigtDurch = relationship('Benutzer', foreign_keys=erledigtDurchNutzer)
    Kategorie = relationship('AuslagenKategorie')
    Bild = relationship('AuslagenBild', back_populates="Auslage")

    def __init__(self, titel, betrag, iban, bic, kontoinhaber, grund, eingereicht_zeit, erstellerBenutzername, kategorieId):
        self.titel = titel
        self.betrag = betrag
        self.iban = iban
        self.bic = bic
        self.kontoinhaber = kontoinhaber
        self.grund = grund
        self.eingereicht_zeit = eingereicht_zeit
        self.erstellerBenutzername = erstellerBenutzername
        self.kategorieId = kategorieId

    def to_dict(self):
        return {
            "idAuslage": self.idAuslage,
            "titel": self.titel,
            "betrag": self.betrag,
            "iban": self.iban,
            "bic": self.bic,
            "kontoinhaber": self.kontoinhaber,
            "grund": self.grund,
            "eingereicht_zeit": self.eingereicht_zeit,
            "erstellerBenutzername": self.erstellerBenutzername,
            "kategorieId": self.kategorieId,
            "freigabe_zeit": self.freigabe_zeit,
            "freigabeDurchBenutzername": self.freigabeDurchBenutzername,
            "erledigtZeit": self.erledigtZeit,
            "erledigtDurchNutzer": self.erledigtDurchNutzer
        }