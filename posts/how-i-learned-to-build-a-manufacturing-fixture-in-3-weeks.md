---
title: Building a Manufacturing Fixture in 3 Weeks.
date: 2015-10-06
description: I had the amazing opportunity of building a fixture to put new software on a product. Unfortunately it was not under the best of circumstances but that
slug: how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks
redirect_from: /how/2015/10/6/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks
draft: false
---

I had the amazing opportunity of building a fixture to put new software on a product. Unfortunately it was not under the best of circumstances but that made for a ludicrous deadline. Perfect conditions to do something I had not even seen a picture of before. I was familiar with the concepts around making that type of fixture but application is understanding and I had never actually used a [pogo pin](https://en.wikipedia.org/wiki/Pogo_pin) in a project.

Queue [The Process](https://gabe.work/how/2015/10/3/the-exploration-process).

I had started this project and gone through the first three iterations prior to the hard deadline being imposed. The first two iterations were done as an exploration but I shelved it and tried another method. What I was doing just did not work. To be honest, those first two revisions were genuinely bad. But they’re supposed to be as you stumble over your own two feet.

There were 3 main things I had to tackle with this build:

- I had never put a pogo pins into a project

- Alignment of the pins had to hit 0.2mm pads on the board

- The fixture had to be rigid enough for prolonged use.

Off the bat I figured I could get the alignment right and could build a rigid enough fixture to hold that alignment. I had zero experience with pogo pins - I’d seen a developer programing fixture or two but nothing meant to process thousands of units. So naturally this is where I started.

# Rev 1

I started off at [McMaster Carr](http://www.mcmaster.com) browsing their “Spring Test Probes”. (McMaster does an incredible job of breaking down products into their simplest forms and then explaining all the variants they carry. Good resource if you’re just getting started on a project.) These were rather large. The smallest was 0.050” but given the overwhelming selection at Mouser and the lack of a DigiKey catalog to actually see what the components looked like, I went with the McMaster selection for the first go. The ABS plastics of the product case was used for alignment to make life a little easier. I offset the pins from the outer edge (2 data, 2 power, and a pin grounded for the bootloader), found some scrap acrylic that was roughly a good thickness, and started cutting.

![](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/01.jpeg)

I never got this variant to work. All the pins looked to be hitting correctly on their pads, albeit not reliably, but it would never connect to the computer when powered on. The root cause of this I wouldn't find out until I was on rev 4.

# Rev 2

![Rev 2, or what really should have been 1.5](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/02.jpg)

Rev 2, or what really should have been 1.5

Rev 2 needed to have smaller pogo pins and better alignment. Ditched the plastics and put dowel holders on the board. Offset the pins again cut out a new plate on the laser cutter andddd same issue. This really should have been rev 1.5 and not 2. I wrongly assumed the pins were not making good enough contact and needed to be more precisely aligned. Pit falls of sticking to what you know and not considering what you don't.

# Rev 3

In comes Rev 3. Full redesign. After talking to some friends who know more than me in the electrical world, I found some very small pogo pins which were replaceable should they break and which I could get close enough to each other for the pads I was attempting to hit on the board. This was designed with a full manufacturing line in mind and not just a single person doing re-work of returned products. Clamps, lots of room around the components should something go wrong and need to be fixed, and strikingly good looks. It almost looks like a real thing at this point and not a shitty side project. I built only one of these which suffered the same fate at the others. The project was shelved until I could figure out why the device wasn't mounting to the computer.

# Rev 4

![](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/03.jpeg)

This is where the deadline comes into play. A hard deadline. Roughly a half week after I designed and build rev 3, we were in need of the capacity to program tens of thousands of units. We needed 24 working fixtures by Friday. 6 Days. I pulled rev 3 off the shelf and began attempting to tune in the design. Luckily at this point I had some electrical hardware guys helping who pointed out that the data lines needed to be *exactly* the same length. This hadn't occurred to me and was exactly why none of the other fixtures had produced good results. Because USB is *so fast* if the two data lines at not exactly the same length you will get errors in the transmission. [Differential signal transmission](https://en.wikipedia.org/wiki/Differential_signaling) got added to my vocabulary (such an elegant solution to interference). Looking back at rev 1,2, and 3 with no wire management you can see why I would have a ton of noise in the signal lines. But, this revision worked! And in our brief testing (5 times) it worked 4/5 times. Good enough to attribute to construction and manufacturing errors. Time to make 24 of them...

![](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/04.jpeg)

With the parts laser cut and ordered we flew everything out to the work site and begin assembling. Testing started after 4 of the fixture were assembled. 2 of the 4 worked flawlessly. The other two had fits and starts. Not powering and then not mounting the device to the computer which I thought was a solved problem with our better wire management. All in all, there was about a 85% success rate with rev 4. Not bad but not the 100% confidence we needed. It was Tuesday and the deadline had been extended to Monday. There was another solution prepped and given I thought most of the issues were still alignment related, we elected to go with a CNC milled top hopping that this would be the final revision and to completely rule out any precision related tolerance issues.

In hindsight there were actually 4 things still majorly broken at this point:

We DID need more precision but the lack of it was due to both the process (laser cutting) and the material (acrylic).

The pin we were using for the boot loader was continually connected causing failures midway through loading the software onto the boards.

It was possible to apply power to the board before all the data pins were securely connected.

The two tiered design I had for constraining the pins was actually over constrained and causing poor alignment.

I have no idea how we were getting 85% success at this stage.

# Rev 5

![First cut of Rev 5 our of acrylic still](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/05.jpeg)

First cut of Rev 5 our of acrylic still

To fix some of the alignment issues, we switched to a single thicker top plate for constraining the spring pins. We had been using acrylic up to this point mainly because of the laser cutter which, after the first cut for rev 5, I was kindly reminded by our [machinist](http://4130cycleworks.com) what a pain it was to work with on the mill. His suggestion was to use [StarBoard](http://www.kingplastic.com/products/king-starboard/) a marine-grade polymer which is super easy to machine, super light and durable, and crazy cheap for the quantity we wanted. 25 12" x 12" x 3/4" boards were around $150. Perfect.

![](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/06.jpeg)

While this was going on, another electrical inclined friend of mine based in our SF office taught me the difference between clean and dirty grounds. I had been making use of the dirty USB case ground to short out a pin on the NAND flash to invoke the boot loader. This caused some of the failures once the device was mounted on the computer due to the noise introduced into the system. Hence, “dirty” ground.

He made a makeshift sheath around the data usb lines going to the pins using the dirty ground. The data lines were as short as possible and now more insulted from the environment. The clean ground was routed through a toggle switch so we could remove the link between it and the bootloader pin once the download started. We then routed the power through a spate toggle switch of ease of use rather than having the board powered the second it touched the spring pings. Much more elegant. And better yet, it worked. Flawlessly and easily.

And finally… Rev 5

![Beauty ain’t she?](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/07.jpeg)

Beauty ain’t she?

![](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/08.jpeg)

The next 48 hours were a scramble to get the rest of the plastics, clean out two Radio Shacks of toggle switches, and soldering the new USB to spring pin harnesses for the 24 fixtures we needed. But at the end of the day:

![Rev 5 in use. They got stickers for how many days they went without the need for repair. ](/assets/blog/how-i-learned-to-build-a-manufacturing-fixture-in-3-weeks/09.jpeg)

Rev 5 in use. They got stickers for how many days they went without the need for repair.

Some notes on timelines:

- The whole process spanned roughly 3 weeks total.

- The majority of the work and the last 3 revisions were completed in less than 7 days.

- Rev 4 -> rev 5 was completed in less than 24 hours.

Some notes on the problems encountered in the build:

- When you use charge in a wire to communicate data (often called a signal) you better remember your physics.

- I still have a ton to learn about electronics and the design of electrical systems.

- Solving problems by yourself can lead to elegant solutions but you can get there faster with good friends.

- Starboard is my new favorite material. Seriously easy to work with.

There’s a lot more detail to this story and the context that prompted the need for this build but that really should be discussed [over a coffee](/#contact).
