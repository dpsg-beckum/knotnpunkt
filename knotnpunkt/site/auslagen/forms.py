import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (DecimalField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class ShowAuslagenForm(KPForm):
    approve = SubmitField("Genehmigen", name="approve")
    done = SubmitField("Erledigt", name="done")
    delete = SubmitField("Löschen", name="delete")


class EditAuslagenForm(KPForm):
    title = StringField("Titel *", validators=[DataRequired()])
    category = SelectField("Kategorie *", coerce=int,
                           validators=[DataRequired()])
    comment = TextAreaField("Begründung / Anmerkungen (200 Zeichen)", validators=[
        Optional(), Length(max=200)])
    submit = SubmitField("Änderungen speichern")


class NewAuslagenForm(KPForm):
    image = FileField("Belegbild *",
                      validators=[DataRequired(),
                                  FileAllowed(["jpg", "png", "jpeg"], "Nur Bilder sind erlaubt")]
                      )
    title = StringField("Titel *", validators=[DataRequired()])
    category = SelectField("Kategorie *", coerce=int,
                           validators=[DataRequired()])
    comment = TextAreaField("Begründung / Anmerkungen (200 Zeichen)", validators=[
        Optional(), Length(max=200)])
    betrag = DecimalField("Betrag(€) *",
                          validators=[DataRequired()], places=2)
    kontoinhaber = StringField("Kontoinhaber_in *", validators=[
        DataRequired(), Length(max=100)])
    iban = StringField("IBAN *", validators=[
        DataRequired(), Length(max=34)])
    bic = StringField("BIC *", validators=[
        Optional(), Length(max=11)])
    submit = SubmitField("Einreichen")
