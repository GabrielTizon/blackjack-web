import tkinter as tk
from tkinter import PhotoImage
import random
import os

CAMINHO_CARTAS = "cartas"

# --- Cria o baralho lendo as imagens disponíveis, sem jokers ---
def criar_baralho():
    arquivos = os.listdir(CAMINHO_CARTAS)
    baralho = []
    for fn in arquivos:
        nome, ext = os.path.splitext(fn)
        n = nome.upper()
        if ext.lower() != '.png':
            continue
        if n in ('BACK', 'BLACK_JOKER', 'RED_JOKER'):
            continue
        baralho.append(n)
    random.shuffle(baralho)
    return baralho

def valor_carta(carta):
    v = carta[:-1]
    if v in ('J','Q','K'):
        return 10
    if v == 'A':
        return 11
    return int(v)

def calcular_pontos(mao):
    pontos = sum(valor_carta(c) for c in mao)
    ases = sum(1 for c in mao if c[:-1] == 'A')
    while pontos > 21 and ases:
        pontos -= 10
        ases  -= 1
    return pontos

# --- Setup GUI ---
janela = tk.Tk()
janela.title("Blackjack com Imagens (Sem Jokers)")
janela.geometry("800x600")

# Cache de imagens e verso (agora que já temos root criado)
imagens_cartas = {}
carta_imagem_oculta = PhotoImage(file=os.path.join(CAMINHO_CARTAS, "BACK.png"))

def carregar_imagem(carta):
    if carta == '?':
        return carta_imagem_oculta
    if carta not in imagens_cartas:
        imagens_cartas[carta] = PhotoImage(file=os.path.join(CAMINHO_CARTAS, f"{carta}.png"))
    return imagens_cartas[carta]

def mostrar_maos():
    for w in frame_jogador.winfo_children():
        w.destroy()
    for w in frame_dealer.winfo_children():
        w.destroy()

    for carta in jogador:
        img = carregar_imagem(carta)
        tk.Label(frame_jogador, image=img).pack(side="left", padx=2)

    for idx, carta in enumerate(dealer):
        img = carregar_imagem('?') if (not mostrar_dealer and idx == 1) else carregar_imagem(carta)
        tk.Label(frame_dealer, image=img).pack(side="left", padx=2)

    lbl_pontos_jogador.config(text=f"Pontos Jogador: {calcular_pontos(jogador)}")
    lbl_pontos_dealer.config(
        text=f"Pontos Dealer: {calcular_pontos(dealer)}" if mostrar_dealer else "Pontos Dealer: ?"
    )

def verificar_resultado():
    global mostrar_dealer
    mostrar_dealer = True
    while calcular_pontos(dealer) < 17:
        dealer.append(baralho.pop())
    mostrar_maos()

    pj, pd = calcular_pontos(jogador), calcular_pontos(dealer)
    if pj > 21:
        texto = "Você estourou! 😢"
    elif pd > 21 or pj > pd:
        texto = "Você venceu! 🏆"
    elif pj == pd:
        texto = "Empate!"
    else:
        texto = "Dealer venceu. 😔"

    lbl_resultado.config(text=texto)
    btn_hit.config(state="disabled")
    btn_stand.config(state="disabled")
    btn_novo.config(state="normal")

def hit():
    jogador.append(baralho.pop())
    mostrar_maos()
    if calcular_pontos(jogador) > 21:
        verificar_resultado()

def stand():
    verificar_resultado()

def novo_jogo():
    global baralho, jogador, dealer, mostrar_dealer
    baralho = criar_baralho()
    jogador = [baralho.pop(), baralho.pop()]
    dealer  = [baralho.pop(), baralho.pop()]
    mostrar_dealer = False
    lbl_resultado.config(text="")
    mostrar_maos()
    btn_hit.config(state="normal")
    btn_stand.config(state="normal")
    btn_novo.config(state="disabled")

# Dealer
tk.Label(janela, text="Dealer:", font=("Arial", 14)).pack(pady=(10,0))
frame_dealer = tk.Frame(janela)
frame_dealer.pack()
lbl_pontos_dealer = tk.Label(janela, text="Pontos Dealer: ?", font=("Arial", 12))
lbl_pontos_dealer.pack(pady=(0,10))

# Jogador
tk.Label(janela, text="Jogador:", font=("Arial", 14)).pack()
frame_jogador = tk.Frame(janela)
frame_jogador.pack()
lbl_pontos_jogador = tk.Label(janela, text="Pontos Jogador: 0", font=("Arial", 12))
lbl_pontos_jogador.pack(pady=(0,10))

# Resultado e botões
lbl_resultado = tk.Label(janela, text="", font=("Arial", 16), fg="blue")
lbl_resultado.pack(pady=10)
btn_hit   = tk.Button(janela, text="Hit",   command=hit,   width=15)
btn_stand = tk.Button(janela, text="Stand", command=stand, width=15)
btn_novo  = tk.Button(janela, text="Novo Jogo", command=novo_jogo, width=15)
btn_hit.pack(pady=5)
btn_stand.pack(pady=5)
btn_novo.pack(pady=5)

# Inicia o jogo
baralho = []
jogador = []
dealer  = []
mostrar_dealer = False
novo_jogo()

janela.mainloop()
