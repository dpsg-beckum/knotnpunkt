import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length
from wtforms_sqlalchemy.fields import QuerySelectField

from ...database.material import KategorieSpezifisch, Set
from ..forms import KPForm


class NewMaterialForm(KPForm):
    title = StringField('Name', validators=[
                        Optional()], render_kw={"placeholder": "Automatisch"})
    category = QuerySelectField(
        "Kategorie",
        query_factory=KategorieSpezifisch.get_all,
        get_label=lambda k: f"{k.kategorie_typen.kuerzel}{k.kuerzel} ({k.kategorie_typen.name} {k.name})",
        allow_blank=False,
    )
    description = TextAreaField('Beschreibung', validators=[Optional()])
    artNr = StringField('Artikelnummer', validators=[Optional()])
    set = QuerySelectField(
        "Set",
        query_factory=Set.get_all,
        get_label=lambda s: f"{s.number}.{s.setType.kuerzel} ({s.setType.name})",
        allow_blank=True,
        blank_text="Kein Set"
    )
    images = MultipleFileField('Bilder', validators=[
                               FileAllowed(['jpg', 'png'], 'Nur Bilder erlaubt')])
    submit = SubmitField('Speichern')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EditMaterialForm(NewMaterialForm):
    delete_images = MultiCheckboxField('Bilder', coerce=int)
