import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (DecimalField, PasswordField, SelectField,
                            SelectMultipleField, StringField, SubmitField,
                            TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class InitalLoginForm(KPForm):
    name = StringField("Name *", validators=[DataRequired()])
    email = StringField(
        "E-Mail", validators=[Optional(), Length(max=255)])
    strasse = StringField("Straße", validators=[Optional()])
    hausnummer = StringField("Hausnummer", validators=[Optional()])
    plz = StringField(
        "PLZ", validators=[Optional(), length(min=5, max=5)])
    ort = StringField("Ort", validators=[Optional()])
    iban = StringField(
        "IBAN", validators=[Optional(), length(min=22, max=34)])
    passwort = PasswordField(
        "Passwort *", validators=[DataRequired(), Length(min=8)])
    passwortBestaetigung = PasswordField(
        "Passwort Bestätigung *", validators=[DataRequired(), EqualTo('passwort')])
    submit = SubmitField("Speichern")


class ChangePasswordForm(KPForm):
    passwort = PasswordField(
        "Neues Passwort *", validators=[DataRequired(), Length(min=8)])
    passwortBestaetigung = PasswordField(
        "Neues Passwort Bestätigung *", validators=[DataRequired(), EqualTo('passwort')])
    submit = SubmitField("Passwort Ändern")


class EditProfileForm(KPForm):
    name = StringField("Name *", validators=[DataRequired()])
    email = StringField(
        "E-Mail", validators=[Optional(), Length(max=255)])
    strasse = StringField("Straße", validators=[Optional()])
    hausnummer = StringField("Hausnummer", validators=[Optional()])
    plz = StringField(
        "PLZ", validators=[Optional(), length(min=5, max=5)])
    ort = StringField("Ort", validators=[Optional()])
    iban = StringField(
        "IBAN", validators=[Optional(), length(min=22, max=34)])
    submit = SubmitField("Profil Aktualisieren")
