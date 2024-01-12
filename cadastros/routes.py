import time
from flask import render_template, request
from iptu_CEHAB_flask.cadastros import app
from iptu_CEHAB_flask.cadastros.models import *
from iptu_CEHAB_flask.instance.trataBanco import conecta
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
        categoria = cadUsuario[0][2]
        status="Retornando"
        return render_template("pesquisaConjunto.html", usuario=usuarioAtual, localAcesso=localAcesso, status=status, nome=nome, categoria=categoria)

@app.route("/")
def homepage():
    global localAcesso, usuarioAtual, status, nome
    usuarioAtual = os.getlogin()
    testeUsuario = f"{os.getenv('USERNAME')} {os.getlogin()}"
    localAcesso = os.getenv('COMPUTERNAME')
    cadUsuario = cursorCL.execute(f"select * from Usuarios where usuario = '{usuarioAtual}'").fetchall()
    if len(cadUsuario)==0:
        status = "Novo"
        return render_template("usuario.html", usuario=usuarioAtual, localAcesso=localAcesso)
    else:
        nome = cadUsuario[0][1]
        categoria = cadUsuario[0][2]
        status="Retornando"
        return render_template("index.html", usuario=usuarioAtual, localAcesso=localAcesso, status=status, nome=nome, categoria=categoria, testeUsuario=testeUsuario)

