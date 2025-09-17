from __future__ import annotations

from datetime import datetime as dt
from typing import List, Optional, Type, TypeVar

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import BaseTable, Benutzer, db
from .exceptions import (ElementAlreadyExists, ElementDoesNotExsist,
                         ElementNotEditable)

"""
Tabellen für Materialverwaltung
"""


class Aktivitaet(BaseTable):
    __tablename__ = 'aktivitaet'
    id: Mapped[int] = mapped_column(primary_key=True)
    MaterialId: Mapped[int] = mapped_column(
        ForeignKey('material.id'), nullable=False)
    ausgecheckt: Mapped[dt] = mapped_column(DateTime, nullable=False)
    eingecheckt: Mapped[Optional[dt]] = mapped_column(DateTime)
    menge: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ersteller_benutzername: Mapped[str] = mapped_column(
        ForeignKey('benutzer.benutzername'), nullable=False)
    bemerkung: Mapped[Optional[str]] = mapped_column(String)

    Material: Mapped[Material] = relationship('Material')
    Ersteller: Mapped[Benutzer] = relationship('Benutzer')

    @staticmethod
    def create_new(material: Material,
                   ersteller: Benutzer,
                   menge: int,
                   bemerkung: str | None = None
                   ) -> Aktivitaet:

        new_aktivitaet = Aktivitaet(
            MaterialId=material.id,
            ausgecheckt=dt.now(),
            eingecheckt=None,
            menge=menge,
            ersteller_benutzername=ersteller.benutzername,
            bemerkung=bemerkung
        )
        db.session.add(new_aktivitaet)
        db.session.commit()
        return new_aktivitaet


class Ausleihe(BaseTable):
    __tablename__ = 'ausleihe'

    id: Mapped[int] = mapped_column(primary_key=True)
    ersteller_benutzername: Mapped[str] = mapped_column(
        ForeignKey('benutzer.benutzername'), nullable=False, index=True)
    empfaenger: Mapped[Optional[str]] = mapped_column(String(45))
    ts_erstellt: Mapped[dt] = mapped_column(DateTime, nullable=False)
    ts_von: Mapped[dt] = mapped_column(Date, nullable=False)
    ts_bis: Mapped[dt] = mapped_column(Date, nullable=False)
    beschreibung: Mapped[Optional[str]] = mapped_column(String)
    materialien: Mapped[str] = mapped_column(String, nullable=False)

    Ersteller: Mapped[Benutzer] = relationship('Benutzer')

    @staticmethod
    def create_new(ersteller: Benutzer,
                   empfaenger: str,
                   ts_von: dt,
                   ts_bis: dt,
                   beschreibung: str,
                   materialien: str) -> Ausleihe:
        new_ausleihe = Ausleihe(
            ersteller_benutzername=ersteller.benutzername,
            empfaenger=empfaenger,
            ts_erstellt=dt.now(),
            ts_von=ts_von,
            ts_bis=ts_bis,
            beschreibung=beschreibung,
            materialien=materialien
        )
        db.session.add(new_ausleihe)
        db.session.commit()
        return new_ausleihe

    def __repr__(self) -> str:
        props = {k: v for k, v in self.__dict__.items(
        ) if k in self.__table__.columns.keys()}
        return f"<Ausleihe {props}>"


class SetTypes(BaseTable):
    """
    Speichert die Typen von Sets
    """

    __tablename__ = 'settypes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kuerzel: Mapped[str] = mapped_column(String(45), nullable=False)
    name: Mapped[str] = mapped_column(String(45), nullable=False)

    sets: Mapped[List[Set]] = relationship('Set', back_populates="setType")

    @staticmethod
    def create_new(kuerzel: str, name: str) -> SetTypes:
        new_set_types = SetTypes(
            kuerzel=kuerzel,
            name=name
        )
        db.session.add(new_set_types)
        db.session.commit()
        return new_set_types

    @staticmethod
    def get_via_kuerzel(kuerzel: str) -> SetTypes:
        """
        Get a SetTypes instance by its kuerzel.
        """
        set_type = db.session.query(
            SetTypes).filter_by(kuerzel=kuerzel).first()
        if not set_type:
            raise ElementDoesNotExsist(
                f"SetType mit kuerzel \"{kuerzel}\" existiert nicht")
        return set_type


