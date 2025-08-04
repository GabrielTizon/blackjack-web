const dealerDiv   = document.getElementById('dealer');
const jogadorDiv  = document.getElementById('jogador');
const pontosD     = document.getElementById('pontos_dealer');
const pontosJ     = document.getElementById('pontos_jogador');
const resultado   = document.getElementById('resultado');
const btnNew      = document.getElementById('btn_new');
const btnHit      = document.getElementById('btn_hit');
const btnStand    = document.getElementById('btn_stand');
const panel       = document.getElementById('panel');
const balanceEl   = document.getElementById('balance');
const inBet       = document.getElementById('input_bet');
const btnBet      = document.getElementById('btn_set_bet');
const inDep       = document.getElementById('input_deposit');
const btnDep      = document.getElementById('btn_deposit');

const VALOR_MAP = {'A':'ace','J':'jack','Q':'queen','K':'king'};
const NAIPE_MAP = {'C':'clubs','D':'diamonds','H':'hearts','S':'spades'};

function cartaSrc(c) {
  if (c === '?') return 'static/cartas/back.png'; // Use minúsculo, igual ao nome do arquivo!
  const v = c.slice(0, -1), n = c.slice(-1);
  const val = VALOR_MAP[v] || v.toLowerCase(), nai = NAIPE_MAP[n];
  return `static/cartas/${val}_of_${nai}.png`;
}

async function atualizar(url) {
  const res = await fetch(url);
  const data = await res.json();

  // Painel
  if (data.balance>0) {
    panel.classList.add('active');
    panel.classList.remove('deposit-mode');
    balanceEl.textContent = data.balance;
    inBet.value = data.bet;
  } else {
    panel.classList.remove('active');
    panel.classList.add('deposit-mode');
  }

  // Dealer
  dealerDiv.innerHTML = '';
  data.dealer.forEach((c,i)=>{
    const slot = document.createElement('div');
    slot.className = 'card-slot';
    if (i===1) {
      const back  = document.createElement('img');
      back.src = 'static/cartas/back.png'; back.className='back';
      const front = document.createElement('img');
      front.src = cartaSrc(c); front.className='front';
      slot.append(back, front);
    } else {
      const img = document.createElement('img');
      img.src = cartaSrc(c); img.className='front';
      slot.append(img);
    }
    dealerDiv.append(slot);
  });
  dealerDiv.className = data.mostrar_dealer?'cards revealed':'cards';
  pontosD.textContent = data.mostrar_dealer?`Pontos: ${data.pontos_dealer}`:'';

  // Jogador
  jogadorDiv.innerHTML = '';
  data.jogador.forEach(c=>{
    const slot = document.createElement('div');
    slot.className='card-slot';
    const img = document.createElement('img');
    img.src = cartaSrc(c); img.className='front';
    slot.append(img);
    jogadorDiv.append(slot);
  });
  pontosJ.textContent = `Pontos: ${data.pontos_jogador}`;

  // Resultado
  resultado.textContent = data.resultado;

  // Controles
  [btnNew, btnHit, btnStand].forEach(btn=>{
    btn.disabled = data.balance<=0;
  });
}

btnBet.onclick   =()=>atualizar(`/bet?valor=${inBet.value}`);
btnDep.onclick   =()=>atualizar(`/deposit?amount=${inDep.value}`);
btnNew.onclick   =()=>atualizar('/new');
btnHit.onclick   =()=>atualizar('/hit');
btnStand.onclick =()=>atualizar('/stand');

// Init
atualizar('/new');
