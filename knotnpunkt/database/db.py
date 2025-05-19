from __future__ import annotations

from logging import debug
from typing import List, Optional, Type, TypeVar

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .exceptions import (ElementAlreadyExists, ElementDoesNotExsist,
                         ElementNotEditable)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


T = TypeVar('T', bound='BaseTable')


class BaseTable(Base):
    __abstract__ = True

    def is_editable(self) -> bool:
        """
        Must be implemented in each model.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement is_editable()")

    def update(self, **kwargs):
        debug(f"Updating {self.__class__.__name__} with {kwargs}")

        try:
            if not self.is_editable():
                raise ElementNotEditable(
                    f"{self.__class__.__name__} kann nicht bearbeitet werden")
        except NotImplementedError:
            raise ElementNotEditable(
                f"{self.__class__.__name__} is not editable (is_editable not implemented)")

        mapper = self.__mapper__
        relationships = mapper.relationships.keys()

        for key in kwargs:
            if not hasattr(self, key):
                raise AttributeError(
                    f"{self.__class__.__name__} has no attribute '{key}'")

            # Prevent updating relationship attributes (like `Kategorie`)
            if key in relationships:
                raise ElementNotEditable(
                    f"Relationship attribute '{key}' is not editable directly. Use the foreign key column instead.")

        for key, value in kwargs.items():
            setattr(self, key, value)

        db.session.commit()
        return self

    def is_deletable(self) -> bool:
        """
        Returns if the element can be deleted
        """
        raise NotImplementedError("is_deletable() must be implemented")

    def delete(self):
        if not self.is_deletable():
            raise ValueError(
                f"{str(self.__class__.__name__).replace('Table', '')} \"{self.id}\" is not deletable")
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def filter_by(cls: Type[T], **kwargs) -> List[T]:
        return db.session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def get_all(cls: Type[T]) -> List[T]:
        return db.session.query(cls).all()

    @classmethod
    def get_via_id(cls: Type[T], id_value: int) -> T:
        item = db.session.get(cls, id_value)
        if not item:
            raise ElementDoesNotExsist(
                f"{str(cls.__name__).replace('Table', '')} mit der ID \"{id_value}\" existiert nicht")
        return item

    def to_dict(self, depth: int = 2, _visited: set[int] | None = None) -> dict:
        if _visited is None:
            _visited = set()

        # Only check for cycles in the current recursion path.
        if id(self) in _visited:
            # Instead of returning an empty dict, you might return a minimal representation.
            return {"id": getattr(self, "id", None)}

        _visited.add(id(self))
        data = {}

        # Serialize columns
        mapper = self.__mapper__
        for column in mapper.columns:
            data[column.key] = getattr(self, column.key)

        # Serialize relationships if depth allows
        if depth > 0:
            for rel in mapper.relationships:
                rel_val = getattr(self, rel.key)
                if rel_val is None:
                    data[rel.key] = None
                elif isinstance(rel_val, list):
                    data[rel.key] = [
                        item.to_dict(depth=depth - 1, _visited=_visited.copy())
                        for item in rel_val
                    ]
                else:
                    data[rel.key] = rel_val.to_dict(
                        depth=depth - 1, _visited=_visited.copy())

        _visited.remove(id(self))
        return data


"""
Tabellen für Nutzerverwaltung
"""


class Rolle(BaseTable):
    """
    1:n to Benutzer
    """

    __tablename__ = 'rolle'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    schreibenKalender: Mapped[bool] = mapped_column(Boolean, default=False)
    lesenKalender: Mapped[bool] = mapped_column(Boolean, default=False)
    schreibenBenutzer: Mapped[bool] = mapped_column(Boolean, default=False)
    lesenBenutzer: Mapped[bool] = mapped_column(Boolean, default=False)
    schreibenMaterial: Mapped[bool] = mapped_column(Boolean, default=False)
    lesenMaterial: Mapped[bool] = mapped_column(Boolean, default=False)
    schreibenEinstellungen: Mapped[bool] = mapped_column(
        Boolean, default=False)
    lesenEinstellungen: Mapped[bool] = mapped_column(Boolean, default=False)
    lesenAlleAuslagen: Mapped[bool] = mapped_column(Boolean, default=False)
    freigebenAuslagen: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self):
        return f"<Rolle {self.name}>"

    @staticmethod
    def get_via_name(name: str) -> Rolle:
        item = db.session.query(Rolle).get({"name": name})
        if not item:
            raise ElementDoesNotExsist(
                f"{str(Rolle.__name__)} mit dem Namen \"{name}\" existiert nicht")
        return item

    @staticmethod
    def create_new(
        id: int,
        name: str,
        schreibenKalender: bool,
        lesenKalender: bool,
        schreibenBenutzer: bool,
        lesenBenutzer: bool,
        schreibenMaterial: bool,
        lesenMaterial: bool,
        schreibenEinstellungen: bool,
        lesenEinstellungen: bool,
        lesenAlleAuslagen: bool,
        freigebenAuslagen: bool
    ) -> Rolle:
        if db.session.query(Rolle).filter_by(name=name).first():
            raise ElementAlreadyExists(
                f"Rolle mit dem Namen \"{name}\" existiert bereits")

        new_rolle = Rolle(
            id=id,
            name=name,
            schreibenKalender=schreibenKalender,
            lesenKalender=lesenKalender,
            schreibenBenutzer=schreibenBenutzer,
            lesenBenutzer=lesenBenutzer,
            schreibenMaterial=schreibenMaterial,
            lesenMaterial=lesenMaterial,
            schreibenEinstellungen=schreibenEinstellungen,
            lesenEinstellungen=lesenEinstellungen,
            lesenAlleAuslagen=lesenAlleAuslagen,
            freigebenAuslagen=freigebenAuslagen
        )
        db.session.add(new_rolle)
        db.session.commit()
        return new_rolle


class Benutzer(UserMixin, BaseTable):
    """
    Benutzer Tabelle
    """

    __tablename__ = 'benutzer'

    benutzername: Mapped[str] = mapped_column(String(45), primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    emailAdresse: Mapped[str] = mapped_column(String(255), nullable=True)
    passwort: Mapped[str] = mapped_column(String(45), nullable=False)
    iban: Mapped[Optional[str]] = mapped_column(String(25))
    strasse: Mapped[Optional[str]] = mapped_column(String(45))
    hausnummer: Mapped[Optional[str]] = mapped_column(String(45))
    postleitzahl: Mapped[Optional[str]] = mapped_column(String(45))
    ort: Mapped[Optional[str]] = mapped_column(String(45))

    rolle_id: Mapped[Optional[int]] = mapped_column(ForeignKey('rolle.id'))
    Rolle: Mapped[Optional[Rolle]] = relationship('Rolle')

    def checkPassword(self, password: str) -> bool:
        return check_password_hash(self.passwort, password)

    def set_passwort(self, neues_passwort: str) -> None:
        self.passwort = generate_password_hash(neues_passwort)
        db.session.commit()

    def update(self, name: str = None, emailAdresse: str = None, passwort: str = None, rolle: Rolle = None):
        if name:
            self.name = name
        if emailAdresse:
            self.emailAdresse = emailAdresse
        if passwort:
            self.set_passwort(passwort)
        if rolle:
            self.rolle_id = rolle.id
        db.session.commit()
        return self

    def is_active(self) -> bool:
        return True

    def get_id(self) -> str | None:
        return self.benutzername

    def views(self) -> list[str]:
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

    def rechte(self) -> dict[str, bool]:
        return {
            'benutzerSchreiben': self.Rolle.schreibenBenutzer,
            'benutzerLesen': self.Rolle.lesenBenutzer,
            'materialSchreiben': self.Rolle.schreibenMaterial,
            'materialLesen': self.Rolle.lesenMaterial,
            'kalenderSchreiben': self.Rolle.schreibenKalender,
            'kalenderLesen': self.Rolle.lesenKalender,
            'einstellungenSchreiben': self.Rolle.schreibenEinstellungen,
            'einstellungenLesen': self.Rolle.lesenEinstellungen}

    @classmethod
    def get_via_id(self, benutzername: int) -> Benutzer:
        item = db.session.query(self).get({"benutzername": benutzername})
        if not item:
            raise ElementDoesNotExsist(
                f"{str(self.__name__)} mit dem Benutzernamen \"{benutzername}\" existiert nicht")
        return item

    @staticmethod
    def create_new(
        benutzername: str,
        name: str,
        email: str,
        passwort: str,
        rolle: Rolle
    ) -> Benutzer:
        if db.session.query(Benutzer).filter_by(benutzername=benutzername).first():
            raise ElementAlreadyExists(
                f"Benutzer mit dem Benutzernamen \"{benutzername}\" existiert bereits")

        new_user = Benutzer(
            benutzername=benutzername.strip(),
            name=name.strip(),
            emailAdresse=email.strip(),
            passwort=passwort,
            rolle_id=rolle.id
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def __repr__(self):
        return f"<User {self.benutzername} {self.Rolle.schreibenEinstellungen}>"
