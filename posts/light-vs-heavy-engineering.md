---
title: Light vs Heavy Engineering
date: 2017-06-21
description: This is the start of a short series on Light vs Heavy Engineering, when one should be applied over the other, the processes used in each, and how to get
slug: light-vs-heavy-engineering
draft: false
---

*This is the start of a short series on Light vs Heavy Engineering, when one should be applied over the other, the processes used in each, and how to get projects with long iteration loops to adopt shorter ones. *

Part 1: Light vs Heavy Engineering

---

As engineers, we're trained to build things that don't break.

Plans for a bridge signed off on by a certified Professional Engineer after years of work. Rockets are simulated over and over in every environment and scenario imagined by its designers.

Colleges teach engineers to design to specifications; a definition that dictates where the project can fail and by how much. "This bridge must have one hundred cars drive on it daily for twenty years before it fails." "Computer RAM must withstand ten million erase cycles before it has corruption errors." It's beaten into us during school to build things that last. We're taught to do Heavy Engineering.

Heavy engineering is the attempt to predict and simulate the real world during your design loops. Specifically the test portion is done in a replicated or simulated environment instead of the true environment in which the product will be used.

We need heavy engineering for the big projects. The military ships, rockets, car air bags, airplane turbines, buildings, and many embedded software projects where the human or monetary cost is too high to test in the real world environment for the product.

Though more and more we're starting to see "light engineering" used for large projects. What's the difference? The time to complete a loop - otherwise known as an [iteration and decision/ OODA loop](https://en.wikipedia.org/wiki/OODA_loop) - for heavy engineering is 6 months or more. For light engineering it's short. Sometimes hours, minutes, or seconds for automated systems.

---

A loop is one design, build, test, ship cycle. To complete a full cycle a project much ship to real customers. In an ideal case the project ships to as many people as possible.

If a team can get its loop timing quick enough they can and should engage in light engineering. The main goal of light engineering is to get to the "Oh my god there's not a market here" or "we didn't plan for variable to make such a large impact" realization as fast and with as little waste as possible. Being incorrect about a fundamental assumption of a company or project is not something tolerated by heavy engineering. There is not the time to be wrong because of how long and the cost it takes to go through a second iteration loop.

You might be thinking, "This sounds like Lean Startup/design/business/etc!" This and the lean methodology have their roots in the same place (see [John Boyd](https://en.wikipedia.org/wiki/John_Boyd_(military_strategist)). However, Lean is prescriptive in how you go about getting your loops short. Light engineering is not. It is a purview for looking at and approaching a particular set of problems.

The faster the loop the better; ship to customers in the real world often. Software developed for the web, most mobile devices, and handmade or basic plastic physical goods are common examples of light engineering. Software is often shipped to customers hourly (or faster) providing almost instant feedback. Hardware is pushing towards shorter loops through additive manufacturing and creative development processes.

One approach is not better than the other. Rather they are two different ways of executing against a problem. If the loops can be quick it's better to test in the real world. If they can't, you'd better simulate the real world to make sure it's right the first time.
