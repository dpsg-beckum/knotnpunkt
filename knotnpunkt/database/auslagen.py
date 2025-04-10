from __future__ import annotations

import base64
from datetime import datetime as dt
from typing import List, Optional, Type, TypeVar

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import BaseTable, Benutzer, db
from .exceptions import (ElementAlreadyExists, ElementDoesNotExsist,
                         ElementNotEditable)


class AuslagenKategorie(BaseTable):
    __tablename__ = "AuslagenKategorie"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    anzeigeName: Mapped[str] = mapped_column(String(), nullable=False)

    @staticmethod
    def create_new(id, name, anzeigeName) -> AuslagenKategorie:
        if db.session.query(AuslagenKategorie).filter_by(id=id).first():
            raise ElementAlreadyExists(
                f"AuslagenKategorie mit der ID \"{id}\" existiert bereits")
        if db.session.query(AuslagenKategorie).filter_by(name=name).first():
            raise ElementAlreadyExists(
                f"AuslagenKategorie mit dem Namen \"{name}\" existiert bereits")

        new_auslagenkategorie = AuslagenKategorie(
            id=id,
            name=name,
            anzeigeName=anzeigeName
        )
        db.session.add(new_auslagenkategorie)
        db.session.commit()
        return new_auslagenkategorie


class AuslagenBild(BaseTable):
    __tablename__ = "AuslagenBild"

    id: Mapped[int] = mapped_column(primary_key=True)
    img: Mapped[str] = mapped_column(String(), nullable=False)
    mimetype: Mapped[str] = mapped_column(String(), nullable=False)

    auslage_id: Mapped[int] = mapped_column(
        ForeignKey('Auslage.id'), nullable=False)

    auslage: Mapped[Auslage] = relationship(
        'Auslage', back_populates="Bild", foreign_keys=auslage_id)

    @property
    def img_base64(self):
        """Embedding an image file into SVG needs the image base64 coded

        Returns:
            str: Base64 code of the img attribute
        """
        return base64.encodebytes(self.img).decode('utf-8')

    @staticmethod
    def create_new(auslage: Auslage, img: str, mimetype: str) -> AuslagenBild:
        new_img = AuslagenBild(
            auslage_id=auslage.id,
            img=img,
            mimetype=mimetype
        )
        db.session.add(new_img)
        db.session.commit()
        return new_img


class Auslage(BaseTable):
    __tablename__ = "Auslage"

    id: Mapped[int] = mapped_column(primary_key=True)
    titel: Mapped[str] = mapped_column(String(45), nullable=False)
    betrag: Mapped[float] = mapped_column(Float(), nullable=False)
    iban: Mapped[str] = mapped_column(String(22), nullable=False)
    bic: Mapped[str] = mapped_column(String(11), nullable=False)
    kontoinhaber: Mapped[str] = mapped_column(String(45), nullable=False)
    grund: Mapped[str] = mapped_column(Text(), nullable=False)
    eingereicht_zeit: Mapped[dt] = mapped_column(DateTime(), nullable=False)
    freigabe_zeit: Mapped[Optional[dt]] = mapped_column(
        DateTime(), nullable=True)

    erledigtZeit: Mapped[Optional[dt]] = mapped_column(
        DateTime(), nullable=True)

    Bild: Mapped[List[AuslagenBild]] = relationship(
        'AuslagenBild', back_populates="auslage", cascade="all, delete-orphan")

    ersteller_id: Mapped[str] = mapped_column(
        ForeignKey('benutzer.benutzername'), nullable=False)
    ersteller: Mapped[Benutzer] = relationship(
        'Benutzer', foreign_keys=ersteller_id)

    freigabeDurch_benutzername: Mapped[Optional[str]] = mapped_column(
        ForeignKey('benutzer.benutzername'), nullable=True)
    Freigebende: Mapped[Optional[Benutzer]] = relationship(
        'Benutzer', foreign_keys=freigabeDurch_benutzername)

    erledigtDurch_benutzername: Mapped[Optional[str]] = mapped_column(
        ForeignKey('benutzer.benutzername'), nullable=True)
    ErledigtDurch: Mapped[Optional[Benutzer]] = relationship(
        'Benutzer', foreign_keys=erledigtDurch_benutzername)

    kategorie_id: Mapped[int] = mapped_column(
        ForeignKey('AuslagenKategorie.id'), nullable=False)
    Kategorie: Mapped[AuslagenKategorie] = relationship(
        'AuslagenKategorie', foreign_keys=kategorie_id)

    def is_deletable(self):
        if self.erledigtDurch_benutzername or \
                self.freigabeDurch_benutzername or \
                self.erledigtZeit or \
                self.freigabe_zeit:
            return False
        return True

    def is_editable(self):
        return self.is_deletable()

    def freigeben(self, benutzer: Benutzer):
        if self.freigabeDurch_benutzername or self.freigabe_zeit:
            raise ValueError(
                f"Auslage \"{self.id}\" wurde bereits freigegeben")
        self.freigabeDurch_benutzername = benutzer.benutzername
        self.freigabe_zeit = dt.now()
        db.session.commit()
        return self

    def erledigen(self, benutzer: Benutzer):
        if self.erledigtDurch_benutzername or self.erledigtZeit:
            raise ValueError(
                f"Auslage \"{self.id}\" wurde bereits erledigt")
        self.erledigtDurch_benutzername = benutzer.benutzername
        self.erledigtZeit = dt.now()
        db.session.commit()
        return self

    @staticmethod
    def create_new(titel: str, betrag: float, iban: str, bic: str, kontoinhaber: str,
                   grund: str, eingereicht_zeit: dt, erstellerBenutzername: str,
                   kategorie: AuslagenKategorie) -> Auslage:

        new_auslage = Auslage(
            titel=titel,
            betrag=betrag,
            iban=iban,
            bic=bic,
            kontoinhaber=kontoinhaber,
            grund=grund,
            eingereicht_zeit=eingereicht_zeit,
            ersteller_id=erstellerBenutzername,
            kategorie_id=kategorie.id
        )
        db.session.add(new_auslage)
        db.session.commit()
        return new_auslage

    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "titel": self.titel,
    #         "betrag": self.betrag,
    #         "iban": self.iban,
    #         "bic": self.bic,
    #         "kontoinhaber": self.kontoinhaber,
    #         "grund": self.grund,
    #         "eingereicht_zeit": self.eingereicht_zeit,
    #         "erstellerBenutzername": self.ersteller_id,
    #         "kategorieId": self.kategorie_id,
    #         "freigabe_zeit": self.freigabe_zeit,
    #         "freigabeDurchBenutzername": self.freigabeDurch_benutzername,
    #         "erledigtZeit": self.erledigtZeit,
    #         "erledigtDurchNutzer": self.erledigtDurch_benutzername
    #     }
