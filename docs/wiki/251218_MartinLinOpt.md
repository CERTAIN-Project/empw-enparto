Which variables do we actually need for the linear optimisation?
- and which variables are so central to the problem that we have to introduce them from the start
- 3.1. general goal definition: the 2 goals are actually one and the same goal, just defined from 2 different perspectives.


Problem statement:
- **Separate** the applied algorithm from the assessment of the distribution
	- **Metrics**: Gini alone is too simplistic for our problem
		- do not search for a single metric, instead combine several sensibly to capture all relevant perspectives
			- combine metrics: show what Gini=0 would mean, and that in that case the distributed energy amount is "too small", and what minimal Gini looks like at maximal distributed energy amount
			- Gini on absolute CommunityCoverage & Gini on CommunityCoverage/Consumption
		- roughly 3-5
		- our problem cannot be reduced to a single figure
		- in the end an REC must decide which perspective it wants to support (e.g. balance between small and large consumers)
	- Algorithms:
		- status quo, current baseline, etc...
		- and then evaluate against the metric combination under all perspectives


- Different agents with a utility function (how happy is the agent)
	- the UF itself is interchangeable; for now all CMPs have the same utility function
		- sensible to define it so the value is between 0 - 1
			- necessarily depends on the CUF
			- it certainly makes a difference whether it is normalised or not
			- what best captures participant satisfaction
	- -> Collective Utility Function (try to make as many agents as happy as possible) -> this CUF is the optimisation goal, maximising "social welfare" (overall satisfaction)
		- 2 options
			- the whole period (1 month) as a single/**global** optimisation goal
			- or **sequentially**, optimise 15min after 15min: we first optimise the first 15min for social welfare, then the next 15min, such that the last 30min are optimised under the constraint that the first 15min can no longer be changed
	- 3 methods for how we define collective utility:
		- sum, linear model
			- sum does not care about minorities
		- egalitarian / (**leximin** is the most sensible variant of this): try to make the unhappiest participant as happy as possible
		- Nash product: consider the product of utilities. A *compromise* between sum and leximin

"Public decision making" -> the allocation of the energy amount -> affects **all** participants -> one decision changes the utility of everyone involved

https://pypi.org/project/gurobipy/

Formalisation:
- explain all information as compactly and as necessarily as possible
- notes on the formalisation:
	- surplus, comm_cov, comm_pot (+ comm_gen) are *actually* functions of cons and gen
	- both water-filling optimisation algorithms only apply for t in surplus or under-coverage respectively
	- current PF definition: missing constraint from m (membership)

Assumptions and topics to ignore:
- hourly PF and integer PF
