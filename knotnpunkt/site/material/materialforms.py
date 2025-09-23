import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (DecimalField, IntegerField, SelectField,
                            SelectMultipleField, StringField, SubmitField,
                            TextAreaField)
from wtforms.validators import (DataRequired, EqualTo, Length, NumberRange,
                                Optional, length)
from wtforms_sqlalchemy.fields import QuerySelectField

from ...database.material import (Img, KategorieSpezifisch, KategorieTypen,
                                  Material, Set, SetTypes)
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
    nrset = IntegerField('Nummer im Set', validators=[
                         Optional(), NumberRange(min=0)], default=0)
    images = MultipleFileField('Bilder', validators=[
                               FileAllowed(['jpg', 'png'], 'Nur Bilder erlaubt')])
    submit = SubmitField('Speichern')

    def populate_obj(self, obj=None):
        self.category.choices = {"Kein": [(-1, "Kein")]} | {
            k.name: [(s.id, f"{s.name} - {k.name}") for s in KategorieSpezifisch.filter_by(kategorie_typen_id=k.id)] for k in KategorieTypen.get_all()}

        self.set.choices = {"Kein": [(-1, "Kein")]} | {
            f"{k.kuerzel} {k.name}": [(s.id, f"{k.kuerzel}.{s.number} {s.name or ''}") for s in Set.filter_by(setType_id=k.id)] for k in SetTypes.get_all()}

        super().populate_obj(obj)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EditMaterialForm(NewMaterialForm):
    delete_images = MultiCheckboxField('Bilder', coerce=int)

    def populate_obj(self, obj=None, material: Material = None):
        if not material:
            raise ValueError("material must be provided")

        self.delete_images.choices = [(i.id, i.id)
                                      for i in Img.filter_by(material_id=material.id)]
        super().populate_obj(obj)
