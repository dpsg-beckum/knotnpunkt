import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length

from ..forms import KPForm


class NewMaterialForm(KPForm):
    title = StringField('Name', validators=[
                        Optional()], render_kw={"placeholder": "Automatisch"})
    category = SelectField('Kategorie', choices=[])
    description = TextAreaField('Beschreibung', validators=[Optional()])
    artNr = StringField('Artikelnummer', validators=[Optional()])
    set = SelectField('Set', choices=[])
    images = MultipleFileField('Bilder', validators=[
                               FileAllowed(['jpg', 'png'], 'Nur Bilder erlaubt')])
    submit = SubmitField('Speichern')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EditMaterialForm(NewMaterialForm):
    delete_images = MultiCheckboxField('Bilder', coerce=int)
