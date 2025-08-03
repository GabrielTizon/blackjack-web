import random
import os
from PIL import Image

# pasta base das cartas
CAMINHO_CARTAS = "cartas"

# mapeamentos
NAIPE_MAP = {'C':'clubs','D':'diamonds','H':'hearts','S':'spades'}
VALOR_MAP = {'A':'ace','J':'jack','Q':'queen','K':'king'}

def criar_baralho():
    valores = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    naipes  = ['C','D','H','S']
    baralho = [v+n for v in valores for n in naipes]
    random.shuffle(baralho)
    return baralho

def valor_carta(carta):
    v = carta[:-1]
    if v in ('J','Q','K'): return 10
    if v == 'A':           return 11
    return int(v)

def calcular_pontos(mao):
    pts = sum(valor_carta(c) for c in mao)
    ases = sum(1 for c in mao if c[:-1]=='A')
    while pts>21 and ases:
        pts -= 10; ases -=1
    return pts

def encontra_arquivo(nome_arquivo):
    """
    Busca recursivamente por nome_arquivo dentro de CAMINHO_CARTAS.
    Retorna o caminho completo ou None.
    """
    for raiz, _, arquivos in os.walk(CAMINHO_CARTAS):
        if nome_arquivo in arquivos:
            return os.path.join(raiz, nome_arquivo)
    return None

def carregar_imagem_pil(carta):
    if carta == '?':
        return None
    v, n = carta[:-1], carta[-1]
    valor = VALOR_MAP.get(v, v.lower())
    naipe = NAIPE_MAP[n]
    nome_arquivo = f"{valor}_of_{naipe}.png"
    caminho = encontra_arquivo(nome_arquivo)
    if not caminho:
        raise FileNotFoundError(f"Não achei '{nome_arquivo}' dentro de '{CAMINHO_CARTAS}'")
    return Image.open(caminho)

def mostrar_imagem(mao, titulo):
    imgs = [carregar_imagem_pil(c) for c in mao if c!='?']
    if not imgs: return
    widths, heights = zip(*(im.size for im in imgs))
    total_w = sum(widths) + (len(imgs)-1)*10
    max_h   = max(heights)
    comp = Image.new('RGBA', (total_w, max_h), (0,0,0,0))
    x=0
    for im in imgs:
        comp.paste(im, (x,0)); x+=im.width+10
    comp.show(title=titulo)

def mostrar_maos(jogador, dealer, fim=False):
    cj = ' '.join(jogador); pj = calcular_pontos(jogador)
    print(f"\nSuas cartas: {cj} | Pontos: {pj}")
    if fim:
        cd = ' '.join(dealer); pd = calcular_pontos(dealer)
        print(f"Cartas do dealer: {cd} | Pontos: {pd}")
    else:
        print(f"Cartas do dealer: {dealer[0]} ?")
    mostrar_imagem(jogador, "Mão do Jogador")
    mao_d = dealer if fim else [dealer[0]]
    mostrar_imagem(mao_d, "Mão do Dealer")

def jogar_blackjack():
    baralho = criar_baralho()
    jogador = [baralho.pop(), baralho.pop()]
    dealer  = [baralho.pop(), baralho.pop()]

    while True:
        mostrar_maos(jogador, dealer)
        pj = calcular_pontos(jogador)
        if pj==21:
            print("Blackjack! Você venceu!"); return
        if pj>21:
            print("Você estourou!"); return

        escolha = input("Hit ou Stand? [H/S]: ").strip().upper()
        if escolha=='H':
            jogador.append(baralho.pop())
        elif escolha=='S':
            break
        else:
            print("Inválido.")

    while calcular_pontos(dealer)<17:
        dealer.append(baralho.pop())

    mostrar_maos(jogador, dealer, fim=True)
    pj,pd = calcular_pontos(jogador), calcular_pontos(dealer)
    if pd>21 or pj>pd:
        print("Você venceu!")
    elif pj==pd:
        print("Empate.")
    else:
        print("Dealer venceu.")

if __name__=="__main__":
    while True:
        jogar_blackjack()
        if input("\nJogar de novo? (s/n): ").strip().lower()!='s':
            break
