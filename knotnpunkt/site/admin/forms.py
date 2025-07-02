import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (DecimalField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class CreateUserForm(KPForm):
    benutzername = StringField("Benutzername *", validators=[DataRequired()])
    name = StringField("Name *", validators=[DataRequired()])
    email = StringField(
        "E-Mail", validators=[Optional(), Length(max=255)])
    passwort = StringField(
        "Passwort (Leer: Automatisch Generiert)", validators=[Optional(), Length(min=8)])
    rolle_id = SelectField("Rolle *", coerce=int, validators=[DataRequired()])


class EditUserForm(KPForm):
    name = StringField("Name *", validators=[DataRequired()])
    email = StringField(
        "E-Mail", validators=[Optional(), Length(max=255)])
    rolle = SelectField("Rolle *", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Benutzer Aktualisieren")
    reset = SubmitField("Passwort Zurücksetzen")
