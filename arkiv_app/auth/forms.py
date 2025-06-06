from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Continuar logado')
    token = StringField('Código 2FA')
    submit = SubmitField('Entrar')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova senha', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Definir senha')
