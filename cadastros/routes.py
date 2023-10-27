from flask import render_template, request
from cadastros import app
from cadastros.models import *
from instance.trataBanco import conecta
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# from flask_paginate import Pagination, get_page_parameter
# from flask_paginate import Pagination, get_page_args

driver='{SQL Server}'
server='HP03-CIF002'
porta='1433'
tabelaIPTU = 'dbo.IPTU$'
usuario='-'
localAcesso='-'
status='-'
nome='-'
# banco='CL_Insc_Cehab'
# parametros = (
#     f'DRIVER={driver};'
#     f'SERVER={server};'
#     f'PORT={porta};'
#     f'DATABASE={banco};'
#     'use_setinputsizes=False;'
#     )

cursorCL = conecta(driver, server, 'CL_Insc_Cehab')
cursorSIGI = conecta(driver, server, 'Dados_Sigi')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
linhas = 300
dicUsuarios={}

#  /////////////////////////// ENTRADAS //////////////////////////////////////////////////
@app.route("/consulta")
def consulta():
    global localAcesso, usuarioAtual, status, nome
    usuarioAtual = os.getenv('USERNAME')
    localAcesso = os.getenv('COMPUTERNAME')
    cadUsuario = cursorCL.execute(f"select * from Usuarios where usuario = '{usuarioAtual}'").fetchall()
    if len(cadUsuario)==0:
        return render_template("usuario.html", usuario=usuarioAtual, localAcesso=localAcesso)
    else:
        nome = cadUsuario[0][1]
        status="Retornando"
        return render_template("pesquisaConjunto.html", usuario=usuarioAtual, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/")
def homepage():
    global localAcesso, usuarioAtual, status, nome
    # usuarioAtual = os.getlogin()
    usuarioAtual = os.getenv('USERNAME')
    localAcesso = os.getenv('COMPUTERNAME')
    cadUsuario = cursorCL.execute(f"select * from Usuarios where usuario = '{usuarioAtual}'").fetchall()
    if len(cadUsuario)==0:
        return render_template("usuario.html", usuario=usuarioAtual, localAcesso=localAcesso)
    else:
        nome = cadUsuario[0][1]
        status="Retornando"
        return render_template("index.html", usuario=usuarioAtual, localAcesso=localAcesso, status=status, nome=nome)

#  /////////////////////////// USUÁRIOS ///////////////////////////////////////////////////
@app.route("/<usuario>,<localAcesso>")
def usuario(usuario, localAcesso):
    global status, nome
    # cursor = conecta(driver, server, 'CL_Insc_Cehab')
    nome=request.args.get('nometxt')
    status = "Primeiro acesso"
    cursorCL.execute(f"INSERT INTO dbo.Usuarios (usuario,nome) VALUES ('{usuario}', '{nome}')")
    cursorCL.commit()
    return render_template("index.html", usuario=usuario, localAcesso=localAcesso, status=status, nome=nome)
    # return render_template("index.html", usuario=usuario, nome=nome)

#  /////////////////////////// ÁREA 1 - IPTU //////////////////////////////////////////////
@app.route("/imoveis") # IPTU
def imoveis():
    global imoveis
    referenciaInsc = request.args.get('referenciaInsc')
    referenciaDados = request.args.get('referenciaDados')
    referenciaNum = request.args.get('referenciaNum')
    referenciaBairro = request.args.get('referenciaBairro')
    e_num = request.args.get('E_Num')
    e_bairro = request.args.get('E_Bairro')
    formulario = Imovel
    if referenciaInsc:
        referencia = referenciaInsc
        imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where inscricao like '%{referencia}%' order by inscricao ").fetchall()
        qtdEncontrada = len(imoveis)
        qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where inscricao like '%{referencia}%'").fetchall())
        referenciaDados = ""
        referenciaNum = ""
        referenciaBairro = ""
    else:
        if e_bairro and referenciaBairro and e_num and referenciaNum:
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' and numero like '%{referenciaNum}%' and bairro like '%{referenciaBairro}%' order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' and numero like '%{referenciaNum}%' and bairro like '%{referenciaBairro}%' order by rua desc").fetchall())
        elif e_bairro and referenciaBairro:
            referenciaNum = ""
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' and bairro like '%{referenciaBairro}%' order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' and bairro like '%{referenciaBairro}%' order by rua desc").fetchall())
        elif e_num and referenciaNum:
            referenciaBairro = ""
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' and numero like '%{referenciaNum}%' order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' and numero like '%{referenciaNum}%' order by rua desc").fetchall())
        else:
            if referenciaBairro:
                referenciaDados = ""
                referenciaNum = ""
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where bairro like '%{referenciaBairro}%' order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where bairro like '%{referenciaBairro}%'").fetchall())
            elif referenciaNum:
                referenciaDados = ""
                referenciaBairro = ""
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where numero like '%{referenciaNum}%' order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where numero like '%{referenciaNum}%'").fetchall())
            elif referenciaDados:
                referenciaNum = ""
                referenciaBairro = ""
                # imoveis = Imovel.query.all()
                # imoveis = Imovel.query.order_by(Imovel.bairro).filter(tabelaIPTU.inscricao.ilike(f'%{referencia}%')).paginate(page=page, per_page=linhas)
                imoveis = cursorCL.execute(
                    f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(
                    cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%'").fetchall())
            else:
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where rua<>'-' order by bairro, rua").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU}").fetchall())
                # total = qtdTotal
                # # page, per_page, offset = get_page_args(page_parameter="p", per_page_parameter="pp", pp=20)
                # per_page=8
                # offset=3
                # # if per_page:
                # sql = f"select top 8 * from {tabelaIPTU} where dados like '%{referencia}%' order by rua"
                #     # sql = f"select top 100 * from {tabelaIPTU} where dados like '%{referencia}%' order by rua limit '{offset}', {per_page}"
                # imoveis = cursor.execute(sql).fetchall()
                # pagination = Pagination(p=page,pp=per_page,total=total,record_name="imoveis",format_total=True,format_number=True,page_parameter="p",per_page_parameter="pp")
                # pagination = Pagination(page=page, total=qtdTotal, search=False, record_name='imoveis')
                # imoveis = Imovel.query.order_by(Imovel.bairro).filter(Imovel.dados.ilike(f'%{referencia}%')).paginate(page=page,per_page=linhas)
        # return render_template("imoveis/imoveis.html", imoveis=imoveis, form=formulario, qtd=qtdEncontrada, qtdTotal=qtdTotal, referenciaInsc=referenciaInsc, referencia=referencia, linhas=linhas, pagination=pagination,)
    return render_template("imoveis/imoveis.html", imoveis=imoveis, form=formulario, qtd=qtdEncontrada, qtdTotal=qtdTotal, referenciaInsc=referenciaInsc, referenciaBairro=referenciaBairro, referenciaDados=referenciaDados, referenciaNum=referenciaNum, linhas=linhas, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/imoveis/imovel/<imovel>") # DETALHES DE UM IMÓVEL
def imovel(imovel):
    form = Imovel()
    imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where inscricao = '{imovel}'").fetchall()
    # imovel = Imovel.query.filter_by(inscricao=imovel).first()
    return render_template("imoveis/imovel.html", imovel=imovel, form=form, imoveis=imoveis, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/conferencia/<numInsc>") # CONFERE INSCRIÇÃO NO SITE
def confereInscricao(numInsc):
    navegador = webdriver.Chrome()
    navegador.get("https://iportal.rio.rj.gov.br/PF331IPTUATUAL/pages/ParcelamentoIptuDs/TelaSelecao.aspx")
    campoInsc = navegador.find_element(By.ID, "ctl00_ePortalContent_inscricao_input")
    campoInsc.send_keys(numInsc)
    navegador.find_element(By.ID, "ctl00_ePortalContent_DefiniGuia").click()
    resposta=navegador.find_element(By.XPATH, "//*[@id='aspnetForm']/div[3]/div[3]")
    return resposta

#  /////////////////////////// ÁREA 2 - SIGI E PLANILHAS ////////////////////////////////////
@app.route("/listaConjuntos") # Cadastro de conjuntos
def listaConjuntos():
    global conjuntos, localAcesso, status, nome
    referenciaCod = request.args.get('referenciaCod')
    formulario = Conjunto
    if referenciaCod:
        referencia = request.args.get('referenciaCod')
        conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where COD like '%{referencia}%' order by COD").fetchall()
    else:
        referencia = request.args.get('referenciaCon')
        conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where nomePlanilha like '%{referencia}%' or nomeSigi like '%{referencia}%' or bairroPlanilha like '%{referencia}%' or bairroSigi like '%{referencia}%' order by COD").fetchall()
    qtdEncontrada = len(conjuntos)
    return render_template("sigi/conjuntos.html", conjuntos=conjuntos, form=formulario, qtd=qtdEncontrada, referencia=referencia, linhas=linhas, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/bairro") # Conjuntos por Bairro
def bairro():
    bairro = request.args.get('bairro')
    # cursor = conecta(driver, server, 'Dados_Sigi')
    conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where bairroPlanilha like '%{bairro}%' or bairroSIGI like '%{bairro}%' order by bairroPlanilha").fetchall()
    qtd=len(conjuntos)
    return render_template("sigi/conjuntos.html", conjuntos=conjuntos, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/conjunto/<codConjunto>/<nomeConjunto>") # DETALHES DO CONJUNTO
def conjunto(codConjunto, nomeConjunto):
    # cursor = conecta(driver, server, 'Dados_Sigi')
    conjunto = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where COD = '{codConjunto}'").fetchall()
    return render_template("sigi/conjunto.html", conjunto=conjunto, codConjunto=codConjunto, nomeConjunto=nomeConjunto, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/conjunto/ruas/<codConjunto>") # RUAS DO CONJUNTO
def ruas(codConjunto):
    ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.ruas where CodConjunto = '{codConjunto}' order by nomeRua").fetchall()
    qtd=len(ruas)
    return render_template("sigi/ruas.html", ruas=ruas, codConjunto=codConjunto, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/ruas-conjuntos/") # RUAS DO CONJUNTO
def ruasConjunto():
    referenciaConjRua=nome=request.args.get('referenciaConjRua')
    ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.Ruas_Conjunto where nomeConjunto like '%{referenciaConjRua}%' order by nomeRua").fetchall()
    qtd=len(ruas)
    return render_template("sigi/ruasConjuntos.html", ruas=ruas, nomeConjunto=referenciaConjRua, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/conjunto/imoveis/<conjunto>/<rua>/<nomeRua>") # IMÓVEIS POR RUA
def imoveisRua(conjunto, rua, nomeRua):
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto = '{conjunto}' and NomeRua = '{nomeRua}' order by CodImovel").fetchall()
    qtd=len(imoveis)
    return render_template("sigi/imoveisRua.html", imoveis=imoveis, rua=rua, conjunto=conjunto, qtd=qtd, nomeRua=nomeRua, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/<codConjunto>/<codImob>") # DETALHES DO IMÓVEL
def detalhesImovel(codConjunto,codImob):
    imovel = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto = '{codConjunto}' and CodImovel = '{codImob}'").fetchall()
    return render_template("sigi/detalhesImovel.html", conjunto=conjunto, imovel=imovel, localAcesso=localAcesso, status=status, nome=nome)

#  /////////////////////////// ÁREA 3 - SIGI ////////////////////////////////////
@app.route("/ruas") # Cadastro de ruas no SIGI
def ruasGeral():
    nomeRua = request.args.get('referenciaNomeRua')
    ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.ruas where NomeRua like '%{nomeRua}%' order by nomeRua ").fetchall()
    qtd=len(ruas)
    return render_template("sigi/ruas.html", ruas=ruas, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/conjunto/") # Consulta por Imobiliário no SIGI
def imob():
    imob = request.args.get('imob')
    conj = request.args.get('conj')
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto like '%{conj}%' and CodImovel like '%{imob}%' order by CodImovel").fetchall()
    qtd=len(imoveis)
    return render_template("sigi/imoveisRua.html", imoveis=imoveis, imob=imob, conjunto=conj, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/mutuario") # Consulta de imóveis por mutuário no SIGI
def imoveisMutuario():
    print('mutuarios')
    imoveisMutuario = request.args.get('imoveisMutuario')
    # cursor = conecta(driver, server, 'Dados_Sigi')
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where NomeMorador like '%{imoveisMutuario}%' order by NomeMorador").fetchall()
    qtdEncontrada = cursorSIGI.execute(f"select * from dbo.Dados_Imovel_Morador where NomeMorador like '%{imoveisMutuario}%'").fetchall()
    qtdEncontrada = len(qtdEncontrada)
    qtd=len(imoveis)
    return render_template("sigi/imoveisMutuario.html", imoveis=imoveis, qtd=qtd, qtdTotal=qtdEncontrada, imoveisMutuario=imoveisMutuario, localAcesso=localAcesso, status=status, nome=nome)

#  /////////////////////////// ÁREA 4 - RESUMO ////////////////////////////////////
@app.route("/resumo") # Mesclagem SIGI x Prefeitura
def resumo():
    referenciaCodCJ = request.args.get('referenciaCodCJ')
    referenciaRua = request.args.get('referenciaRua')
    if referenciaCodCJ:
        resumo = cursorCL.execute(f"select top {linhas} * from dbo.resumo where codConjunto like '%{referenciaCodCJ}%' order by NomeConjunto, ruaPLANILHA").fetchall()
        qtdTotal = cursorCL.execute(f"select * from dbo.resumo where codConjunto like '%{referenciaCodCJ}%'").fetchall()
    else:
        resumo = cursorCL.execute(f"select top {linhas} * from dbo.resumo where RuaPLANILHA like '%{referenciaRua}%' order by NomeConjunto, ruaPLANILHA").fetchall()
        qtdTotal = cursorCL.execute(f"select * from dbo.resumo where RuaPLANILHA like '%{referenciaRua}%'").fetchall()
        # conjuntos = cursor.execute(f"select * from dbo.resumo where NomeConjunto like '%{referencia}%' order by NomeConjunto").fetchall()
    qtdEncontrada = len(resumo)
    qtdTotal = len(qtdTotal)
    # resumo2 = pd.DataFrame(resumo,columns=['CodConjunto','NomeConjunto','BairroPlanilha','BairroIPTU','RuaPLANILHA','RuaSIGI','CL','inscricao','Número','Imób','Lg','ContribuinteIPTU','ContribuintePLANILHA','dados'])
    # resumo2=pd.DataFrame(resumo)
    return render_template("resumo/resumo.html", resumo=resumo, qtd=qtdEncontrada, qtdTotal=qtdTotal, localAcesso=localAcesso, status=status, nome=nome)