class Set(BaseTable):
    """
    Speichert die Sets
    """

    __tablename__ = 'set'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    setType_id: Mapped[int] = mapped_column(
        ForeignKey('settypes.id'), nullable=False)
    setType: Mapped[SetTypes] = relationship('SetTypes')

    materials: Mapped[List[Material]] = relationship(
        'Material', back_populates="set")

    @staticmethod
    def create_new(number: int, setType: SetTypes) -> Set:
        number = int(number)

        if not isinstance(setType, SetTypes):
            raise TypeError("setType muss ein SetTypes Objekt sein")

        existing_sets = Set.filter_by(setType_id=setType.id)
        if existing_sets:
            for s in existing_sets:
                if s.number == number:
                    raise ElementAlreadyExists(
                        f"Set mit der Nummer \"{number}\" existiert bereits")

        new_set = Set(
            number=number,
            setType_id=setType.id
        )
        db.session.add(new_set)
        db.session.commit()
        return new_set

    @property
    def name(self) -> str:
        return f"{self.number}.{self.setType.kuerzel}"

    @staticmethod
    def get_via_number(number: int, setType: SetTypes) -> Set:
        """
        Get a Set instance by its number and type.
        """
        if not isinstance(setType, SetTypes):
            raise TypeError("setType muss ein SetTypes Objekt sein")

        set_instance = db.session.query(Set).filter_by(
            number=number, setType_id=setType.id).first()
        if not set_instance:
            raise ElementDoesNotExsist(
                f"Set mit Nummer \"{number}\" und Typ \"{setType.kuerzel}\" existiert nicht")

        return set_instance

    @staticmethod
    def get_via_code(code: str) -> Set:
        """
        Get a Set instance by its code.
        eg. "1-8" for Set with number 1 and type 8.
        """
        code = code.split("-")
        if len(code) != 2:
            raise ValueError("Code must be in the format 'Number-Type'")

        number, typ = code
        set_type = SetTypes.get_via_kuerzel(typ)
        return Set.get_via_number(int(number), set_type)


class KategorieTypen(BaseTable):
    """
    Kategorisiert die Typen von Materialien
    e.g. Seitenbahn, Fensterbahn, Bodenplane, Stange, Komplettdach ...
    """

    __tablename__ = 'kategorietypen'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kuerzel: Mapped[str] = mapped_column(String(45), nullable=False)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    spezifizierer: Mapped[str] = mapped_column(String(45))

    spezifisch: Mapped[List[KategorieSpezifisch]] = relationship(
        "KategorieSpezifisch", back_populates="kategorie_typen")

    @staticmethod
    def create_new(kuerzel: str, name: str, spezifizierer: str = "") -> KategorieTypen:
        if db.session.query(KategorieTypen).filter_by(kuerzel=kuerzel).first():
            raise ElementAlreadyExists(
                f"KategorieTypen mit kuerzel \"{kuerzel}\" existiert bereits")

        new_kategorie_typen = KategorieTypen(
            kuerzel=kuerzel,
            name=name,
            spezifizierer=spezifizierer
        )
        db.session.add(new_kategorie_typen)
        db.session.commit()
        return new_kategorie_typen

    @staticmethod
    def get_via_kuerzel(kuerzel: str) -> KategorieTypen:
        """
        Get a KategorieTypen instance by its kuerzel.
        """
        kategorie_typen = db.session.query(
            KategorieTypen).filter_by(kuerzel=kuerzel).first()
        if not kategorie_typen:
            raise ElementDoesNotExsist(
                f"KategorieTypen mit kuerzel \"{kuerzel}\" existiert nicht")
        return kategorie_typen


