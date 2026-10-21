// Card artwork: https://github.com/block52/cards (MIT)
const CARD_CDN = "https://raw.githubusercontent.com/block52/cards/main/";
const RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];
const SUITS = ["S", "H", "D", "C"];
const cardState = {
  community: [null, null, null, null, null],
  players: [[null, null], [null, null]]
};
const dialog = document.getElementById("card-dialog");
const picker = document.getElementById("card-picker");
let activeSlot = null;
let latestRequest = 0;

function cardUrl(code) { return `${CARD_CDN}${code}.svg`; }
function getSlot(group, index, player) {
  return group === "community" ? cardState.community[index] : cardState.players[player][index];
}
function setSlot(group, index, player, code) {
  if (group === "community") cardState.community[index] = code;
  else cardState.players[player][index] = code;
}
function makeSlot(group, index, player = null) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "card-slot";
  button.addEventListener("click", () => openPicker(group, index, player));
  return button;
}
function initSlots() {
  const community = document.getElementById("community");
  for (let i = 0; i < 5; i++) community.appendChild(makeSlot("community", i));
  for (let p = 0; p < 2; p++) {
    const target = document.getElementById(`player${p + 1}`);
    for (let i = 0; i < 2; i++) target.appendChild(makeSlot("player", i, p));
  }
  renderSlots();
}
function drawSlot(button, code, label) {
  button.replaceChildren();
  button.setAttribute("aria-label", `${label}: ${code || "未選択"}、クリックして選択・変更`);
  if (!code) {
    button.textContent = "+";
    return;
  }
  const img = document.createElement("img");
  img.src = cardUrl(code);
  img.alt = code;
  img.onerror = () => { img.replaceWith(document.createTextNode(code)); };
  button.appendChild(img);
}
function renderSlots() {
  [...document.querySelectorAll("#community .card-slot")].forEach((button, i) => {
    drawSlot(button, cardState.community[i], `コミュニティカード ${i + 1}`);
  });
  for (let p = 0; p < 2; p++) {
    [...document.querySelectorAll(`#player${p + 1} .card-slot`)].forEach((button, i) => {
      drawSlot(button, cardState.players[p][i], `プレイヤー ${p + 1} のハンド ${i + 1}`);
    });
  }
}
function usedCards() {
  return new Set([...cardState.community, ...cardState.players.flat()].filter(Boolean));
}
function openPicker(group, index, player) {
  activeSlot = { group, index, player };
  const occupied = usedCards();
  picker.replaceChildren();
  for (const suit of SUITS) {
    for (const rank of RANKS) {
      const code = rank + suit;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "pick-card";
      button.disabled = occupied.has(code);
      button.title = code;
      button.setAttribute("aria-label", code);
      const img = document.createElement("img");
      img.src = cardUrl(code);
      img.alt = code;
      img.loading = "lazy";
      img.onerror = () => { img.replaceWith(document.createTextNode(code)); };
      button.appendChild(img);
      button.addEventListener("click", () => {
        setSlot(group, index, player, code);
        dialog.close();
        onCardsChanged();
      });
      picker.appendChild(button);
    }
  }
  dialog.showModal();
}
function showRates(rate1, rate2) {
  for (const [i, rate] of [rate1, rate2].entries()) {
    document.getElementById(`fill${i + 1}`).style.width = rate === null ? "0%" : `${rate}%`;
    document.getElementById(`rate${i + 1}`).textContent = rate === null ? "--" : `${Number(rate.toFixed(2))}%`;
  }
}
async function onCardsChanged() {
  renderSlots();
  const requestId = ++latestRequest;
  document.getElementById("status").textContent = "比較中...";
  showRates(null, null);
  try {
    const response = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cardState)
    });
    const data = await response.json();
    if (requestId !== latestRequest) return;
    if (!response.ok) throw new Error(data.error || "リクエストに失敗しました");
    if (data.ready) showRates(data.player1, data.player2);
    document.getElementById("status").textContent = data.message;
  } catch (error) {
    if (requestId !== latestRequest) return;
    document.getElementById("status").textContent = error.message;
  }
}
document.getElementById("close-dialog").addEventListener("click", () => dialog.close());
document.getElementById("clear-slot").addEventListener("click", () => {
  if (activeSlot) {
    setSlot(activeSlot.group, activeSlot.index, activeSlot.player, null);
    dialog.close();
    onCardsChanged();
  }
});
initSlots();