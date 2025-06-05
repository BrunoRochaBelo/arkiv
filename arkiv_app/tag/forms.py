from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TagForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    color_hex = StringField('Cor')
    submit = SubmitField('Salvar')
