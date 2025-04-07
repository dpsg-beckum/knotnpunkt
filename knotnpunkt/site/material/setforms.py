import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class NewSetTypeForm(KPForm):
    name = StringField('Name', validators=[
                       DataRequired()])
    kuerzel = StringField('Kürzel', validators=[
                          DataRequired()])
    submit = SubmitField('Speichern')


class NewSetForm(KPForm):
    number = StringField('Nummer', validators=[
        DataRequired()])
    submit = SubmitField('Speichern')
