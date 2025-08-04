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
