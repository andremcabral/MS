from cadastros import db
class Imovel(db.Model):
    inscricao = db.Column(db.String, primary_key=True)
    dados = db.Column(db.String)
    cl = db.Column(db.String)
    rua = db.Column(db.String)
    numero = db.Column(db.String)
    compl = db.Column(db.String)
    bairro = db.Column(db.String)
    contribuinte = db.Column(db.String)
    def __str__(self):
        return self.inscricao

class Conjunto(db.Model):
    codigo = db.Column(db.String, primary_key=True)
    nome = db.Column(db.String)
    bairro = db.Column(db.String)
    uhs = db.Column(db.String)
    legalizado = db.Column(db.String)
    comercializacao = db.Column(db.String)
    cod_Município = db.Column(db.String)
    municipio = db.Column(db.String)
    ruas = db.Column(db.String)
    def __str__(self):
        return self.codigo

