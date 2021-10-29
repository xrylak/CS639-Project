# Traffic Livestream Analysis
##Problem
In terms of traffic, connectivity is costly. As cars overburden the streets of the US, our world
becomes increasingly congested. Especially in larger cities, where around 90% of daily
commuters use private vehicles, policymakers struggle to find tenable solutions (2). One
commonly utilized option is physically expanding the capacity of roads, but urban planners are
often hard-pressed in finding locations in which to allocate valuable resources into roads, but
the construction required is often unrealistically costly in terms of both resources and money.
Additionally, these massive roads would be grossly unnecessary during non-peak traffic hours,
and once word got around that the road had expanded, people would flood in, and congestion
would re-appear. This dilemma hints at the true problem, of which congestion is only a
symptom. The true problem is the fact that the majority of people commute using specific roads
at specific times of the day, colloquially known as “rush hours”.
Why it needs to be solved
There are multiple reasons why solving the problem of rush hours would help our society. One
easily identifiable one is gas. For example, take New York, where during rush hour traffic,
commutes are increased by an average of 27 minutes. Factor in the number of people
commuting and average amount of fuel consumption per car, and you get about 12.5 billion
dollars of wasted fuel every single day (1). Another reason is personal health. Recent studies
have shown that during rush hours, the interiors of cars can become filled with dangerous levels
of pollutants (3). Additional broad reasons include environmental impact and overall productivity.
For all these reasons and more, it’s clear that striking a blow at the problem of rush hours would
be greatly beneficial, both on a personal and societal level. Our project aims to provide a step in
this direction.
##Proposed Solution
The solution to lessening the negative productivity and environmental impact of rush hour traffic
involves gathering data about where it occurs and its severity. Thus drivers can be better
informed about where to drive and at what hours of the day. Our proposed solution involves an
algorithm that, given the input of a live stream video of a stretch of road, outputs the
location/bounding boxes of vehicles on this road and their projected velocities in order to gauge
traffic speed. Choices arise in how best to detect these vehicles: either through image filtering
and motion-detecting techniques or a deep learning model trained to detect vehicles. We will try
both approaches, comparing each on detection accuracy and speed, and continue down the
most promising route. As our video will be fed in from a live stream, accurate predictions must
also be quick to compute. We will also have to determine a way to find accurate speeds of the
vehicles regardless of camera angle. A potential solution to this problem might be deducing
scene geometry from parallel road lines and extrapolating relative car position and thus velocity
from the movement in position. From this extracted data we can build useful traffic tools to help
individuals or cities analyze traffic patterns and plan their routes or infrastructure changes
accordingly. After successfully implementing this algorithm, we plan on attaching it to multiple
live streams and running it over the course of many days to gather enough data to do analysis.
With this data, we can produce metrics such as traffic speed vs. time at a certain location and
heat maps of traffic over time.
##Applications/Analysis
Numerous applications can be made of the solution provided. One such application might be
identifying outliers in the data, such as people moving at a significantly different speed
compared to the rest of the traffic. This could potentially help law enforcement catch problematic
drivers and determine which locations they are most populated in. If a heat map were made of
numerous roads indicating the congestion hotspots this solution would also benefit future road
design plans by identifying problematic designs which do not work. Another unique application
would be detecting congestion at drive-throughs which will help people decide if they truly want
to go to a particular restaurant.
##Timeline
● Mid/Late October: Recognize car from video
● Start November: Accurately calculate velocity of moving vehicles
● Mid November: Apply recognition to livestream(s) and begin data collection
● Late November: Build analysis tools / apply gathered data
● December: Produce finished demo and analysis of all collected data
###Sources
1: https://www.theatlantic.com/sponsored/hitachi-building-tomorrow/global-rush-hour/237/
2: https://www.brookings.edu/research/traffic-why-its-getting-worse-what-government-can-do/
3: https://www.triplepundit.com/story/2017/health-impacts-rush-hour-pollution/16231


































































































### Contributors
Anders Carlsson (awcarlsson@wisc.edu), Fritz Ringler (fringler@wisc.edu), Casey Frank (csfrank3@wisc.edu)
