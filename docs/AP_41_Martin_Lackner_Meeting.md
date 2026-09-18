Say first:
- the amount produced at time X / number of participants
  - the amount that should be available to everyone
  - distributing the remaining amount to those

1. Everyone is allocated 10 units
   1. everyone gets 10 units, but some need less, e.g. only 8
   2. afterwards X units remain

Temporal perspective!
1. What we actually want to do
   1. then it makes sense to formulate this properly as an optimisation problem

What are the different ways optimisation can proceed?
1. Accept that energy units actually flow back to the grid (are lost to the REC) -> in exchange, guarantee that everyone gets the same amount
2. or optimise these feed-in points so that as little as possible happens (this creates disadvantages for some people)

Linear optimisation is the right approach and makes sense!


! Write down mathematically which quantities exist
Write down as a linear model:
- write our problem statement "mathematically"
- as simple a model as possible, to describe the problem adequately
  - amount of energy consumed by a certain metering point at time t
  - the produced amount
  - something that describes the distribution
- What matters to the individual actors in the system?
  - what does each individual metering point actually want?

**Formalise**
- then state what the objective is! what is to be minimised
- or actually more than 1 goal, each actor has its own objective function

**Linear programming** would be good, nice, but the question is whether it remains expressive enough

----

Variables:
- Set of RECs: "org_id"

- Set of metering points: "mp_id"
  - Set of feed-in metering points (FMP)
  - Set of consumption metering points (CMP)

for every time t there are, for each FMP, the values:
- wt_meas_generation (gen), wt_surp_gen

for every time t there are, for each CMP, the values:
- wt_meas_consumption (cons), comm_cov, comm_pot

If sum(gen of every FMP) >= sum(cons of every CMP): -> surplus
then for every CMP it must hold that: cons == comm_cov



If sum(gen of every FMP) < sum(cons of every CMP): -> under-coverage
then:
- Fair absolute energy amount = (sum(gen of every FMP) / number of CMPs)
- for every CMP:
  - cons = min(cons, fair absolute energy amount)
    - "where cons < 'fair absolute energy amount' -> it must hold that: cons == comm_cov -> its consumption is 100% covered"
  - Remaining amount, which is distributed in the new round = (sum(gen of every FMP)) - sum(cons)
    - if remaining amount == 0 -> optimisation finished, otherwise the rest must continue to be distributed
  - Participants who receive something again in the new round = all CMPs where cons == fair absolute energy amount



for every CMP it must hold that: cons == comm_cov
-----
