from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired

from ...forms import KPForm


class NewSetTypeForm(KPForm):
    name = StringField('Name', validators=[
                       DataRequired()])
    kuerzel = StringField('Kürzel', validators=[
                          DataRequired()])
    submit = SubmitField('Speichern')


class NewSetForm(KPForm):
    number = StringField('Nummer', validators=[
        DataRequired()], default="1")
    submit = SubmitField('Erstellen')
