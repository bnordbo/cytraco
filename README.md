# Cytraco 2.0

Cytraco is a cycling trainer controller meant to automate interval workouts. It is based on the protocol from Training and Racing With a Power Meter, which states that intervals should continue until their average power drop below a certain level. The level is calculated based on the average power of the interval completing a minimum of 10 minutes of work, or the third interval, whichever comes first:

- 10 min, until 4–6% drop in average power
- 5 min, until 5–7% drop in average power
- 3 min, until 8–9% drop in average power
- 2 min, until 10–12% drop in average power
- 1 min, until 10–12% drop in average power
- 30 sec, until 10–12% drop in average power
- 15 sec, until 10–15% drop in average power

The rationale is that the first two intervals will have artificially high output due to muscles being fresh. To find the true baseline output, a later interval is used. Once the power drops below the cutoff, the workout should end. Adding further intervals at this point would be inefficient, and add fatigue with only maginal adaptation.
