from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class NoticeForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    body = TextAreaField('Conteúdo', validators=[DataRequired()])
    category = StringField('Categoria')
    submit = SubmitField('Salvar')
