---
title: Building a homelab my AI operates, part 5: the control-plane loop
date: 2026-07-26
description: The finale. I gave a 30B model kubectl, a GitHub token, and write access to my cluster. It has not fixed anything yet, and that is the most useful thing it has taught me.
draft: false
slug: homelab-ai-operated-part-5-control-plane
---

A few months ago I gave a 30-billion-parameter model `kubectl`, a GitHub token, and write access to my Kubernetes cluster. It has not fixed anything yet.

That is the finale of this series, and I have been holding that line since [part 1](/how/homelab-ai-operated-part-1-bootstrapping/) on purpose. By now you know the ground it stands on: the [develop loop](/how/homelab-ai-operated-part-2-develop-deploy-review/), the [infrastructure](/how/homelab-ai-operated-part-3-infrastructure/), and [how we fix problems by hand](/how/homelab-ai-operated-part-4-fixing-problems/). This post is the autonomous part. The agent that watches the cluster and is allowed to act on its own.

The headline sounds like a confession of failure. It is the opposite. An agent that can push to `master` and chooses not to, almost every time, is exactly what I was trying to build. Let me show you why, and how.

## It was built twice

The honest history first, because it is the whole thesis in one fact.

The first version of this control plane was scrapped. I opened the pull request, read my own design, and closed it without merging. That first design called a frontier model over the API and opened a pull request for every change it wanted to make. It was reasonable. It was also more eager and more expensive than I was comfortable turning loose.

The version running today is the second one, and it is deliberately more conservative. It runs a local model. It commits directly to `master`, but only through a set of constraints I will walk through. The reversal from the first design to the second, more cloud-power and more process to less power and tighter budgets, is the lesson. You do not earn autonomy by giving the agent more. You earn it by giving it less, with sharper edges, and widening the gap only as the track record justifies it.

When it came back, it came back in standby: it booted, it observed, and it did nothing at all until I added credentials. The agent's first live state was "watch and report." Acting came later, and grudgingly.

## Three loops

The control plane is three concurrent loops that share per-problem state.

| Loop | Cadence | Job |
|---|---|---|
| Fast | 30s | Observe the cluster, fingerprint problems, run rule-based triage, wake the deep loop only for signals worth a model call |
| Deep | event-driven | One model turn per actionable problem. A tool-use loop that ends in a decision |
| Slow | 600s | Re-queue escalated problems, prune resolved state |

Most of the system is the fast loop and the slow loop, and neither of them is intelligent. They are plain code. The model only runs in the deep loop, and the deep loop only runs when the other two decide it should. That ordering is the entire cost and safety story.

## Fingerprint first

Every problem gets a stable identity before anything else happens:

```
fingerprint = kind:namespace:name:issue_class
```

For example `Pod:homelab-apps:zot:CrashLoopBackOff`. That string is the unit of work. State keys off it. Budgets key off it. The audit log keys off it. Learning keys off it. Without a stable fingerprint you cannot deduplicate a problem, you cannot budget how often you act on it, and you cannot tell whether a fix worked. If you have used a Datadog monitor, this is the group-by tag. I did not invent a data model. I named the one that was already there.

## Triage before reason

This is the most important idea in the whole series, and the one most people skip. Before the model is ever woken, a rule-based classifier looks at each new problem and emits one of four verdicts:

| Verdict | Meaning | Tokens |
|---|---|---|
| `suppress` | Below the bar. A pod restarted once. Ignore it | 0 |
| `escalate` | Known to be unfixable by the agent's tools. A node's overlay is down (see part 4) | 0 |
| `autofix` | Matches a proven recipe. Just run it | 0 |
| `reason` | None of the above. Wake the model | many |

A control plane is a classifier with consequences. The reasoning is the expensive fallback for the small residual that does not classify cleanly. The interesting engineering is not "can the model fix it." It is "how does the system decide which problems need the model at all." Most do not. A node going `NotReady` does not need a language model to tell you it is broken. The cheapest token is the one you never spend, and triage is how you avoid spending it.

## The authority ladder

When a problem does reach the model, the model can reach for exactly a few tools, ordered by how much damage they could do.

1. **In-cluster, drift-only.** Delete a pod, restart a rollout, force a Flux reconcile. The controllers self-heal toward the declared state. Lowest blast radius.
2. **Commit to `master`.** A direct push. Flux reconciles it in minutes. This is the path for a durable fix, a real change to the desired state.
3. **Raise an incident.** Surface a card for me, with the diagnosis and the suggested fix. Informational, not blocking. This is what it does when the fix is outside its reach, like the host-level command from part 4.

A direct push to `master` with no human review is the part that makes people flinch. It does not make me flinch, because the architecture wraps it in constraints a hand-written automation script would never have. These are the real values from the config:

- **A rolling commit budget.** Three commits per fingerprint per hour. Twenty across the whole cluster per hour. When the budget is spent, the commit tool refuses and forces an escalation instead. The agent physically cannot panic-push a hundred fixes.
- **A first-observation debounce.** It will not act until it has seen a problem at least twice. The first sighting of anything is never actionable. This kills the reflex to react to a single flapping pod.
- **Verify windows.** After it acts, the state machine refuses to retry the same action until the previous attempt has had time to land: two minutes for an in-cluster action, fifteen for a commit. It cannot spin.
- **GitOps as the action surface.** Every durable fix is a commit, which means every fix reverts with `git revert`. The blast radius of "the agent shipped a bad change" is bounded by the same one-command rollback I use myself. You cannot say that about a script that ran a mutation and moved on.
- **An audit log of everything.** Every observation, every verdict, every tool call, one JSON line, append-only.

