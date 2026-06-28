---
title: Building a homelab my AI operates, part 1: goals and bootstrapping
date: 2026-06-28
description: The start of a series on a homelab written almost entirely by AI agents. This first post is the why, the workflow, and how it got off the ground, with the commands to copy.
draft: false
slug: homelab-ai-operated-part-1-bootstrapping
---

Almost every line of YAML in my Kubernetes cluster was written by an AI agent. Every Dockerfile. Every CI pipeline. Every service. I review the diff and I merge the PR. The git log is the receipt: each commit is either me or [Claude Code](https://www.anthropic.com/claude-code), no hand-wave.

This is the start of a series about that cluster. It runs about seventeen apps across two machines in my apartment, and the goal it is built toward is uncomfortable to say out loud: a system that operates itself, where an agent watches the cluster and is allowed to fix it.

I will get to that agent. Not today. The thing everyone wants to talk about, the model with `kubectl`, is the last thing I built, and the order is the entire point. This first post is the part people skip: why I did it, the workflow that makes it safe, and how the foundation got stood up. With the commands, so you can copy it.

## The goals

I did not set out to build "an AI-operated homelab." That is a destination, not a plan. I set out to answer three things that bug me about how infrastructure actually gets run.

**Runbooks rot.** The wiki page that tells you how to fix the thing is wrong six months after someone writes it. Can the system maintain its own runbook instead?

**Triage is reactive.** A human looks at every alert to decide if it even matters. Most do not. Can the obvious calls get made without a person, so attention goes only to the cases that are genuinely unclear?

**Autonomy is binary.** Either a script runs unattended or a human approves every action. Nothing in between. Can a system earn more authority as its track record justifies it, one narrow step at a time?

None of those is "let the AI run it." The goal was to find out what would make me *comfortable* letting it run any of it. So the real design goal, the one everything else serves: build a system that earns autonomy instead of one that takes it.

## The workflow: an agent types, I review

Before any of the infrastructure, the thing that made this possible is a workflow. I do almost no typing. Claude Code does the typing. I do the reviewing and the trusting. For that to be safe rather than reckless, the agent runs inside a set of guardrails, and none of them are AI-specific. They are standard infra hygiene that happens to be exactly sufficient.

Here is the setup, concretely, because this is the part you can replicate today on any repo.

**Deny by default, allowlist verbs.** Claude Code asks before running anything not on an allowlist. In `.claude/settings.json` the tool permissions name the commands the agent runs unattended, and everything else stops for my approval:

```json
{
  "permissions": {
    "allow": [
      "Bash(kubectl:*)",
      "Bash(flux:*)",
      "Bash(sops:*)"
    ]
  }
}
```

The trick that keeps this list short: put credentials like `KUBECONFIG` and `SOPS_AGE_KEY_FILE` in the environment, not inline in commands. A bare `kubectl ...` matches `Bash(kubectl:*)`; a `KUBECONFIG=... kubectl ...` does not, and you end up with fifty hyper-specific rules instead of one.

**The agent never sees plaintext secrets.** Everything sensitive is SOPS-encrypted in the repo (more on that below). The agent reads and edits ciphertext. It cannot leak what it cannot decrypt.

**Branches, not direct pushes.** The agent commits to a feature branch. I merge to `master`. The one deliberate exception is the autonomous control plane later in the series, and it is the most heavily constrained actor in the whole system.

**A CI gate on every push.** `kustomize build` renders every manifest and [`kubeconform`](https://github.com/yannh/kubeconform) schema-checks it before [Flux](https://fluxcd.io) ever sees it. A broken manifest fails in CI, not in the cluster. So my review is about intent, not syntax. The pipeline owns syntax.

**Hooks for the boring failure modes.** A `SessionStart` hook bootstraps the agent's environment every time a session opens, so it starts from a known state instead of whatever the last session left behind.

None of this is novel. That is the point. The novelty is that this boring set of rules turns out to be *enough*, because the agent respects them by construction.

## How it got bootstrapped, layer by layer

I did not begin by handing a model the keys. Each layer got built only after the one below it got boring. That ordering matters more than any single tool, so here are the phases I actually went through.

**Phase 1: Claude Code edits files, I review every diff.** Just the agent pointed at the repo, inside the guardrails above. Nothing autonomous. The value is not speed. It is that I learned exactly which mistakes the agent makes, and built guardrails for those specific mistakes, before trusting it with anything bigger.

**Phase 2: CI validates and deploys, I trust the pipeline.** Once a commit lands, `kustomize` + `kubeconform` gate it and Flux reconciles. A bad config fails before it reaches the cluster. Now I review intent; the pipeline catches syntax.

**Phase 3: skills and memory, knowledge compounds.** I wrote a `homelab` skill: a few hundred lines describing the cluster topology, the common failure modes, and the exact commands to diagnose them, which the agent loads on startup. Then a shared memory store (a [Dify](https://dify.ai) knowledge base, embedded with a local `nomic-embed-text` model) so a fix found in one session becomes a retrievable card in the next. The model did not get smarter. The knowledge layer did. The cluster got easier to operate even as it grew.

**Phase 4: a chat agent, operator in the loop.** Same skills, same memory, conversational, running in-cluster. I can ask "why is the registry unhappy" and it runs the diagnosis. Still me driving, but now the agent has a body in the cluster, not just on my laptop.

**Phase 5: the control plane, an autonomous loop.** The one that watches and acts on its own, running a local `qwen3:30b-a3b` model on a single GPU node via [Ollama](https://ollama.com). This is where the series spends most of its time, and the one thing I will not unpack today.

The lesson in that list: you do not earn autonomy by promising it. You earn it by removing, one at a time, every reason a human had to intervene at the layer below. Phase 5 was only safe to attempt because phases 1 through 4 were already dull.

How dull? The git history is blunt about it. For months before any agent ran inside the cluster, the agent was just writing apps: an energy dashboard pulling my ConEd usage, a controller for my Daikin heat pumps, a ledger, a pile of small sites. Dozens of pull requests, all of them the ordinary develop-deploy-review loop, none of them autonomous. The first attempt at the autonomous control plane was actually scrapped. I opened it, looked at the design, and closed it without merging. The version that runs today is the second one, and it is deliberately more conservative than the first. That whole story is the last post in this series. I mention it now only to set the expectation: nothing here arrived in one leap.

## The foundation, with the commands

You do not need a GPU, a model, or an autonomous anything to lay the groundwork. Here is the minimum that everything else is built on, in build order. If you do only this, you already have a homelab worth having, and you have built the surface a future agent will operate on.

### 1. One repo, reconciled. Not `kubectl apply`.

Get [k3s](https://k3s.io) on a box and put Flux in front of it. The moment your cluster's desired state lives in a git repo, you get audit, rollback, and review for free.

```bash
# on the node
curl -sfL https://get.k3s.io | sh -

# from your laptop, point Flux at your repo
flux bootstrap github \
  --owner=you --repository=homelab-config \
  --branch=main --path=clusters/home --personal
```

Every change is now a commit. Reverting a bad one is `git revert`. This single move is worth more than anything else in the series. It is also what makes letting an agent touch the cluster thinkable: the blast radius of a bad change is bounded by the same revert you already have.

### 2. Mesh the nodes over Tailscale, not your LAN.

Route inter-node traffic over a [Tailscale](https://tailscale.com) tailnet instead of local IPs. Now a second node can live anywhere: another room, another building, a friend's closet. The cluster does not care. The one trick: point the agent node's join address at the server's Tailscale IP (the `100.x.y.z` one), not its LAN address.

### 3. Encrypt secrets in the repo with SOPS.

This is what makes "everything in git" safe, and what lets the agent work in the repo without ever touching a plaintext credential.

```bash
age-keygen -o age-keys.txt        # keep the private key out of the repo
# add the public key to .sops.yaml, then:
sops --encrypt --in-place infrastructure/myapp/secret.yaml
# give Flux the private key so it can decrypt at runtime
kubectl create secret generic sops-age \
  -n flux-system --from-file=age.agekey=age-keys.txt
```

That is the whole foundation. k3s, Flux, Tailscale, SOPS, plus Claude Code working inside the guardrails. Boring on purpose. The boring is what makes the rest safe.

## What is working, and what is not

This is a series about a real system, not a victory lap, so the honest scorecard up front.

**Working:** the agent does basically all the typing and I review the diff. GitOps means I have never been afraid of a change, because every change reverts in one command. Knowledge compounds; the cluster is easier to operate today than when it was half this size.

**Not working yet:** the autonomous control plane has not made a single fix on its own. It watches, it reasons, and it almost always decides to do nothing. That is the design, and a full post is coming on why that is the result I wanted. There are real unsolved problems too: telling whether a fix actually worked is a weak signal, and coordinating multiple agents that share memory but not live state is genuinely hard.

The local model, by the way, is not the smart part. `qwen3:30b-a3b` is an ordinary model on one GPU. The intelligence lives in the scaffolding around it. That claim is going to do a lot of work later in the series.

## Where this goes next

This was the start: the goals, the workflow, and the foundation you can stand up this weekend. From here the series builds up one layer at a time.

- **How we develop, deploy, and review apps.** The everyday loop: the agent proposes a change, the machine checks it, I decide. The contract that makes the agent's output usable, and the three layers of review.
- **An infrastructure overview.** The two nodes, what runs where, and why the placement of a single VXLAN device can take down half the cluster.
- **How we fix problems together.** What happens when something breaks: the diagnosis loop, what the agent is good and bad at under pressure, and how a fix becomes knowledge the next session inherits.
- **The control-plane loop.** Finally, the autonomous agent. The thing that watches the cluster and is allowed to act, the authority ladder that makes that safe, and why it has not made a single fix yet.

Most of us are building systems that take autonomy. I am trying to build one that earns it. Next post, the loop I run every day.
