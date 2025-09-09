import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length
from wtforms_sqlalchemy.fields import QuerySelectField

from ...database.material import (KategorieSpezifisch, KategorieTypen, Set,
                                  SetTypes)
from ..forms import KPForm


class NewMaterialForm(KPForm):
    title = StringField('Name', validators=[
                        Optional()], render_kw={"placeholder": "Automatisch"})
    category = SelectField(
        "Kategorie",
        coerce=int,
        validators=[DataRequired()]
    )
    description = TextAreaField('Beschreibung', validators=[Optional()])
    artNr = StringField('Artikelnummer', validators=[Optional()])
    set = SelectField(
        "Set",
        coerce=int,
        validators=[DataRequired()]
    )
    images = MultipleFileField('Bilder', validators=[
                               FileAllowed(['jpg', 'png'], 'Nur Bilder erlaubt')])
    submit = SubmitField('Speichern')

    def populate_obj(self, obj=None):
        self.category.choices = {"Kein": [(-1, "Kein")]} | {
            k.name: [(s.id, s.name) for s in KategorieSpezifisch.filter_by(kategorie_typen_id=k.id)] for k in KategorieTypen.get_all()}

        self.set.choices = {"Kein": [(-1, "Kein")]} | {
            k.name: [(s.id, s.name) for s in Set.filter_by(setType_id=k.id)] for k in SetTypes.get_all()}

        super().populate_obj(obj)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EditMaterialForm(NewMaterialForm):
    delete_images = MultiCheckboxField('Bilder', coerce=int)
