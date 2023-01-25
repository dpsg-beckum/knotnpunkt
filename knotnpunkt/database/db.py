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
    adresseRef = db.Column(db.ForeignKey(
        'Adresse.idAdresse'), nullable=False, index=True)
    rolleRef = db.Column('RolleRef', db.ForeignKey(
        'Rolle.idRolle'), nullable=False, index=True)
    eingeloggt = db.Column(db.Boolean, nullable=False, default=False)
    Adresse = relationship('Adresse')
    Rolle = relationship('Rolle')

    def __init__(self, benutzername, name, emailAdresse, passwort, idRolle) -> None:
        super().__init__()
        self.benutzername = benutzername
        self.name = name
        self.emailAdresse = emailAdresse
        self.passwort = generate_password_hash(passwort)
        self.adresseRef = 1
        self.rolleRef = idRolle
        self.eingeloggt = False

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
        'Material.idMaterial'), primary_key=True, nullable=False, index=True)
    img = db.Column(db.String(), nullable=False)
    mimetype = db.Column(db.String(), nullable=False)
