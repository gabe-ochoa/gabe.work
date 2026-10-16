"use strict";
const morning = document.querySelector("[data-morning]");
if (morning) {
  const steps = [...morning.querySelectorAll("[data-step]")];
  let current = 0;
  const back = morning.querySelector("[data-back]");
  const next = morning.querySelector("[data-next]");
  const render = () => {
    steps.forEach((step, i) => { step.hidden = i !== current; });
    back.disabled = current === 0;
    next.disabled = current === steps.length - 1;
    morning.querySelector("[data-progress]").textContent = `Step ${current + 1} of ${steps.length}. Fictional example.`;
  };
  back.addEventListener("click", () => { current = Math.max(0, current - 1); render(); });
  next.addEventListener("click", () => { current = Math.min(steps.length - 1, current + 1); render(); });
  morning.querySelector("[data-reset]").addEventListener("click", () => { current = 0; render(); });
  morning.querySelector(".controls").hidden = false;
  render();
}
const cli = document.querySelector("[data-cli]");
if (cli) {
  const handlers = new Map([
    ["storage", "Selected handler: inspectStorage. In the real tool, this would collect volume and mount health through a named read-only operation."],
    ["network", "Selected handler: inspectNetwork. This label is valid, but the evidence supports storage. A bounded choice can still be a bad judgment."]
  ]);
  cli.querySelector(".controls").hidden = false;
  cli.querySelector("[data-run]").addEventListener("click", () => {
    const choice = cli.querySelector("select").value;
    const label = choice === "unknown" ? null : choice === "invalid" ? "repair_everything" : choice;
    cli.querySelector("[data-model]").textContent = choice === "unavailable" ? "Inference unavailable: no response received." : JSON.stringify({label}, null, 2);
    cli.querySelector("[data-result]").textContent = choice === "unavailable" ? "Unresolved. Keep the evidence; no handler selected." : label === null ? "Abstained. No handler selected. Ask for more evidence or use the caller’s documented safe fallback." : handlers.has(label) ? handlers.get(label) + " Demo only: nothing was executed." : "Rejected: label is outside the allowed options. No handler selected.";
  });
}
