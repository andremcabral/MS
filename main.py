# install flask
# pip install flask
# INSTALAR AS DEPENDÊNCIAS >> pip install -r requirements.txt
# importar o aplicativo criado no __init__
from iptu_CEHAB_flask.cadastros import app

#  inicia o programa
# if __name__ == "__main__":
    # RODA APENAS NESTA MÁQUINA
    # app.run(debug=True)
    # RODA NA REDE
app.run(port=4048, host='0.0.0.0', debug=True, threaded=True)
    # app.run(port=5000, host='0.0.0.0', debug=False, threaded=True)
    # app.run(host='0.0.0.0', debug=False)

# pip install auto-py-to-exe
# auto-py-to-exe