#  /////////////////////////// USUÁRIOS ///////////////////////////////////////////////////
@app.route("/<usuario>,<localAcesso>")
def usuario(usuario, localAcesso):
    global status, nome
    # cursor = conecta(driver, server, 'CL_Insc_Cehab')
    nome=request.args.get('nometxt')
    categoria = 'categoria'
    status = "Primeiro acesso"
    cursorCL.execute(f"INSERT INTO dbo.Usuarios (usuario,nome, categoria) VALUES ('{usuario}', '{nome}', 'basico')")
    cursorCL.commit()
    return render_template("index.html", usuario=usuario, localAcesso=localAcesso, status=status, nome=nome, categoria=categoria)
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
    pagina = int(request.args.get('page', 1))
    # linhas = 300
    offset = (pagina - 1) * linhas
    if referenciaInsc:
        referencia = referenciaInsc
        imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where inscricao like '%{referencia}%' order by inscricao ").fetchall()
        # imoveis = cursorCL.execute(f"select * from {tabelaIPTU} where inscricao like '%{referencia}%' order by inscricao OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
        qtdEncontrada = len(imoveis)
        qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where inscricao like '%{referencia}%'").fetchall())
        referenciaDados = ""
        referenciaNum = ""
        referenciaBairro = ""
        num_paginas = int(qtdTotal / linhas) + 2
    else:
        if e_bairro and referenciaBairro and e_num and referenciaNum:
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and numero like '%{referenciaNum}%' and bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and numero like '%{referenciaNum}%' and bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI order by rua desc").fetchall())
            num_paginas = int(qtdTotal / linhas) + 2
        elif e_bairro and referenciaBairro:
            referenciaNum = ""
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI order by rua desc").fetchall())
            num_paginas = int(qtdTotal / linhas) + 2
        elif e_num and referenciaNum:
            referenciaBairro = ""
            imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and numero like '%{referenciaNum}%' order by rua desc").fetchall()
            qtdEncontrada = len(imoveis)
            qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI and numero like '%{referenciaNum}%' order by rua desc").fetchall())
            num_paginas = int(qtdTotal / linhas) + 2
        else:
            if referenciaBairro:
                referenciaDados = ""
                referenciaNum = ""
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where bairro like '%{referenciaBairro}%' collate Latin1_General_CI_AI").fetchall())
                num_paginas = int(qtdTotal / linhas) + 2
            elif referenciaNum:
                referenciaDados = ""
                referenciaBairro = ""
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where numero like '%{referenciaNum}%' order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where numero like '%{referenciaNum}%'").fetchall())
                num_paginas = int(qtdTotal / linhas) + 2
            elif referenciaDados:
                referenciaNum = ""
                referenciaBairro = ""
                # imoveis = Imovel.query.all()
                # imoveis = Imovel.query.order_by(Imovel.bairro).filter(tabelaIPTU.inscricao.ilike(f'%{referencia}%')).paginate(page=page, per_page=linhas)
                imoveis = cursorCL.execute(
                    f"select top {linhas} * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI order by rua desc").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU} where dados like '%{referenciaDados}%' collate Latin1_General_CI_AI").fetchall())
                num_paginas = int(qtdTotal / linhas) + 2
            else:
                imoveis = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where rua <> '-' order by bairro, rua").fetchall()
                imoveisTodos = cursorCL.execute(f"select top {linhas} * from {tabelaIPTU} where rua <> '-' order by bairro, rua").fetchall()
                # imoveis = cursorCL.execute(f"select * from {tabelaIPTU} order by inscricao OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
                qtdEncontrada = len(imoveis)
                qtdTotal = len(cursorCL.execute(f"select * from {tabelaIPTU}").fetchall())
                num_paginas = int(qtdTotal/linhas)+2
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
    return render_template("imoveis/imoveis.html", imoveis=imoveis, form=formulario, qtd=qtdEncontrada, qtdTotal=qtdTotal, referenciaInsc=referenciaInsc, referenciaBairro=referenciaBairro, referenciaDados=referenciaDados, referenciaNum=referenciaNum, linhas=linhas, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

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
#  OK - PESQUISA CONJUNTOS
def listaConjuntos():
    global conjuntos, localAcesso, status, nome
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    referenciaCod = request.args.get('referenciaCod')
    formulario = Conjunto
    if referenciaCod:
        referencia = request.args.get('referenciaCod')
        conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where COD like '%{referencia}%' order by COD").fetchall()
        # conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where COD like '%{referencia}%' order by COD OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
        qtdEncontrada = len(cursorSIGI.execute(f"select * from dbo.CONJUNTOS_GERAL where COD like '%{referencia}%' order by COD").fetchall())
        num_paginas = int(qtdEncontrada / linhas) + 2
    else:
        referencia = request.args.get('referenciaCon')
        conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where nomePlanilha like '%{referencia}%' collate Latin1_General_CI_AI or nomeSigi like '%{referencia}%' collate Latin1_General_CI_AI or bairroPlanilha like '%{referencia}%' collate Latin1_General_CI_AI or bairroSigi like '%{referencia}%' collate Latin1_General_CI_AI order by COD").fetchall()
        # conjuntos = cursorSIGI.execute(f"select * from dbo.CONJUNTOS_GERAL where nomePlanilha like '%{referencia}%' or nomeSigi like '%{referencia}%' or bairroPlanilha like '%{referencia}%' or bairroSigi like '%{referencia}%' order by COD OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
        # qtdEncontrada = len(cursorSIGI.execute(f"select * from dbo.CONJUNTOS_GERAL where nomePlanilha like '%{referencia}%' or nomeSigi like '%{referencia}%' or bairroPlanilha like '%{referencia}%' or bairroSigi like '%{referencia}%' order by COD").fetchall())
        qtdEncontrada=len(cursorSIGI.execute(f"select * from dbo.CONJUNTOS_GERAL where nomePlanilha like '%{referencia}%' collate Latin1_General_CI_AI or nomeSigi like '%{referencia}%' collate Latin1_General_CI_AI or bairroPlanilha like '%{referencia}%' collate Latin1_General_CI_AI or bairroSigi like '%{referencia}%' collate Latin1_General_CI_AI").fetchall())
        num_paginas = int(qtdEncontrada / linhas) + 2
    return render_template("sigi/conjuntos.html", conjuntos=conjuntos, form=formulario, qtd=qtdEncontrada, referencia=referencia, linhas=linhas, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

@app.route("/ruas-conjuntos/<codConjunto>/<nomeConjunto>") # RUAS DO CONJUNTO
#  OK - PESQUISA CONJUNTOS
def ruasConjunto(codConjunto,nomeConjunto):
    # referenciaConjRua=nome=request.args.get('referenciaConjRua')
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.Ruas_Conjunto where CodConjunto = '{codConjunto}' and NomeConjunto = '{nomeConjunto}' collate Latin1_General_CI_AI order by NomeRua").fetchall()
    qtd=len(ruas)
    num_paginas = int(qtd / linhas) + 2
    return render_template("sigi/ruasConjuntos.html", ruas=ruas, codConjunto=codConjunto, nomeConjunto=nomeConjunto, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

@app.route("/conjunto/imoveis/<codConjunto>/<nomeConjunto>/<rua>/<nomeRua>") # IMÓVEIS POR RUA
#  OK - PESQUISA CONJUNTOS
def imoveisRua(codConjunto, nomeConjunto, rua, nomeRua):
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto = '{codConjunto}' and NomeRua = '{nomeRua}' collate Latin1_General_CI_AI order by CodImovel").fetchall()
    qtd=len(imoveis)
    num_paginas = int(qtd / linhas) + 2
    return render_template("sigi/imoveisRua.html", imoveis=imoveis, rua=rua, nomeConjunto=nomeConjunto, codConjunto=codConjunto, qtd=qtd, nomeRua=nomeRua, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

#  /////////////////////////// ÁREA 3 - SIGI ////////////////////////////////////
@app.route("/ruas") # Cadastro de ruas no SIGI
# OK BUSCA DE RUAS
def ruasGeral():
    nomeRua = request.args.get('referenciaNomeRua')
    print(nomeRua)
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    # ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.ruas where NomeRua like '%{nomeRua}%' collate Latin1_General_CI_AI order by nomeRua").fetchall()
    ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.Ruas_Conjunto where NomeRua like '%{nomeRua}%' collate Latin1_General_CI_AI order by NomeRua").fetchall()
    qtd = cursorSIGI.execute(f"select * from dbo.Ruas_Conjunto where NomeRua like '%{nomeRua}%' collate Latin1_General_CI_AI order by NomeRua").fetchall()
    print(ruas)
    if len(ruas) > 0:
        nomeConjunto = ruas[0][1]
        codConjunto = ruas[0][0]
    else:
        nomeConjunto = ""
        codConjunto = ""
    exibidas=len(ruas)
    qtd=len(qtd)
    num_paginas = int(qtd / linhas) + 2
    return render_template("sigi/ruas.html", ruas=ruas, exibidas=exibidas, qtd=qtd, nomeConjunto=nomeConjunto, codConjunto=codConjunto, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

@app.route("/conjunto/") # Consulta por Imobiliário no SIGI
def imob():
    imob = request.args.get('imob')
    conj = request.args.get('conj')
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto like '%{conj}%' and CodImovel like '%{imob}%' order by CodImovel").fetchall()
    qtd = cursorSIGI.execute(f"select * from dbo.Dados_Imovel_Morador where CodConjunto like '%{conj}%' and CodImovel like '%{imob}%' order by CodImovel").fetchall()
    exibidos=len(imoveis)
    qtd=len(qtd)
    num_paginas = int(qtd / linhas) + 2
    return render_template("sigi/imoveisRua.html", imoveis=imoveis, exibidos=exibidos, imob=imob, conjunto=conj, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

@app.route("/mutuario") # Consulta de imóveis por mutuário no SIGI
def imoveisMutuario():
    print('mutuarios')
    imoveisMutuario = request.args.get('imoveisMutuario')
    # cursor = conecta(driver, server, 'Dados_Sigi')
    pagina = int(request.args.get('page', 1))
    linhas = 500
    offset = (pagina - 1) * linhas
    imoveis = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where NomeMorador like '%{imoveisMutuario}%' collate Latin1_General_CI_AI order by NomeMorador").fetchall()
    qtdEncontrada = cursorSIGI.execute(f"select * from dbo.Dados_Imovel_Morador where NomeMorador like '%{imoveisMutuario}%' collate Latin1_General_CI_AI").fetchall()
    qtdEncontrada = len(qtdEncontrada)
    qtd=len(imoveis)
    num_paginas = int(qtd / linhas) + 2
    return render_template("sigi/imoveisMutuario.html", imoveis=imoveis, qtd=qtd, qtdTotal=qtdEncontrada, imoveisMutuario=imoveisMutuario, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

@app.route("/consultaGeral")
def consultaSigiGeral():
    consultaCodCj = request.args.get('consultaCodCj')
    consultaNomeCj = request.args.get('consultaNomeCj')
    consultaNomeMut = request.args.get('consultaNomeMut')
    consultaNomeRua = request.args.get('consultaNomeRua')
    consultaNum = request.args.get('consultaNum')
    consultaImob = request.args.get('consultaImob')
    imoveis = cursorSIGI.execute(f"select top {linhas} * from Dados_Imovel_Morador where"
                                    f" CodConjunto like '%{consultaCodCj}%' and"
                                    f" NomeConjunto like '%{consultaNomeCj}%' collate Latin1_General_CI_AI and"
                                    f" NomeMorador like '%{consultaNomeMut}%' collate Latin1_General_CI_AI and"
                                    f" NomeRua like '%{consultaNomeRua}%' collate Latin1_General_CI_AI and"
                                    f" Numero like '%{consultaNum}%' and"
                                    f" CodImovel like '%{consultaImob}%'"
                                    f" order by NomeConjunto, NomeRua, Numero").fetchall()
    qtd = cursorSIGI.execute(f"select * from Dados_Imovel_Morador where"
                                    f" CodConjunto like '%{consultaCodCj}%' and"
                                    f" NomeConjunto like '%{consultaNomeCj}%' collate Latin1_General_CI_AI and"
                                    f" NomeMorador like '%{consultaNomeMut}%' collate Latin1_General_CI_AI and"
                                    f" NomeRua like '%{consultaNomeRua}%' collate Latin1_General_CI_AI and"
                                    f" Numero like '%{consultaNum}%' and"
                                    f" CodImovel like '%{consultaImob}%'"
                                    f" order by NomeConjunto, NomeRua, Numero").fetchall()
    qtdExibida = len(imoveis)
    qtd = len(qtd)
    return render_template("sigi/consultaGeral.html", imoveis=imoveis, qtdExibida=qtdExibida, qtdTotal=qtd, consultaCodCj=consultaCodCj, consultaNomeCj=consultaNomeCj, consultaNomeMut=consultaNomeMut,consultaNomeRua=consultaNomeRua,consultaNum=consultaNum, consultaImob=consultaImob, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/ficha/<cj>/<imb>")
def ficha(cj,imb):
    ficha=cj + imb + '.pdf'
    return render_template("sigi/ficha.html", ficha=ficha)
@app.route("/dossie/<cj>/<imb>")
def dossie(cj,imb):
    dossie=cj + imb + '.pdf'
    return render_template("sigi/dossie.html", dossie=dossie)


#  /////////////////////////// ÁREA 4 - RESUMO ////////////////////////////////////
@app.route("/resumo") # Mesclagem SIGI x Prefeitura
def resumo():
    referenciaCodCJ = request.args.get('referenciaCodCJ')
    referenciaRua = request.args.get('referenciaRua')
    pagina = int(request.args.get('page', 1))
    linhas = 300
    offset = (pagina - 1) * linhas
    # if referenciaCodCJ:
    #     resumo = cursorCL.execute(f"select top {linhas} * from dbo.resumo where codConjunto like '%{referenciaCodCJ}%' order by NomeConjunto, ruaPLANILHA").fetchall()
    #     # resumo = cursorCL.execute(f"select * from dbo.resumo where codConjunto like '%{referenciaCodCJ}%' order by NomeConjunto, ruaPLANILHA OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
    #     qtd = cursorCL.execute(f"select * from dbo.resumo where codConjunto like '%{referenciaCodCJ}%'").fetchall()
    # else:
    resumo = cursorCL.execute(f"select top {linhas} * from dbo.Junta_IPTU_DADOS_SIGI where rua like '%{referenciaRua}%' collate Latin1_General_CI_AI and codConjunto like '%{referenciaCodCJ}%' order by NomeConjunto, rua").fetchall()
    # resumo = cursorCL.execute(f"select * from dbo.resumo where RuaPLANILHA like '%{referenciaRua}%' order by NomeConjunto, ruaPLANILHA OFFSET {offset} ROWS FETCH NEXT {linhas} ROWS ONLY").fetchall()
    qtd = cursorCL.execute(f"select * from dbo.Junta_IPTU_DADOS_SIGI where rua like '%{referenciaRua}%' collate Latin1_General_CI_AI").fetchall()
    # conjuntos = cursor.execute(f"select * from dbo.resumo where NomeConjunto like '%{referencia}%' order by NomeConjunto").fetchall()
    qtdEncontrada = len(resumo)
    qtd = len(qtd)
    # resumo2 = pd.DataFrame(resumo,columns=['CodConjunto','NomeConjunto','BairroPlanilha','BairroIPTU','RuaPLANILHA','RuaSIGI','CL','inscricao','Número','Imób','Lg','ContribuinteIPTU','ContribuintePLANILHA','dados'])
    # resumo2=pd.DataFrame(resumo)
    num_paginas = int(qtd / linhas) + 2
    return render_template("resumo/resumo.html", resumo=resumo, qtd=qtdEncontrada, qtdTotal=qtd, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)

#  /////////////////////////// COMPLEMENTOS ////////////////////////////////////
@app.route("/conjunto/<codConjunto>/<nomeConjunto>") # DETALHES DO CONJUNTO
def conjunto(codConjunto, nomeConjunto):
    # cursor = conecta(driver, server, 'Dados_Sigi')
    conjunto = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where COD = '{codConjunto}'").fetchall()
    return render_template("sigi/conjunto.html", conjunto=conjunto, codConjunto=codConjunto, nomeConjunto=nomeConjunto, localAcesso=localAcesso, status=status, nome=nome)

@app.route("/<codConjunto>/<codImob>") # DETALHES DO IMÓVEL
def detalhesImovel(codConjunto,codImob):
    imovel = cursorSIGI.execute(f"select top {linhas} * from dbo.Dados_Imovel_Morador where CodConjunto = '{codConjunto}' and CodImovel = '{codImob}'").fetchall()
    return render_template("sigi/detalhesImovel.html", conjunto=conjunto, imovel=imovel, localAcesso=localAcesso, status=status, nome=nome)

#  /////////////////////////// CPF ////////////////////////////////////

@app.route("/cpf") # CPF
def cpf():
    from random import randint
    verNome=request.args.get('verNome')
    cpf=request.args.get('cpf')[0:9]
    gerar=request.args.get('gerar')
    # if gerar:
    if (len(cpf)==0):
        a = randint(0, 9)
        b = randint(0, 9)
        c = randint(0, 9)
        d = randint(0, 9)
        e = randint(0, 9)
        f = randint(0, 9)
        g = randint(0, 9)
        h = randint(0, 9)
        i = randint(0, 9)
    else:
        cpf = int(cpf)
        a = cpf // 100000000 % 10
        b = cpf // 10000000 % 10
        c = cpf // 1000000 % 10
        d = cpf // 100000 % 10
        e = cpf // 10000 % 10
        f = cpf // 1000 % 10
        g = cpf // 100 % 10
        h = cpf // 10 % 10
        i = cpf // 1 % 10

    soma = (a * 10) + (b * 9) + (c * 8) + (d * 7) + (e * 6) + (f * 5) + (g * 4) + (h * 3) + (i * 2)
    if ((soma % 11) <= 1):
        x = 0
    else:
        x = 11 - (soma % 11)
    soma = (a * 11) + (b * 10) + (c * 9) + (d * 8) + (e * 7) + (f * 6) + (g * 5) + (h * 4) + (i * 3) + (
            x * 2)
    if ((soma % 11) <= 1):
        z = 0
    else:
        z = 11 - (soma % 11)
    respCpf = f"{a}{b}{c}.{d}{e}{f}.{g}{h}{i}-{x}{z}"
    if (i == 1):
        uf = 'Distrito Federal, Goiás, Mato Grosso do Sul ou Tocantins'
    elif (i == 2):
        uf = 'Pará, Amazonas, Acre, Amapá, Rondônia ou Roraima'
    elif (i == 3):
        uf = 'Ceará, Maranhão ou Piauí'
    elif (i == 4):
        uf = 'Pernambuco, Rio Grande do Norte, Paraíba ou Alagoas'
    elif (i == 5):
        uf = 'Bahia ou Sergipe'
    elif (i == 6):
        uf = 'Minas Gerais'
    elif (i == 7):
        uf = 'Rio de Janeiro ou Espírito Santo'
    elif (i == 8):
        uf = 'São Paulo'
    elif (i == 9):
        uf = 'Paraná ou Santa Catarina'
    elif (i == 0):
        uf = 'Rio Grande do Sul'
    else:
        uf = 'Não identificado'
    if verNome:
        nome = encontraNome(respCpf)
    else:
        nome = ''
    return render_template("outros/cpf.html", cpf=respCpf, verNome=nome, uf=uf)

def encontraNome(CPF):
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument('--headless=new')
    navegadorCPF = webdriver.Chrome(options=options)
    link = "https://www.situacao-cadastral.com/"
    navegadorCPF.get(link)
    navegadorCPF.find_element(By.ID, 'doc').send_keys(CPF)
    navegadorCPF.find_element(By.ID, 'consultar').click()
    if len(navegadorCPF.find_elements(By.XPATH, '//*[@id="resultado"]/span[2]'))>0:
        nome = navegadorCPF.find_element(By.XPATH, '//*[@id="resultado"]/span[2]').text
        situacao = navegadorCPF.find_element(By.XPATH, '//*[@id="resultado"]/span[3]/span').text
    else:
        nome="Não identificado"
        situacao="Não identificado"
    time.sleep(3)
    navegadorCPF.close()
    navegadorCPF.quit()
    return [nome,situacao]

# @app.route("/bairro") # Conjuntos por Bairro
# def bairro():
#     bairro = request.args.get('bairro')
#     pagina = int(request.args.get('page', 1))
#     linhas = 500
#     offset = (pagina - 1) * linhas
#     # cursor = conecta(driver, server, 'Dados_Sigi')
#     conjuntos = cursorSIGI.execute(f"select top {linhas} * from dbo.CONJUNTOS_GERAL where bairroPlanilha like '%{bairro}%' collate Latin1_General_CI_AI or bairroSIGI like '%{bairro}%' collate Latin1_General_CI_AI order by bairroPlanilha").fetchall()
#     qtd=len(conjuntos)
#     num_paginas = int(qtd / linhas) + 2
#     return render_template("sigi/conjuntos.html", conjuntos=conjuntos, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)
#
# @app.route("/conjunto/ruas/<codConjunto>") # RUAS DO CONJUNTO
# def ruas(codConjunto):
#     pagina = int(request.args.get('page', 1))
#     linhas = 500
#     offset = (pagina - 1) * linhas
#     ruas = cursorSIGI.execute(f"select top {linhas} * from dbo.ruas where CodConjunto = '{codConjunto}' order by nomeRua").fetchall()
#     qtd=len(ruas)
#     num_paginas = int(qtd / linhas) + 2
#     return render_template("sigi/ruasConjuntos.html", ruas=ruas, codConjunto=codConjunto, qtd=qtd, localAcesso=localAcesso, status=status, nome=nome, num_paginas=num_paginas, pagina=pagina)
#
