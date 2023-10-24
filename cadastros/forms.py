from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from cadastros.models import *

class UsuarioIncluir(FlaskForm):
    nome = StringField("Nome: ", validators=[DataRequired()])
    idade = StringField("Idade: ", validators=[DataRequired()])
    botao_confirmar = SubmitField('Confirmar')

class UsuarioEditar(FlaskForm):
    id = StringField("ID: ")
    nome = StringField("Nome: ", validators=[DataRequired()])
    idade = StringField("Idade: ", validators=[DataRequired()])
    botao_confirmar = SubmitField('Confirmar')
