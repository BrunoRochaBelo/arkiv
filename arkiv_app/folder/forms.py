from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class FolderForm(FlaskForm):
    library_id = SelectField('Library', coerce=int, validators=[DataRequired()])
    parent_id = SelectField('Parent', coerce=int, choices=[(0, 'Root')])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')