class KategorieSpezifisch(BaseTable):
    """
    Kategorisiert die spezifischen Kategorien
    e.g. *-Einzel, *-Doppel, *-Kurz ...
    """

    __tablename__ = 'kategoriespezifisch'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    kuerzel: Mapped[str] = mapped_column(String(45), nullable=False)

    kategorie_typen_id: Mapped[int] = mapped_column(
        ForeignKey("kategorietypen.id"), nullable=False)
    kategorie_typen: Mapped[KategorieTypen] = relationship(
        "KategorieTypen", back_populates="spezifisch")

    material: Mapped[List[Material]] = relationship(
        "Material", back_populates="spezifisch")

    @staticmethod
    def create_new(kuerzel: str, name: str, typ: KategorieTypen) -> KategorieSpezifisch:
        if not isinstance(typ, KategorieTypen):
            raise TypeError("typ muss ein KategorieTypen Objekt sein")
        if db.session.query(KategorieSpezifisch).filter_by(
                kuerzel=kuerzel, kategorie_typen_id=typ.id).first():
            raise ElementAlreadyExists(
                f"KategorieSpezifisch mit kuerzel \"{kuerzel}\" existiert bereits")

        new_kategorie_spezifisch = KategorieSpezifisch(
            kuerzel=kuerzel,
            name=name,
            kategorie_typen_id=typ.id
        )
        db.session.add(new_kategorie_spezifisch)
        db.session.commit()
        return new_kategorie_spezifisch

    def to_dict(self, depth: int = 1, _visited: set[int] | None = None) -> dict:
        if _visited is None:
            _visited = set()
        if id(self) in _visited:
            return {}
        _visited.add(id(self))

        data = {
            "id": self.id,
            "name": self.name,
            "kuerzel": self.kuerzel,
        }
        # Force serialize kategorie_typen regardless of depth
        data["kategorie_typen"] = self.kategorie_typen.to_dict(
            depth=max(depth, 1), _visited=_visited)
        # Optionally, if you need to include materials too:
        data["material"] = [
            m.to_dict(depth=max(depth, 1), _visited=_visited) for m in self.material]
        return data

    @staticmethod
    def get_via_kuerzel(kuerzel: str, typ: KategorieTypen) -> KategorieSpezifisch:
        """
        Get a KategorieSpezifisch instance by its kuerzel.
        """
        if not isinstance(typ, KategorieTypen):
            raise TypeError("typ muss ein KategorieTypen Objekt sein")

        print(
            f"Searching for KategorieSpezifisch with kuerzel: {kuerzel} and typ: {typ.kuerzel}")

        kategorie_spezifisch = db.session.query(KategorieSpezifisch).filter_by(
            kuerzel=kuerzel, kategorie_typen_id=typ.id).first()
        print(kategorie_spezifisch)
        if not kategorie_spezifisch:
            raise ElementDoesNotExsist(
                f"KategorieSpezifisch mit kuerzel \"{kuerzel}\" existiert nicht")
        return kategorie_spezifisch

    @staticmethod
    def get_via_code(code: str) -> KategorieSpezifisch:
        """
        Get a KategorieSpezifisch instance by its code.
        eg. "S-E" for Seitenbahn-Einzel.
        """
        code = code.split("-")
        if len(code) != 2:
            raise ValueError(
                "Code must be in the format 'Kuerzel-Spezifizierer'")
        typ, spezifizierer = code

        kategorie_typen = KategorieTypen.get_via_kuerzel(typ)
        return KategorieSpezifisch.get_via_kuerzel(
            spezifizierer, kategorie_typen)


class Material(BaseTable):
    """
    Beschreibung eines kleinstes Materials
    """
    __tablename__ = 'material'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    eigenschaften: Mapped[Optional[dict]] = mapped_column(JSON)

    spezifisch_id: Mapped[int] = mapped_column(
        ForeignKey('kategoriespezifisch.id'), nullable=False)
    spezifisch: Mapped[KategorieSpezifisch] = relationship(
        'KategorieSpezifisch', back_populates="material")

    set_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('set.id'), nullable=True)
    set: Mapped[Optional[Set]] = relationship(
        'Set', back_populates="materials")

    imgs: Mapped[List[Img]] = relationship('Img')

    numberinset: Mapped[Optional[int]] = mapped_column(Integer)

    @staticmethod
    def create_new(name: str,
                   kategorie: KategorieSpezifisch,
                   eigenschaften: dict | None = None,
                   description: str | None = None,
                   set: Set | None = None
                   ) -> Material:

        if len(name) < 1 and kategorie:
            name = kategorie.name + " " + kategorie.kategorie_typen.name

        if eigenschaften is None:
            eigenschaften = {}
        if not isinstance(eigenschaften, dict):
            raise TypeError("eigenschaften must be a dictionary")

        new_material = Material(
            name=name,
            eigenschaften=dict(eigenschaften),
            description=description,
            spezifisch_id=kategorie.id if kategorie else None,
            set_id=set.id if set else None
        )
        db.session.add(new_material)
        db.session.commit()
        return new_material

    def is_editable(self) -> bool:
        # For example, Material instances are editable.
        return True

    def add_to_set(self, set: Set) -> None:
        sid = set.id if set else Set.get_via_id(1).id
        self.set_id = sid
        db.session.commit()

    def set_kategorie(self, kategorie: KategorieSpezifisch) -> None:
        self.spezifisch_id = kategorie.id
        db.session.commit()


class Img(BaseTable):
    __tablename__ = 'img'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey('material.id'), nullable=False)
    img: Mapped[str] = mapped_column(String, nullable=False)
    mimetype: Mapped[str] = mapped_column(String, nullable=False)

    @staticmethod
    def create_new(material: Material, img: str, mimetype: str) -> Img:
        new_img = Img(
            material_id=material.id,
            img=img,
            mimetype=mimetype
        )
        db.session.add(new_img)
        db.session.commit()
        return new_img

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()
