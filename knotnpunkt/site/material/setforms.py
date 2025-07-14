import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length
from wtforms_sqlalchemy.fields import QuerySelectField

from ...database.material import SetTypes
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


class NewSetForm(KPForm):
    number = StringField('Nummer', validators=[
        DataRequired()], default="1")
    set_type = QuerySelectField(
        "Set Typ",
        query_factory=SetTypes.get_all,
        get_label=lambda s: f"{s.kuerzel} ({s.name})",
        allow_blank=False
    )
    submit = SubmitField('Erstellen')
