from __future__ import annotations

import secrets
from logging import debug
from typing import List, Optional, Type, TypeVar

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, ForeignKey, String, Table
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

# 1) Define the association table
rolle_rechte_association = Table(
    "rolle_rechte",
    BaseTable.metadata,
    Column("rolle_id", ForeignKey("rolle.id"), primary_key=True),
    Column("rechte_id", ForeignKey("rechte.id"), primary_key=True),
)


class Rolle(BaseTable):
    """
    Rolle Tabelle
    """

    __tablename__ = 'rolle'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)

    # 2) Declare the relationship, pointing at Rechte, via the association table
    rechte: Mapped[List[Rechte]] = relationship(
        "Rechte",
        secondary=rolle_rechte_association,
        back_populates="rollen",
        collection_class=list,
    )

    benutzer: Mapped[List[Benutzer]] = relationship(
        "Benutzer",
        back_populates="Rolle",
        collection_class=list,
    )

    def __str__(self):
        return f"<Rolle {self.name}>"

    def to_dict(self, depth: int = 2, _visited: set[int] | None = None) -> dict:

        data = super().to_dict(depth, _visited)

        recht: Rechte
        for recht in Rechte.get_all():
            if self.hat_recht(recht):
                data[recht.name] = True
            else:
                data[recht.name] = False

        return data

    @staticmethod
    def get_via_name(name: str) -> Rolle:
        item = db.session.query(Rolle).get({"name": name})
        if not item:
            raise ElementDoesNotExsist(
                f"{str(Rolle.__name__)} mit dem Namen \"{name}\" existiert nicht")
        return item

    @staticmethod
    def create_new(id: int, name: str) -> Rolle:
        if db.session.query(Rolle).filter_by(name=name).first():
            raise ElementAlreadyExists(
                f"Rolle mit dem Namen \"{name}\" existiert bereits"
            )
        new = Rolle(id=id, name=name)
        db.session.add(new)
        db.session.commit()
        return new

    def hat_recht(self, recht: Rechte | str) -> bool:
        """
        Überprüft, ob die Rolle ein bestimmtes Recht hat.
        :param recht: Das Recht, das überprüft werden soll (entweder als Rechte-Objekt oder Name).
        :return: True, wenn die Rolle das Recht hat, sonst False.
        """
        if isinstance(recht, str):
            try:
                recht = Rechte.get_via_name(recht)
            except ElementDoesNotExsist:
                debug(
                    f"Recht {recht} nicht gefunden, kann nicht überprüft werden.")
                return False
        return recht in self.rechte

    def add_recht(self, recht: Rechte) -> None:
        """Fügt ein Recht zur Rolle hinzu."""
        if recht in self.rechte:
            raise ElementAlreadyExists(
                f"Recht \"{recht.name}\" ist schon in Rolle \"{self.name}\"."
            )
        self.rechte.append(recht)
        db.session.commit()

    def remove_recht(self, recht: Rechte) -> None:
        """Entfernt ein Recht aus der Rolle."""
        if recht not in self.rechte:
            raise ElementDoesNotExsist(
                f"Recht \"{recht.name}\" ist nicht in Rolle \"{self.name}\"."
            )
        self.rechte.remove(recht)
        db.session.commit()


class Rechte(BaseTable):
    """
    Rechte Tabelle
    """

    __tablename__ = 'rechte'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    beschreibung: Mapped[str] = mapped_column(String(255), nullable=True)

    # 3) Mirror the relationship on the other side
    rollen: Mapped[List[Rolle]] = relationship(
        "Rolle",
        secondary=rolle_rechte_association,
        back_populates="rechte",
        collection_class=list,
    )

    def __str__(self):
        return f"<Recht {self.name}>"

    @staticmethod
    def get_via_name(name: str) -> "Rechte":
        item = db.session.query(Rechte).filter_by(name=name).first()
        if not item:
            raise ElementDoesNotExsist(
                f"Rechte mit dem Namen \"{name}\" existiert nicht"
            )
        return item

    @staticmethod
    def create_new(id: int, name: str, beschreibung: str = None) -> "Rechte":
        if db.session.query(Rechte).filter_by(name=name).first():
            raise ElementAlreadyExists(
                f"Rechte mit dem Namen \"{name}\" existiert bereits"
            )
        new = Rechte(id=id, name=name, beschreibung=beschreibung)
        db.session.add(new)
        db.session.commit()
        return new


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

    rolle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rolle.id"))
    Rolle: Mapped[Optional[Rolle]] = relationship(
        "Rolle",
        back_populates="benutzer",
    )

    def checkPassword(self, password: str) -> bool:
        return check_password_hash(self.passwort, password)

    def set_passwort(self, neues_passwort: str) -> None:
        self.passwort = generate_password_hash(neues_passwort)
        db.session.commit()

    def reset_passwort(self) -> str:
        passwort = secrets.token_urlsafe(8)
        self.passwort = passwort
        db.session.commit()
        return passwort

    def set_rolle(self, rolle: Rolle) -> None:
        Rolle.get_via_id(rolle.id)  # Ensure the Rolle exists
        self.rolle_id = rolle.id
        db.session.commit()

    def update(
            self,
            name: str = None,
            emailAdresse: str = None,
            iban: str = None,
            strasse: str = None,
            hausnummer: str = None,
            postleitzahl: str = None,
            ort: str = None):
        updates = {
            'name': name,
            'emailAdresse': emailAdresse,
            'iban': iban,
            'strasse': strasse,
            'hausnummer': hausnummer,
            'postleitzahl': postleitzahl,
            'ort': ort,
        }
        for attr, value in updates.items():
            if value is not None:
                setattr(self, attr, value)
        db.session.commit()
        return self

    def is_active(self) -> bool:
        return True

    def get_id(self) -> str | None:
        return self.benutzername

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
        return f"<User {self.benutzername} {self.Rolle.name}>"
