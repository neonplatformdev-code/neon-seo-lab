"use strict";
const filters = [...document.querySelectorAll("[data-filter]")];
const cards = [...document.querySelectorAll("[data-kind]")];
const count = document.querySelector("#result-count");
for (const button of filters) {
  button.addEventListener("click", () => {
    const selected = button.dataset.filter;
    for (const item of filters) item.setAttribute("aria-pressed", String(item === button));
    let visible = 0;
    for (const card of cards) {
      card.hidden = selected !== "all" && card.dataset.kind !== selected;
      if (!card.hidden) visible += 1;
    }
    count.textContent = `Показано сценариев: ${visible} из ${cards.length}`;
  });
}
