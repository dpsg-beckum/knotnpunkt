import wtforms.widgets as widgets
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from werkzeug.datastructures.structures import ImmutableMultiDict
from wtforms.fields import (SelectField, SelectMultipleField, StringField,
                            SubmitField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length, Optional, length


class LRForm(FlaskForm):
    def update_form(self):
        """
        Updates the form's field values and reprocesses the form to ensure the new values are used in rendering.
        This is useful when field values are updated after initial form processing.
        """
        # self.process()
        # Re-process each field with the updated data
        for field in self:
            data = field.data if field.data is not None else ""
            # ensures it re-processes using the current `data`
            field.process(formdata=ImmutableMultiDict(
                {field.name: data}))
            pass


class NewMaterialForm(LRForm):
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
