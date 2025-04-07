from flask_wtf import FlaskForm
from werkzeug.datastructures.structures import ImmutableMultiDict


class KPForm(FlaskForm):
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
