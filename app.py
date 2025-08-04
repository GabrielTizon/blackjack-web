<<<<<<< HEAD
from flask import Flask, render_template, jsonify, request, session
import random

app = Flask(__name__)
app.secret_key = 'segredo_super_seguro'  # Troque na produção!

# Utilidades
def novo_baralho():
    naipes = 'CDHS'
    valores = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
    baralho = [v + n for n in naipes for v in valores]
    random.shuffle(baralho)
    return baralho

def pontos(mao):
    vals = {'A': 1, 'J': 10, 'Q': 10, 'K': 10}
    soma = 0
    ases = 0
    for c in mao:
        v = c[:-1]
        if v == 'A':
            ases += 1
        # Sempre use .get() e trate o erro:
        if v in vals:
            soma += vals[v]
        else:
            try:
                soma += int(v)
            except:
                soma += 0  # Caso venha algo inesperado
    for _ in range(ases):
        if soma + 10 <= 21:
            soma += 10
    return soma


def inicia_jogo():
    baralho = novo_baralho()
    jogador = [baralho.pop(), baralho.pop()]
    dealer  = [baralho.pop(), baralho.pop()]
    return baralho, jogador, dealer

def get_estado(result=None):
    estado = session.get('bj', None)
    if not estado:
        # Reseta a sessão se corrompida
        baralho, jogador, dealer = inicia_jogo()
        estado = {
            'baralho': baralho,
            'jogador': jogador,
            'dealer': dealer,
            'mostrar_dealer': False,
            'encerrado': False,
            'resultado': ''
        }
        session['bj'] = estado
        if 'balance' not in session: session['balance'] = 1000
        if 'bet' not in session: session['bet'] = 100

    balance = session.get('balance', 1000)
    bet = session.get('bet', 100)
    mostrar_dealer = estado.get('mostrar_dealer', False)
    pontos_dealer = pontos(estado.get('dealer', []))
    pontos_jogador = pontos(estado.get('jogador', []))
    dealer = estado.get('dealer', [])
    jogador = estado.get('jogador', [])
    if not mostrar_dealer and len(dealer) >= 2:
        dealer_vis = [dealer[0], '?']
    else:
        dealer_vis = dealer
    return {
        "balance": balance,
        "bet": bet,
        "dealer": dealer_vis,
        "jogador": jogador,
        "pontos_dealer": pontos_dealer,
        "pontos_jogador": pontos_jogador,
        "mostrar_dealer": mostrar_dealer,
        "resultado": result or estado.get('resultado', "")
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new():
    baralho, jogador, dealer = inicia_jogo()
    session['bj'] = {
        'baralho': baralho,
        'jogador': jogador,
        'dealer': dealer,
        'mostrar_dealer': False,
        'encerrado': False,
        'resultado': ""
    }
    # Só inicia balance e bet se não existirem
    if 'balance' not in session: session['balance'] = 1000
    if 'bet' not in session: session['bet'] = 100
    return jsonify(get_estado())

@app.route('/hit')
def hit():
    estado = session.get('bj', None)
    if not estado:
        return jsonify(get_estado("Erro: sessão não iniciada!"))
    if estado.get('encerrado'):
        return jsonify(get_estado(estado.get('resultado', '')))
    baralho = estado['baralho']
    jogador = estado['jogador']
    if len(baralho) == 0:
        baralho = novo_baralho()
    jogador.append(baralho.pop())
    if pontos(jogador) > 21:
        estado['mostrar_dealer'] = True
        estado['encerrado'] = True
        session['balance'] = session.get('balance', 0) - session.get('bet', 100)
        result = "Estourou! Você perdeu."
        estado['resultado'] = result
        estado['baralho'] = baralho
        estado['jogador'] = jogador
        session['bj'] = estado
        return jsonify(get_estado(result))
    estado['baralho'] = baralho
    estado['jogador'] = jogador
    session['bj'] = estado
    return jsonify(get_estado())

@app.route('/stand')
def stand():
    estado = session.get('bj', None)
    if not estado:
        return jsonify(get_estado("Erro: sessão não iniciada!"))
    if estado.get('encerrado'):
        return jsonify(get_estado(estado.get('resultado', '')))
    baralho = estado['baralho']
    jogador = estado['jogador']
    dealer = estado['dealer']
    if len(baralho) == 0:
        baralho = novo_baralho()
    while pontos(dealer) < 17:
        dealer.append(baralho.pop())
    pts_j = pontos(jogador)
    pts_d = pontos(dealer)
    estado['mostrar_dealer'] = True
    estado['encerrado'] = True
    if pts_d > 21 or pts_j > pts_d:
        session['balance'] = session.get('balance', 0) + session.get('bet', 100)
        result = "Parabéns, você ganhou!"
    elif pts_j < pts_d:
        session['balance'] = session.get('balance', 0) - session.get('bet', 100)
        result = "Dealer ganhou. Você perdeu."
    else:
        result = "Empate!"
    estado['dealer'] = dealer
    estado['resultado'] = result
    estado['baralho'] = baralho
    session['bj'] = estado
    return jsonify(get_estado(result))

@app.route('/bet')
def bet():
    valor = int(request.args.get('valor', 100))
    session['bet'] = valor
    return jsonify(get_estado())

@app.route('/deposit')
def deposit():
    amount = int(request.args.get('amount', 500))
    session['balance'] = session.get('balance', 0) + amount
    return jsonify(get_estado())

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, render_template, jsonify, request
import random, os

app = Flask(__name__)
CAMINHO_CARTAS = os.path.join('static', 'cartas')

NAIPE_MAP  = {'C':'clubs','D':'diamonds','H':'hearts','S':'spades'}
VALOR_MAP  = {'A':'ace','J':'jack','Q':'queen','K':'king'}

jogo = {
    'baralho': [],
    'jogador': [],
    'dealer': [],
    'mostrar_dealer': False,
    'resultado': '',
    'balance': 1000,
    'bet': 0
}

def criar_baralho():
    valores = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    naipes  = ['C','D','H','S']
    b = [v+n for v in valores for n in naipes]
    random.shuffle(b)
    return b

def valor_carta(c):
    v = c[:-1]
    if v in ('J','Q','K'): return 10
    if v == 'A':           return 11
    return int(v)

def calcular_pontos(mao):
    pts  = sum(valor_carta(c) for c in mao)
    ases = sum(1 for c in mao if c[:-1]=='A')
    while pts>21 and ases:
        pts -= 10; ases -=1
    return pts

def estado_jogo():
    return {
        'jogador': jogo['jogador'],
        'dealer': jogo['dealer'] if jogo['mostrar_dealer'] else [jogo['dealer'][0]],
        'mostrar_dealer': jogo['mostrar_dealer'],
        'pontos_jogador': calcular_pontos(jogo['jogador']),
        'pontos_dealer': calcular_pontos(jogo['dealer']) if jogo['mostrar_dealer'] else None,
        'resultado': jogo['resultado'],
        'balance': jogo['balance'],
        'bet': jogo['bet']
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/deposit')
def deposit():
    try:
        amt = int(request.args.get('amount', 0))
    except:
        amt = 0
    if amt > 0:
        jogo['balance'] += amt
        jogo['resultado'] = f"Você depositou {amt}."
    return jsonify(estado_jogo())

@app.route('/bet')
def set_bet():
    valor = int(request.args.get('valor', 0))
    valor = max(0, min(valor, jogo['balance']))
    jogo['bet'] = valor
    jogo['resultado'] = ''
    return jsonify(estado_jogo())

@app.route('/new')
def new_game():
    if jogo['balance'] <= 0:
        jogo['resultado'] = "Saldo zerado. Deposite para jogar."
        return jsonify(estado_jogo())
    if jogo['bet'] <= 0:
        jogo['resultado'] = "Defina uma aposta para começar!"
        return jsonify(estado_jogo())
    jogo['baralho'] = criar_baralho()
    jogo['jogador'] = [jogo['baralho'].pop(), jogo['baralho'].pop()]
    jogo['dealer']  = [jogo['baralho'].pop(), jogo['baralho'].pop()]
    jogo['mostrar_dealer'] = False
    jogo['resultado'] = ''
    return jsonify(estado_jogo())

@app.route('/hit')
def hit():
    if jogo['balance'] <= 0 or not jogo['bet'] or jogo['resultado']:
        return jsonify(estado_jogo())
    jogo['jogador'].append(jogo['baralho'].pop())
    if calcular_pontos(jogo['jogador']) >= 21:
        return stand()
    return jsonify(estado_jogo())

@app.route('/stand')
def stand():
    if jogo['balance'] <= 0 or not jogo['bet'] or jogo['resultado']:
        return jsonify(estado_jogo())
    jogo['mostrar_dealer'] = True
    while calcular_pontos(jogo['dealer']) < 17:
        jogo['dealer'].append(jogo['baralho'].pop())
    pj = calcular_pontos(jogo['jogador'])
    pd = calcular_pontos(jogo['dealer'])
    if pj > 21:
        jogo['resultado'] = "Você estourou! 😓"
        jogo['balance'] -= jogo['bet']
    elif pd > 21 or pj > pd:
        jogo['resultado'] = "Você venceu! 🏆"
        jogo['balance'] += jogo['bet']
    elif pj == pd:
        jogo['resultado'] = "Empate."
    else:
        jogo['resultado'] = "Dealer venceu. 😔"
        jogo['balance'] -= jogo['bet']
    return jsonify(estado_jogo())

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> f4da73fb906c82eebdfaa91ec18db3519ffd8ce1
