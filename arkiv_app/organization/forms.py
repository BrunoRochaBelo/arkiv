from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email


class OrganizationForm(FlaskForm):
    name = StringField('Nome da Organização', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    custom_domain = StringField('Domínio Personalizado')
    submit = SubmitField('Salvar')


class InviteUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    role = SelectField(
        'Papel',
        choices=[
            ('MANAGER', 'MANAGER'),
            ('EDITOR', 'EDITOR'),
            ('CONTRIBUTOR', 'CONTRIBUTOR'),
            ('VIEWER', 'VIEWER'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Convidar')
