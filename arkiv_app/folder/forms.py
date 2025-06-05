from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class FolderForm(FlaskForm):
    library_id = SelectField('Biblioteca', coerce=int, validators=[DataRequired()])
    parent_id = SelectField('Pai', coerce=int, choices=[(0, 'Raiz')])
    name = StringField('Nome', validators=[DataRequired()])
    submit = SubmitField('Salvar')
