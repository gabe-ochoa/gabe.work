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

const reportBuilder = document.querySelector("[data-report-builder]");
if (reportBuilder) {
  const form = reportBuilder.querySelector("form");
  const source = form.querySelector("#report-sources");
  const tour = form.querySelector("#report-tour");
  const equipment = form.querySelector("#report-equipment");
  const output = reportBuilder.querySelector("[data-built-report]");
  const status = reportBuilder.querySelector("[data-report-status]");
  const renderReport = () => {
    output.replaceChildren();
    const add = (tag, content) => {
      const element = document.createElement(tag);
      element.textContent = content;
      output.append(element);
      return element;
    };
    if (source.value === "blocked") {
      add("h3", "Preflight stopped: no report generated");
      add("p", "The required document connection is unavailable. Restore it and rerun preflight before gathering the report. No task list is generated from partial connections.");
      status.textContent = "Preflight blocked. No report generated. Nothing executed.";
      return;
    }
    add("h3", "Proposed morning report");
    const prepare = [];
    const approval = ["Send the workshop announcement. Source: message. Drafting can happen before approval; sending cannot."];
    const personal = ["Have the 10:00 conversation. Source: calendar. The agent can help prepare."];
    const questions = [];
    const blocked = [];
    if (source.value === "ready") prepare.push("Summarize the workshop proposal. Sources: note and message, reconciled into one task; proposal document read successfully.");
    else blocked.push("Proposal summary: the document read failed. Keep the request from the note and message, but do not invent a summary.");
    if (tour.value === "pending") approval.push("Follow up about Thursday’s tour. Sources: note and pending calendar invitation. Ask before contacting the other person.");
    if (equipment.value === "draft") prepare.push("Draft the equipment checklist for review. Source: explicitly delegated note.");
    else if (equipment.value === "send") approval.push("Send the equipment checklist to the group. Source: note. Sending needs separate approval.");
    else questions.push("What outcome is wanted for the equipment question? Source: ambiguous note. Ask rather than guess.");
    const groups = [["Agent can prepare", prepare], ["Needs approval", approval], ["Needs me", personal], ["Needs clarification", questions], ["Blocked on evidence", blocked]];
    for (const [title, rows] of groups) {
      if (!rows.length) continue;
      add("h4", `${title} (${rows.length})`);
      const list = add("ul", "");
      for (const row of rows) {
        const item = document.createElement("li"); item.textContent = row; list.append(item);
      }
    }
    add("h4", "Reconciliation notes");
    add("p", tour.value === "accepted" ? "Tour follow-up removed: both attendees accepted. Duplicate summary requests combined while retaining both source references." : "Tour follow-up retained: the invitation is pending. Duplicate summary requests combined while retaining both source references.");
    add("h4", "Source accounting");
    add("p", "Notes: contributed. Messages: contributed. Calendar: contributed. Documents: " + (source.value === "ready" ? "proposal read successfully. Skipped: none among these four modeled sources." : "proposal read failed; no document contents used. Skipped: proposal document (read failed)."));
    add("p", "Nothing has started or been sent. I choose the next action after reviewing the report.");
    status.textContent = `Report updated: ${prepare.length} preparation, ${approval.length} approval, ${personal.length} personal, ${questions.length} clarification, ${blocked.length} blocked. Nothing executed.`;
  };
  form.addEventListener("change", renderReport);
  form.addEventListener("submit", event => event.preventDefault());
  form.addEventListener("reset", () => { setTimeout(renderReport, 0); });
  form.hidden = false;
  renderReport();
}
