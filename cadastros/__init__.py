# import urllib.parse, pyodbc, os
# import sqlalchemy.dialects.mssql.pyodbc
# from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from instance.trataBanco import conecta
from urllib.parse import quote_plus

# cria o aplicativo usando o nome informado no código
app = Flask(__name__)
# driver='pyodbc'
driver='{SQL Server}'
server='HP03-CIF002'
porta='1433'
banco='CL_Insc_Cehab'
parametros = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'PORT={porta};'
    f'DATABASE={banco};'
    'use_setinputsizes=False;'
    # Nome de usuário.
    # 'UID=sa;'
    # Senha/Token.
    # 'PWD=sacehab23'
    )

# cursorCL = conecta(driver, server, 'CL_Insc_Cehab')
# cursorSIGI = conecta(driver, server, 'Dados_Sigi')

url_db = quote_plus(parametros)
# engine = create_engine(f"mssql+pyodbc://@{server}:{porta}/{banco}?driver=ODBC+Driver+17+for+SQL+Server")
# eng = create_engine("mssql+pyodbc:///?odbc_connect=%s" % url_db)
# conexao = eng.connect()

# # informa onde será criado o banco de dados e qual o tipo (neste caso é um sqlite)
#  BANCO SQL SERVER
# app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc:///?odbc_connect=%s" % url_db
app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc://@{server}:{porta}/{banco}?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # EM TESTE

#  USAR BANCO SQLITE
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cadastros"

# cria banco de dados vinculando ao aplicativo
db = SQLAlchemy(app)

# importa o arquivo de rotas (no final do código)
from cadastros import routes