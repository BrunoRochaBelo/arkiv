from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    color_hex = StringField('Color')
    submit = SubmitField('Save')
