from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from ..models import Tag
from ..utils import current_org_id


class TagForm(FlaskForm):
    """Formulário para criação/edição de tags."""

    name = StringField("Nome", validators=[DataRequired()])
    color_hex = StringField("Cor")
    submit = SubmitField("Salvar")

    def __init__(self, original=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tag instance being edited, for uniqueness validation
        self.original = original

    def validate_name(self, field):
        org_id = current_org_id()
        if org_id is None:
            return
        query = Tag.query.filter_by(org_id=org_id, name=field.data)
        if self.original is not None:
            query = query.filter(Tag.id != self.original.id)
        if query.first():
            raise ValidationError("Nome de tag j\u00e1 existe")
