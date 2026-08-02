---
title: Festival Gear: Not your average glow things
date: 2015-09-29
description: A very good way to get questioned at the airport I love things that glow. Most people do. Something about them screams future, life, presence. The only
slug: festival-gear-not-your-average-glow-things
redirect_from: /how/2015/9/29/festival-gear-not-your-average-glow-things
draft: true
---

![A very good way to get questioned at the airport](/assets/blog/festival-gear-not-your-average-glow-things/01.jpeg)

A very good way to get questioned at the airport

I love things that glow. Most people do. Something about them screams future, life, presence. The only thing better than making something glow is making it react to the world or people around it. Not your average glow things but a piece that's prompts an audible "oooooooooo."

So why not make some Converse of the future that glow everytime you step?

I had bought a pair of [Converse Chuck II's](http://www.converse.com/landing-chuckII) when they first came out. Great shoes. Highly recommended. But they would be better if they had lights on them. More specifically, lights that reacted to your every step. Not a new concept - if you were a kid in the 90s you desperately wanted a pair of [LA Lights](http://lagear.com/collections/la-lights) - but one worth exploring.

The issue with LA lights or the lot on [Amazon](http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=light+up+shoes) and Ebay is the response time. You step, they light up a second later or worse send a chase patter around the individual LEDs on the shoes. OK for one step but some place where you'll dance your face off. I really wanted an almost instant response.

I had made a sound reactive backpack outlined in EL wire a couple years back that had a wonderful response time to the beat of the music playing. Great place to start. (I upgraded the backpack with much brighter lighting, new batteries, and a controller. I'll include pictures at the end of the post.)

So where do we start? Well what do I absolutely have to get right?

**Requirements:**

- **18 hours of runtime**. Thats's 3 days x 6 hours a night. Conservatively I assumed they would be on whole time even though in practice they would be off when I was not moving.

- **Contained on the shoes**. Didn't want a wire running up to the backpack. Just less of a PINTA.

- **Lite weight**. Going to be strapped to my feet after all

- **Fast reaction to every step**. Had to keep up and react faster than I can move my feet (not that fast).

- **Bright**. They needed to be noticeable when on in the dark.

First I need a pressure sensor for under the heel to sense when I step. Ok easy. Force Sensitive Resistors (FSR) are your standard pressure sensor. Problem: they're relatively expensive for what they are and fragile. Solution: [Velostat](https://en.wikipedia.org/wiki/Velostat)! This wonderful material drops its resistance based on the pressure applied but was developed as an ESD material. Awesome stuff. It's cheap and it makes a pressure sensor of any reasonable human scale size easily with two wires attached to either side.

I decided to use EL tape around the bottom white portion of the converse for the lighting. It's bright, durable, and awesome looking. First issue: electroluminescent lighting is a AC power capacitive light source. This means I need to go from the DC power of a battery to the AC power needed for the EL Tape. Which means a battery, a controller for the sensor input, and an inverter.

![](/assets/blog/festival-gear-not-your-average-glow-things/02.jpeg)

There is where China comes in (yayayayay). Remember that backpack I was talking about? Well it just so happens the [sound reactive controller](https://www.adafruit.com/product/832) I used for it takes care of the controller and and inverter portions. The controllers have a mic and a gain adjustment for different sound levels. A microphone is a pressure sensor and with a gain I could probably get away with replacing it with the Velostat directly and using the gain to tune the controller in. This worked remarkably well. I ended up bottoming out the resistance of the pressure sensor when standing on it which go the controller to go to steady state and produce no light. Perfect. The lights would only come on when I picked my feet up.

![](/assets/blog/festival-gear-not-your-average-glow-things/03.jpeg)

With the controller already sizable I had to make sure the batteries were small. I opted to try a 6V pack made of 2 coin cell batteries ([Thanks Adafruit for the inspiration](https://www.adafruit.com/product/783)). After wiring everything up it was just not bright enough. I needed to use the 12V controllers which meant a bigger battery. Which meant to keep the size down I needed a small LiPo pack. Easy enough. [3 individual LiPo cells](https://www.adafruit.com/product/1578) for a 3s1p (3 in series, 1 in parallel) battery pack with a rating of ~12 volts and 500mAh. The amperage draw of the EL tape on was less than 25mA which gives me about 20 hours of runtime. When building battery packs one must use a lot of electric tape/heat shrink/care. [LiPos are nasty when they explode](https://www.youtube.com/watch?v=EseOhC8n7ro).

After everything was assembled and glued onto the shoes I ended up with something that was pretty awesome. Here was the quick and dirty test run with the wires all over the place:

Super sketchy looking but awesome output and reaction time. Video in the dark below.

Some more pictures from the build and the light up power button for my chest that turned my backpack on and off. Might do a post of them but not nearly as interesting as the shoes.

![IMG_3001.jpg](/assets/blog/festival-gear-not-your-average-glow-things/04.jpg)

![IMG_2999.jpg](/assets/blog/festival-gear-not-your-average-glow-things/05.jpg)

![IMG_3002.jpg](/assets/blog/festival-gear-not-your-average-glow-things/06.jpg)

![IMG_3027.jpg](/assets/blog/festival-gear-not-your-average-glow-things/07.jpg)

![IMG_3048.jpg](/assets/blog/festival-gear-not-your-average-glow-things/08.jpg)

![IMG_3050.jpg](/assets/blog/festival-gear-not-your-average-glow-things/09.jpg)

![IMG_3051.jpg](/assets/blog/festival-gear-not-your-average-glow-things/10.jpg)

![IMG_3063.jpg](/assets/blog/festival-gear-not-your-average-glow-things/11.jpg)
