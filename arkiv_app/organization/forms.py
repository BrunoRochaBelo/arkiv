from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class OrganizationForm(FlaskForm):
    name = StringField('Nome da Organização', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    custom_domain = StringField('Domínio Personalizado')
    submit = SubmitField('Salvar')
