import re

from flask_wtf.file import FileAllowed, FileField
from wtforms.fields import (DecimalField, SelectField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from ..forms import KPForm


def validate_iban(form, field: StringField):
    """Custom validator for IBAN format and checksum."""
    value = field.data.replace(' ', '').upper()
    # Basic IBAN format check
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', value):
        raise ValidationError('Ungültiges IBAN-Format.')
    # Move first four chars to end and convert letters to numbers (A=10, ..., Z=35)
    rearranged = value[4:] + value[:4]
    numerized = ''
    for c in rearranged:
        if c.isdigit():
            numerized += c
        elif c.isalpha():
            numerized += str(ord(c) - 55)
        else:
            raise ValidationError('Ungültige Zeichen in der IBAN.')
    # Perform mod-97 check
    if int(numerized) % 97 != 1:
        raise ValidationError('IBAN-Prüfziffer ist ungültig.')

    # Save the formatted IBAN back to the field
    field.data = value
    return True


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
        DataRequired(), Length(max=34), validate_iban])
    bic = StringField("BIC *", validators=[
        Optional(), Length(max=11)])
    submit = SubmitField("Einreichen")

    def update_form(self):
        super().update_form()

        # format iban data to insert spaces every 4 chars
        self.iban.data = ' '.join(
            self.iban.data[i:i+4] for i in range(0, len(self.iban.data), 4))
