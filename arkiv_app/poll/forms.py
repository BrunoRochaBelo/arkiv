from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField, FieldList
from wtforms.validators import DataRequired


class PollForm(FlaskForm):
    question = StringField('Pergunta', validators=[DataRequired()])
    closes_at = DateTimeField('Encerra em', format='%Y-%m-%d %H:%M', validators=[])
    options = FieldList(StringField('Opção', validators=[DataRequired()]), min_entries=2)
    submit = SubmitField('Salvar')