```jsonl
{"event":"observation","obs_count":4731}
{"event":"triage_verdict","fp":"Pod:apps:zot:CLB","verdict":"reason"}
{"event":"problem_turn_start","fp":"Pod:apps:zot:CLB","attempts":1}
{"event":"tool_call","tool":"kubectl_logs","ok":true}
{"event":"agent_finish","fp":"Pod:apps:zot:CLB","action":"noop"}
```

I do not trust the model's account of what it did. I trust the trace. Budget caps the rate. Debounce caps how fast it reacts. The verify window caps the retry rate. GitOps caps the blast radius. Today every one of those knobs is turned down low. The point is that they are knobs, they exist by construction, and the architecture forces them. That part transfers whether or not you ever put a model anywhere near your cluster.

## The ratchet, not the switch

Here is what the system is building toward.

Today the agent reasons about every problem that reaches it. Every fix costs tokens. Fine for a homelab, wrong at scale. So when the agent resolves a problem, the system logs what worked, the `(kind, issue_class, tool)` it used, and mines those outcomes for patterns:

```
observe --> reason --> act --> observe
                                  |
                                  v
                         (kind, issue, tool)
                                  |
                            recipe miner
                                  |
                                  v
                  learning --> ready --> active
                  (>= 3 successes, < 20% failure rate,
                   then I click activate)
```

A recipe in `learning` is a pattern the agent has used a few times. A recipe in `ready` has crossed the threshold, at least three successes and under a twenty percent failure rate, and it shows up on the dashboard, but it does not fire. A recipe in `active` runs in the fast loop with zero model calls. The promotion from `ready` to `active` is a button I press, not something the system does to itself.

Nothing has been promoted to `active`. The agent still reasons every single time. That is not the system failing to learn. That is the ratchet refusing to click forward until the data earns it. Autonomy is a destination you arrive at one rung at a time, gated by outcomes the system can verify itself. It is not a checkbox you flip because a demo looked good.

## Why it has not fixed anything, and why that is the point

So: months of running, a model with `kubectl` and a token, and not one autonomous fix. Read that the right way.

Most problems get `suppress` or `escalate` from triage, with no model call at all. Of the few that reach the model, most resolve themselves before the debounce clears, or the right answer genuinely is "do nothing and watch." The cases where the correct move is "the agent should change the cluster, right now, on its own" are rare, and when they have come up, they have usually been the host-level kind the agent correctly hands to me.

An agent that does nothing, loudly and auditably, is more useful than one that does something plausible and wrong. The whole machine is built to make "do nothing" the easy default and "act" the thing you have to earn your way into. It is working exactly as designed. The interesting result was never a fix count. It was watching a system decline to act, over and over, for good reasons I can read in the audit log.

## The model is the least interesting part

One more thing, because it is the thread through every post. The agent runs a local `qwen3:30b-a3b` model on a single consumer GPU. Not a frontier model. I tried to swap it and [learned why I could not](/how/homelab-ai-operated-part-4-fixing-problems/), but the deeper point is that the model is interchangeable. The intelligence that makes this safe to leave running does not live in the weights. It lives in the fingerprint, the triage classifier, the budgets, the verify windows, the audit log, and the memory that carries lessons between sessions. Swap the model and the system still works. Remove the scaffolding and no model is safe to run unattended.

## What is still hard

I will not pretend the work is done. The genuinely unsolved parts:

- **Did it work?** "The pod came back" is a weak signal. Semantic verification, knowing a fix actually fixed the thing and not just the symptom, is still crude.
- **Coordination.** The chat agent and the control plane share memory but not live state. Two agents acting on the same cluster without stepping on each other is a real problem I have only half-solved.
- **Judgment.** Knowing when an approach is wrong, when to say no, when to throw the design out. The agent does not do this. I do. That is the job I have kept, and I am not close to giving it up.

Each of those is a multi-quarter problem, not a weekend one.

## What transfers

You do not need any of my hardware to use the shape. If you take one thing from five posts, take this build order:

1. **Fingerprint** your problems before you do anything else. Everything keys off a stable identity.
2. **Triage before you reason.** Most signals are obvious. Classify them with rules and spend the model only on the residual.
3. **Narrow the action ladder.** Each rung more reversible than the one below it.
4. **Make GitOps, or your equivalent, the action surface.** Then audit and rollback come for free.
5. **Make the track record the runbook.** Do not ask the model to remember. Let the system promote proven fixes into deterministic recipes.
6. **Ratchet, do not switch.** Grant authority slowly, gated by outcomes the system can verify itself.

It is two machines in my apartment, an open 30B model, and a few thousand lines of Python. None of that is the interesting bit. The interesting bit is the shape of the scaffolding, and the shape does not need a homelab. It does not even need a model.

Most of us are building systems that take autonomy. I spent this series building one that earns it. It has not fixed anything yet. That is the most useful thing it has taught me.
