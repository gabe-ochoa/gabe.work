---
title: Building a homelab my AI operates, part 3: the infrastructure
date: 2026-07-12
description: Part 3 of the series. The map. Two main nodes meshed over a private network, what runs where, the registry I tore out and replaced, and the one device whose absence can take down half the cluster.
draft: false
slug: homelab-ai-operated-part-3-infrastructure
---

[Part 1](/how/homelab-ai-operated-part-1-bootstrapping/) was the goals and the bootstrap. [Part 2](/how/homelab-ai-operated-part-2-develop-deploy-review/) was the everyday loop: the agent proposes, the machine checks, I decide.

This post is the map. You need it before the next two, because both of them, fixing problems and the autonomous loop, are really stories about this map. Where things run determines what breaks together, and what breaks together is the whole game once you let an agent try to fix things.

I will keep it concrete. Here is what the cluster actually is.

## Two machines and a network

The cluster is two main nodes (plus a NAS node I added later), meshed into one Kubernetes cluster over a [Tailscale](https://tailscale.com) tailnet. They do not need to share a LAN. k3s routes its own traffic over the tailnet, so in principle these boxes could live in different buildings and the cluster would not notice.

```
            tailnet (hawk-tuna.ts.net)
   ┌───────────────────┴───────────────────┐
   │                                        │
hostnamec23-1                              b21
k3s server                                k3s agent, GPU node
  CoreDNS                                   Ollama (local LLMs)
  Traefik                                   MinIO + Zot (registry)
  metrics-server                            ClickHouse, embeddings
                                            Plausible, Dify
                                            the control plane itself
```

The split matters, so read it carefully.

**`hostnamec23-1` is the server.** It runs the Kubernetes control plane, CoreDNS (the cluster's DNS), and Traefik (ingress). It is the brain stem. Boring, stable, mostly stateless.

**`b21` is the GPU node, and it is where the weight is.** A single NVIDIA RTX 4060 Ti with 16GB of VRAM. Almost everything stateful or heavy lives here: [Ollama](https://ollama.com) serving the local models, the object store, the container registry, the analytics database, the embedding service, the analytics frontend, the knowledge base, and the autonomous control plane itself.

Write that last sentence on the wall. The agent that is supposed to fix the cluster runs on the same node as its own brain (the model) and its own memory (the database and embeddings). That is a deliberate convenience and also a structural weakness, and it is the heart of part 4. Hold that thought.

## How the nodes mesh

The trick that makes "nodes anywhere" work is one line in the k3s bootstrap. Each node advertises its Tailscale IP and runs the pod network over the tailnet interface:

```bash
k3s ... \
  --node-ip <tailscale-ip> \
  --flannel-iface tailscale0
```

That is the whole multi-site story. No VPN to manage, no port forwarding between sites, no public control-plane endpoint. A new node anywhere on the tailnet can join with the server's `100.x.y.z` address. I have a script that detects the Tailscale IP and wires this up, but the two flags above are the substance.

There is a sharp edge hiding in here. I will get to it.

## The platform layer

On top of k3s, a set of shared services that every app leans on. None of this is exotic. The value is that it is all declared in the same repo and reconciled by Flux, so the agent treats platform changes the same way it treats app changes.

- **MetalLB** hands out load-balancer IPs from a pool on my LAN. This is what lets a `Service` of type `LoadBalancer` actually get an address at home, where there is no cloud provider to do it.
- **cert-manager** issues Let's Encrypt certs for the handful of public hostnames.
- **Longhorn** is distributed block storage, replica count two. Any app that needs a real disk gets a Longhorn volume. This is also a character in the part-4 incident, because replicas that cannot reach each other panic.
- **MinIO and Zot** are the registry stack, and they have a story worth telling.

### The registry I tore out

Early on I ran [Quay](https://quay.io) as the container registry. It worked. It was also absurd for a homelab: Postgres, Redis, a config bundle, and a 6GB memory ceiling, all to store some images I build myself. The operational overhead was wildly out of proportion to the job.

So I replaced it with two smaller pieces:

- **[MinIO](https://min.io)**, a single-replica S3-compatible object store, with two buckets: one backs the registry, one holds generic artifacts.
- **[Zot](https://zotregistry.dev)**, a lightweight OCI registry, with its storage driver pointed at MinIO.

Pulls are anonymous, so cluster workloads need no image-pull secrets. Pushes are gated by an htpasswd file with two accounts: one for me, one for CI. Zot creates a repository on first push, so there is no provisioning step. The whole thing uses a fraction of the memory Quay did.

The lesson is not "Zot good, Quay bad." Quay is excellent at Quay's job. The lesson is that homelab infrastructure has a different cost function than production infrastructure, and the right call is often the boring lightweight thing, not the powerful heavy thing. Picking the heavy thing because it is what you would use at work is a real and common mistake. I made it, then fixed it.

## How things get exposed

Two ways out of the cluster, and the default is the private one.

**Tailnet by default.** Any service with a UI gets a single annotation, `tailscale.com/expose: "true"`, and a unique hostname. It becomes reachable from any device on my tailnet, full stop. No public DNS, no certificate dance, no attack surface. Grafana, the dashboards, the internal tools: all tailnet-only. This is the right default for anything that is just for me.

**Public only on an explicit allowlist.** A small number of things need to be on the real internet: a couple of public sites. Those go through a [Cloudflare](https://www.cloudflare.com) tunnel, and the list of what is allowed out is a single config file. Adding a hostname is a deliberate edit. Nothing is public by accident. Internal tools that someone might be tempted to expose stay off that list on purpose.

That default, private unless I say otherwise, is also a guardrail for the agent. It cannot accidentally publish something to the internet, because publishing requires editing the one file that everyone, human and agent, has to go through.

## The sharp edge

I promised a sharp edge. Here it is, because it is the bridge to the next post.

The pod network runs over the tailnet, but Tailscale is not the whole story. Flannel, the thing that actually moves pod-to-pod traffic, still creates a virtual network device on each node called `flannel.1` and installs a route to the other node's pod range. If that device disappears on a node, every pod on that node loses the ability to talk to pods on the other node. DNS lookups time out. Storage replicas cannot sync. The registry cannot reach the object store.

Now recall where everything lives. If that device vanishes on `b21`, the GPU node, then the model, the memory, the registry, the database, and the control plane are all on the wrong side of a partition at once. And the agent whose job is to notice and fix problems cannot, because the model it thinks with and the memory it learns from just became unreachable.

That is not a hypothetical. It happened. And what the agent did, what it could not do, and what I changed so it would not happen again, is the next post.

## What is working, and what is not

**Working:** the tailnet mesh is the best decision in the whole stack. Nodes are trivial to add, nothing is exposed I did not choose to expose, and I have never thought about VPNs or port forwarding. GitOps over the same repo means platform and apps are one workflow. Replacing Quay with Zot-on-MinIO cut a real chunk of memory and operational worry for zero lost capability.

**Not working as well as I want:** too much lives on one node. `b21` is a single point of failure for the interesting half of the cluster, and the autonomous agent sharing a node with its own brain is a design smell I have not fixed. Longhorn at replica two is the minimum that is not pointless, and it is sensitive to exactly the network failure described above. The honest summary is that the cluster is resilient to a pod dying and fragile to a node's overlay breaking. Guess which one this series spends a whole post on.

## Where this goes next

That is the map: two main nodes on a private mesh, the heavy half concentrated on the GPU box, a lightweight registry I learned to prefer, and a private-by-default exposure model. Plus one device whose absence partitions the things that matter.

Next post: **how we fix problems together.** A real incident where one cause wore six disguises, an experiment I ran and killed with data, and the mechanism that turns a fix into something the next session already knows. That is where the agent stops being a code author and starts being an operator, with all the limits that exposes.
