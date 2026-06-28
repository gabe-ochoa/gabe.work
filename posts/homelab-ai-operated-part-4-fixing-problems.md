---
title: Building a homelab my AI operates, part 4: how we fix problems together
date: 2026-07-19
description: Part 4 of the series. Writing code is easy mode. This is what happens when something breaks: a partition that wore six disguises, an experiment I killed with data, and how a fix becomes knowledge the next session already has.
draft: false
slug: homelab-ai-operated-part-4-fixing-problems
---

[Part 3](/how/homelab-ai-operated-part-3-infrastructure/) ended on a cliffhanger: a single network device, `flannel.1`, whose absence on the GPU node partitions the half of the cluster that matters. I promised that was not a hypothetical.

This post is what happens when things break, and how the agent and I handle it together. Writing code is the easy mode. The agent proposes, the pipeline checks, I merge, and if it is wrong I revert. Operating is the hard mode. There is no pipeline between a broken cluster and you. Something is down right now, the signals are lying to you, and the fix might be a place the agent literally cannot reach.

Two stories. One is an incident. One is an experiment I ran and killed. Together they are the actual texture of operating this thing with an AI in the loop.

## Six symptoms, one cause

One morning the cluster lit up. Not one alarm. A cluster of them, all at once, all looking unrelated:

- Pods on `b21` could not resolve DNS. `i/o timeout` talking to CoreDNS.
- Longhorn went into a rebuild storm. Storage replicas could not reach their peers: `dial tcp <peer-ip> i/o timeout`, over and over.
- The registry could not reach the object store. `lookup minio: i/o timeout`.
- The control plane's own calls started failing.

If you take those at face value, you open six investigations. DNS is broken. Storage is broken. The registry is broken. Each of those has its own runbook, its own rabbit hole. You could spend an hour fixing the wrong layer.

They were one cause. The `flannel.1` device on `b21` had vanished. That device is what carries pod-to-pod traffic to the other node. With it gone, every pod on `b21` was cut off from everything on the server node. DNS lives across the partition. Storage peers live across the partition. The object store lives across the partition. One overlay device fell over, and six services screamed in six different voices.

The single most useful lesson I have learned operating this cluster: **many same-node services failing connectivity at once is one infrastructure problem wearing costumes, not six application problems.** Do not chase the symptoms. Find the thing they share.

The confirmation was three commands on the node:

```bash
ip link show flannel.1      # the device: does not exist
ip route | grep 10.42.0.0   # the route to peer pods: gone
lsmod | grep vxlan          # the kernel module: loaded, refcount 0
```

The fix was one command:

```bash
systemctl restart k3s-agent   # flannel rebuilds flannel.1 + the route in ~15s
```

Restart the agent, flannel recreates the device and the route, and all six symptoms clear together. You do not touch DNS. You do not touch storage. You fix the overlay and the rest recovers on its own.

## The thing the agent could not do

Here is where operating with an AI gets interesting, and honest.

The fix was `systemctl restart k3s-agent`. That is a command on the host, over SSH. The control plane has no SSH access. By design, it can act inside the cluster (delete a pod, restart a rollout, reconcile Flux) and it can commit to the repo. It cannot run a command on a node.

So for this class of problem, the entire arsenal the agent has is useless. It can delete every pod on `b21` and it will not help, because the pods are not the problem, the wire under them is. An agent that does not know the edge of its own authority would thrash here: restart this, delete that, try again, burn tokens, change nothing.

The correct move, the one the agent now knows, is to stop. Recognize the signature, name the one cause, and **escalate with the exact remediation command for a human to run.** Not "something is wrong with networking." Instead: "this is the flannel partition signature on `b21`; the fix is `systemctl restart k3s-agent`; I cannot run host commands, this needs you." An agent that hands you the precise fix and gets out of the way is worth more than one that tries everything in reach.

This is a general principle, not a homelab quirk. Any autonomous operator needs to know not just what to do, but what it is not allowed or able to do, and to escalate cleanly instead of flailing inside its own sandbox.

## Make the fix permanent two ways

A good incident ends with two artifacts, and we wrote both.

**A machine fix, so it cannot recur.** I added a watchdog: a small systemd timer that runs on each node every couple of minutes, checks that `flannel.1` exists and that a route to the pod network goes through it, and if not, restarts k3s to rebuild the overlay. It has a cooldown so it cannot restart-loop a genuinely broken node. The exact failure that took an hour to diagnose now self-heals in about two minutes, with no human and no agent involved. That is the best kind of fix: the one that makes the problem stop being a problem.

