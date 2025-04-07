import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class NewKategorieStep1Form(KPForm):
    name = StringField('Name', validators=[
                       DataRequired()])
    kuerzel = StringField('Kürzel', validators=[
                          DataRequired()])
    submit = SubmitField('Speichern')


class NewKategorieStep2Form(KPForm):
    name = StringField('Name', validators=[
                       DataRequired()])
    kuerzel = StringField('Kürzel', validators=[
                          DataRequired()])
    submit = SubmitField('Speichern')
