---
title: Building a homelab my AI operates, part 2: how we develop, deploy, and review apps
date: 2026-07-05
description: Part 2 of the series. The everyday loop where an agent proposes a change, the machine checks it, and I decide. The contract, the deploy path, and the three layers of review, with the commands.
draft: false
slug: homelab-ai-operated-part-2-develop-deploy-review
---

[Part 1](/how/homelab-ai-operated-part-1-bootstrapping/) was the foundation: k3s, Flux, Tailscale, SOPS, and the claim that almost every line in the repo was written by an AI agent while I reviewed the diff.

This post is that claim in motion. Not the autonomous loop, the everyday one: I describe an app, [Claude Code](https://www.anthropic.com/claude-code) writes the manifests, a pipeline checks them, and a change ships to the cluster. It is the most-run loop in the whole system, and it is the one I would actually recommend to anyone, model with `kubectl` or not.

The shape is simple. **The agent proposes. The machine checks. I decide.** Each of those three is a real, separable mechanism. Here they are.

## The agent proposes: a contract, not vibes

The reason an agent can write usable Kubernetes manifests for my cluster is not that the model is brilliant. It is that the repo tells it exactly how this cluster does things. That contract lives in one file: `AGENTS.md` at the repo root.

It is a plain document, but it is the single highest-leverage thing in the workflow. It says, in specific terms:

- Where things go. `infrastructure/` for shared services, `apps/<workload>/` for app manifests, `services/` for buildable source code.
- What to copy. "Follow the `whoami` example for a stateless app, Homebridge for a persistent one, `home-portal` for a configmap-driven frontend, `solar-collectors` for a CronJob." The agent does not invent a deployment from scratch. It copies the closest working pattern and edits it.
- The house rules. Two-space YAML. Secrets encrypted with SOPS, always update `.sops.yaml` when adding a secret path. Any UI Service must carry `tailscale.com/expose: "true"` and a unique hostname so it is reachable on the tailnet. Public exposure is an explicit allowlist in the Cloudflare tunnel config, nothing leaks out by default.

```
clusters/<name>/     Flux entry points
infrastructure/      shared services (MetalLB, cert-manager, Longhorn, Zot...)
apps/<workload>/     app manifests (copy the nearest example)
services/<name>/     buildable source (becomes a container image)
```

Write this file for your own repo and the agent's output goes from "plausible Kubernetes" to "manifests that match the other forty things already running." It is the difference between an intern who has read your runbook and one who has not. The model is the same; the context is what changed.

So a new app starts as a sentence from me: "add a small status page, stateless, expose it on the tailnet." The agent reads `AGENTS.md`, copies the `whoami` pattern, wires it into the cluster kustomization, and opens a branch. I have written no YAML.

This is not a toy claim. The cluster filled up this way: an energy dashboard pulling my ConEd usage, a controller for my Daikin heat pumps over Home Assistant, a self-hosted analytics service, a handful of small public sites. One of those sites went through something like fifteen pull requests on its own as the idea changed under it. A signup flow moved from a database to a third-party backend to an email-only Edge Function. A payment step got replaced by a single checkbox. Every one of those was the same loop: a sentence, a branch, a review, a merge. The loop is boring on purpose, and boring is what lets you run it dozens of times without dread.

## The machine checks: validate before anything is real

Before I look at a diff, two things have already judged it.

**Local validation.** Every manifest set renders and gets schema-checked. This is one command, and it catches the entire class of "this YAML is structurally wrong" before it wastes anyone's time:

```bash
just validate homelab
# under the hood: kustomize build | kubeconform
```

To preview what a change would actually do to the live cluster, Flux can diff the desired state against reality:

```bash
flux diff ks homelab --path clusters/homelab
```

**CI on push.** When the agent's branch hits GitHub, a self-hosted [Woodpecker](https://woodpecker-ci.org) runner picks it up. It runs the same validation, and if the change touched a buildable service, it builds the container image with Kaniko and pushes it to the in-cluster registry. CI runs inside the cluster, on the same hardware everything else does. There is no external build service in the loop.

The important property: a broken manifest fails here, in CI, not in the cluster. By the time a change is in front of me, syntax is a solved problem. I get to spend my attention on whether the change is a good idea, which is the only part a machine cannot do for me.

## I decide: three layers, then a merge

Review is not one step. It is three, each cheaper than the last failing late.

**Layer one is the CI gate.** Already covered. If `kustomize build | kubeconform` fails, there is nothing to review yet.

**Layer two is a second model reading the diff.** Before I read a PR, a different local model does. This one exists for a mundane reason: GitHub's own Copilot review needs a paid plan on a private repo, so I built the equivalent on hardware I already own. A CronJob runs every fifteen minutes, lists open PRs, skips any whose latest commit it has already reviewed, and for the rest sends the diff to the in-cluster [Ollama](https://ollama.com) and posts the review back as a PR comment. Idle runs make zero model calls, so the GPU only wakes when there is something new to read. There is also an on-demand version for a single PR:

```bash
scripts/llm-pr-review.sh <pr-number> --post
```

It runs `qwen2.5-coder:32b` with a system prompt that tells it to act like a senior infra engineer: look for broken references, wrong ports, plaintext secrets, over-broad RBAC, missing probes, and the GitOps-specific traps like using `RollingUpdate` on a PVC-backed app. It is told to skip style nits and praise. The output is a short summary and a bulleted findings list, signed with the model and commit SHA.

This matters for a specific reason: the agent that *wrote* the change should not be the only agent that *judges* it. A separate model, separate prompt, separate job, reading the same diff with fresh eyes, catches a real fraction of issues before a human ever looks. On its first real run, against a 485-line PR, it caught a genuine secret-rotation risk and threw a couple of false positives. That ratio is the honest picture of a 32B model reviewing on one GPU: useful, not infallible, and free.

**Layer three is me.** I read the diff and the bot's comment, and I merge. That is the part I keep for myself, on purpose. The agent commits to a feature branch; merging to `master` is my call. After the merge, Flux does the rest.

## Deploy: there is no deploy step

This is the part people expect to be complicated and it is the opposite. There is no `kubectl apply` in my workflow. There is no deploy script I run. The merge *is* the deploy.

```
agent branch ──► PR ──► CI builds image + pushes to registry
                           │
                     I review + merge to master
                           │
                     Flux notices the new commit
                           │
                     Flux reconciles the cluster (~minutes)
```

Flux watches the repo. When `master` changes, it pulls the new manifests, decrypts any SOPS secrets with the key it holds, and reconciles the live cluster toward the new desired state. For a first-party service, the manifest now points at the image CI just built, so the new code rolls out the same way.

I can force it to happen immediately instead of waiting for the interval:

```bash
just flux-reconcile homelab
```

The thing I want to land: because the deploy is just "the repo changed," every deploy is also a commit, every commit is reviewed, and every change reverts with `git revert`. Rollback is not a separate capability I had to build. It is the same mechanism running backward. That property is why I am willing to let an agent participate in deploys at all, and it is the hinge the entire autonomous half of this series swings on.

## What is working, and what is not

**Working:** the loop is genuinely fast. A small app goes from a sentence to running on the tailnet in one sitting, and I never opened a YAML file. The contract file does most of the heavy lifting; the two-model split (one writes, one reviews) catches more than either would alone. And because everything is GitOps, I have never lost sleep over a deploy.

**Not working as well as I want:** the local PR-review model is good at the mechanical classes of bug and weak at judgment. It will reliably catch a wrong port and reliably miss "this whole approach is wrong." Image tagging is still rougher than I would like; tying a freshly built image to the manifest that should use it is not as automatic as the rest. And the review still depends on me for anything that requires taste. That is fine, that is the job I kept, but it is the ceiling on how hands-off this particular loop can get.

## Where this goes next

That is the development loop: a contract so the agent proposes well, a pipeline so the machine checks, and a three-layer review so I only spend judgment where judgment is needed.

Next post is the **infrastructure overview**: the two nodes, what runs where, the registry and object store and analytics DB, and why the placement of one VXLAN device can take down half the cluster. You need that map before the last two posts make sense, because both of them, fixing problems together and the autonomous control loop, are really about that map.

The agent does the typing. The machine does the checking. I do the deciding. Next, the ground all of it runs on.