**A knowledge fix, so the next investigation is faster.** This is the part that is specific to working with agents, and it is the quiet superpower of the whole setup. I wrote the incident into the shared memory store as a retrievable card: the signature (what the six symptoms look like together), the three confirmation commands, the one-line fix, and the crucial note that the control plane cannot run it and must escalate.

Now any agent session, the chat agent, the control plane, a fresh Claude Code session on my laptop, gets that card back the instant a similar signature appears. I did not ask the model to remember the incident. The model does not remember anything between sessions. The *system* remembers, because the fix became data. The next time half the cluster goes dark at once, the first thing surfaced is "you have seen this; here is the one cause and the one command." The runbook does not rot, because there is no runbook. There is a memory that grows every time something breaks.

## The experiment I killed

Not every problem is an incident. Some are decisions, and the interesting thing is how we make them: with data from the live cluster, not vibes.

Everything local runs on one GPU on `b21`, an NVIDIA 4060 Ti with 16GB of VRAM. The models I use are slightly too big for it. The reasoning model and the code-review model both spill over 16GB and bleed onto the CPU, which is slower. So a tempting idea: switch everything to DeepSeek models that are about half the size, fit entirely on the GPU, and run faster.

It is a clean hypothesis. So we tested it, on the real cluster, before committing. The agent ran the evaluation. I made the call. Here is what came back.

**Tool-calling, the dealbreaker.** The control plane and the chat agent work by calling tools. They observe and act by emitting structured tool calls, not prose. Tested with a single `get_pods` tool:

- The incumbent reasoning model returned a clean tool call.
- One DeepSeek model returned prose instead, even when the API was told tool calls were required.
- The other DeepSeek model returned an HTTP 400: "does not support tools."

No DeepSeek model on that box does tool-calling. For two of the four roles, that is the end of the conversation. An agent that cannot call tools cannot observe or fix a cluster.

**Review quality, the regression.** For the PR reviewer, I gave both models the same diff with three planted bugs: a file-handle leak, a re-read inside a loop, and an off-by-one. The 32B incumbent caught all three. The smaller DeepSeek coder caught zero, and paraphrased the diff back at me instead. It is faster and it fits the GPU, and it would have made my review worse, not better.

**Embeddings, the non-starter.** DeepSeek ships no embedding model, and the memory layer needs embeddings. Nothing to switch to.

So I reverted all of it. Merged the switch, benchmarked it live, reverted the switch, and wrote it down as an architecture decision record so the next person, including future me, does not re-run the same experiment hoping for a different answer. The record states the conclusion plainly: GPU-fit is a real want, but not at the cost of tool-calling or review depth. The slower model that fits the job beats the faster model that does not.

The reason I am telling you a story about a change that did not ship: this is what "fixing problems together" actually looks like most of the time. Not a dramatic 2am save. A hypothesis, a measurement on the real system, and the discipline to throw out your own idea when the data says no. The agent is genuinely good at running that kind of eval, fast and without ego about it. I am the one who has to decide what the numbers mean and live with the call.

## What the agent is good and bad at, under pressure

Honest scorecard, because the whole series is supposed to teach you something you can use.

**Good at:** recalling a signature it has seen before and matching it instantly. Running a structured evaluation across several options without getting bored or sloppy. Writing the fix once you have decided what the fix is. Producing the watchdog, the card, the ADR, cleanly and fast.

**Bad at:** knowing when a problem is outside its reach, unless you have taught it that edge explicitly. Telling whether a fix actually worked, because "the pod came back" is a weak signal and "the cluster is healthy" is a weaker one. Judgment calls that need taste rather than pattern-matching. Resisting the urge to *do something* when the right move is to stop and escalate.

Notice that almost every weakness is addressed by the scaffolding, not by a smarter model. The edge-of-authority problem is solved by a memory card. The "did it work" problem is solved by verify windows in the control loop. The "do something" reflex is solved by a budget that forces escalation. The model did not change. The system around it learned.

## Where this goes next

That is fixing problems together: find the one cause behind the many symptoms, know what the agent cannot touch, make every fix permanent in code and in memory, and decide changes with data instead of vibes.

You now have the full picture: the goals, the develop loop, the infrastructure, and how we operate it by hand. The last post is the one everyone wanted first. **The control-plane loop.** The autonomous agent that watches the cluster and is allowed to fix it on its own. How it is built, the authority ladder and budgets that make a direct push to `master` something I sleep through, why its first version was scrapped, and why the current one has not made a single fix yet, on purpose. That last part is the whole reason I built it this way. See you there.
