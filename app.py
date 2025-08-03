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
