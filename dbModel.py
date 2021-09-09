# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import DATETIME, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Adresse(Base):
    __tablename__ = 'Adresse'

    idAdresse = Column(Integer, primary_key=True)
    straße = Column(String(45), nullable=False)
    hausnummer = Column(String(45))
    postleitzahl = Column(String(45))
    ort = Column(String(45), nullable=False)


class Kategorie(Base):
    __tablename__ = 'Kategorie'

    idKategorie = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    istZaehlbar = Column(String(45), nullable=False)


class Label(Base):
    __tablename__ = 'Label'

    idLabel = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    datentyp = Column(String(45), nullable=False)


class Benutzer(Base):
    __tablename__ = 'Benutzer'

    benutzername = Column(String(45), primary_key=True)
    name = Column(String(45), nullable=False)
    emailAdresse = Column(String(45), nullable=False, unique=True)
    passwort = Column(String(45), nullable=False)
    adresseRef = Column(ForeignKey('Adresse.idAdresse'), nullable=False, index=True)
    authenticated = Column(TINYINT(1), nullable=False)

    Adresse = relationship('Adresse')


class Standarteigenschaft(Base):
    __tablename__ = 'Standarteigenschaft'

    Kategorie_idKategorie = Column(ForeignKey('Kategorie.idKategorie'), primary_key=True, nullable=False, index=True)
    Label_idLabel = Column(ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = Column(String(45))
    wertString = Column(String(45))
    wertBool = Column(String(45))

    Kategorie = relationship('Kategorie')
    Label = relationship('Label')


class Aktion(Base):
    __tablename__ = 'Aktion'

    idAktion = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    beginn = Column(DATETIME(fsp=4), nullable=False)
    ende = Column(DATETIME(fsp=4), nullable=False)
    ansprechpartnerRef = Column(ForeignKey('Benutzer.benutzername'), nullable=False, index=True)
    Adresse_idAdresse = Column(ForeignKey('Adresse.idAdresse'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')


class Lager(Base):
    __tablename__ = 'Lager'

    idLager = Column(Integer, primary_key=True)
    adresseRef = Column(ForeignKey('Adresse.idAdresse'), nullable=False, index=True)
    ansprechpartnerRef = Column(ForeignKey('Benutzer.benutzername'), nullable=False, index=True)

    Adresse = relationship('Adresse')
    Benutzer = relationship('Benutzer')


class Material(Base):
    __tablename__ = 'Material'

    idMaterial = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    Kategorie_idKategorie = Column(ForeignKey('Kategorie.idKategorie'), nullable=False, index=True)
    Lager_idLager = Column(ForeignKey('Lager.idLager'), nullable=False, index=True)

    Kategorie = relationship('Kategorie')
    Lager = relationship('Lager')


class Eigenschaft(Base):
    __tablename__ = 'Eigenschaft'

    Material_idMaterial = Column(ForeignKey('Material.idMaterial'), primary_key=True, nullable=False, index=True)
    Label_idLabel = Column(ForeignKey('Label.idLabel'), primary_key=True, nullable=False, index=True)
    wertInt = Column(String(45))
    wertString = Column(String(45))
    wertBool = Column(String(45))

    Label = relationship('Label')
    Material = relationship('Material')
