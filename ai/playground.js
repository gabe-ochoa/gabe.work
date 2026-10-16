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
  const handlers = new Map([["storage", "inspectStorage"], ["network", "inspectNetwork"]]);
  const storage = cli.querySelector("#storage-evidence");
  const network = cli.querySelector("#network-evidence");
  const response = cli.querySelector("#response");
  const decide = () => storage.value === "failed" && network.value !== "failed" ? "storage" : network.value === "failed" && storage.value !== "failed" ? "network" : null;
  const render = () => {
    const suggested = decide();
    const choice = response.value;
    const label = choice === "auto" ? suggested : choice === "unknown" ? null : choice === "invalid" ? "repair_everything" : choice;
    const gap = storage.value === "unknown" || network.value === "unknown";
    cli.querySelector("[data-evidence]").textContent = `Storage: ${storage.selectedOptions[0].textContent}. Network: ${network.selectedOptions[0].textContent}.` + (gap ? " Evidence is incomplete." : "");
    cli.querySelector("[data-model]").textContent = choice === "unavailable" ? "Inference unavailable: no response received." : "Simulated response: " + JSON.stringify({label}, null, 2);
    let result;
    if (choice === "unavailable") result = "Unresolved. Keep the evidence; no handler selected.";
    else if (label === null) result = "Abstained. No handler selected. Ask for more evidence or use the caller’s documented safe fallback.";
    else if (!handlers.has(label)) result = "Rejected: label is outside the allowed options. No handler selected.";
    else {
      result = `Selected handler: ${handlers.get(label)}.`;
      if (label !== suggested) result += " This is an allowed label, but it disagrees with the demo rules for the current evidence. A valid response can still be a bad judgment.";
      if (gap) result += " An unchecked subsystem remains an evidence gap.";
      result += " Demo only: nothing was executed.";
    }
    cli.querySelector("[data-result]").textContent = result;
  };
  cli.querySelectorAll("select").forEach(select => select.addEventListener("change", render));
  cli.querySelector("[data-run]").addEventListener("click", render);
  cli.querySelector(".controls").hidden = false;
  render();
}
