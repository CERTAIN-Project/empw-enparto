Every formulation of "weighting" is also an optimisation factor
- in two ways:
  - either as a given / input parameter
    - either as an exact target value that must be met
    - or as a range within which the optimiser can move
  - or the optimisation itself tries to push the given concrete weighting in a certain direction

## Single EEG (energy community):
- Every consideration of the following optimisation concerns the participation factors (PF) per individual time unit (15 minutes) -> #TODO formalise these rules mathematically
	- Setting for a single hour only: weight 4 values (because 1h / 15min -> 4)?
	- same for daily schedules: weighting of 96 values?


- for the "dimension" of time, e.g. how the 4 quarter-hour values within an hour are weighted for the respective optimum
	- Average?
	- Average, but only from a certain outlier/size onward
	- are there also constraints / basic requirements here

### Energy amounts (kWh)
#### Constraints / basic requirements
- Reduce consumption from the REC
	- Sticking point
	  Only if there is under-coverage. PF change only if not the entire electricity consumption is covered.
- Reduce feed-in to the REC
	- Sticking point
	  If there is surplus, and after the PF change there is no longer any surplus
- When do these checks need to be applied?
---
### Concrete computation goal
- **Absolute** consumption is the same for everyone
- Feed-in / sale within the REC is the same for everyone
	- Documentation: if we implement it this way, how much energy is moved -> what are the effects for both sides


---
PF change only for **outliers**
- Not all metering points are equalised or reduced, only those that deviate by, e.g., more than 2 sigma.

---
Compute and take into account **behind-the-meter**
- Assign feed-in points to consumers
- Look at how large the feed-in point is
- from that, compute approximately how much is generated and approximately how much more is consumed

- or fair anyway, because they also generate
---
- **Credit system**?
	- whenever a household feeds in, it receives "credits"
	- which "benefit" it when it has consumption during under-coverage in the REC, and is thereby "preferred"


---

### Costs

- REC price tracks the spot market so it is never **more expensive**
	- **consumer**-oriented
- REC price tracks the spot market so it is never **cheaper**
	- **feed-in**-oriented

! EDA: how large is the current respective cost difference, common "fair" price distribution
Fair:
- Example: for consumers and producers respectively 50/50 averaged over the difference of their respective cost optima


Control not from the perspective of the REC, but each metering point controls itself individually and optimises itself. -> Experiment: what comes out of that? Are there stable states?
- Does that make sense? or would it eventually turn out that


## Multiple EEGs (energy communities)

Basic consideration: which metering points should/may be shifted?
- only the feed-in points (to where electricity is needed)
- only the consumption points (to where electricity is currently available)
- or both
  - makes the optimisation effort larger, because both "sides" (feed-in AND consumption) have to be *balanced*

### Two EEGs
Different generation profiles:
- e.g. 1st EEG combining only PV with a 2nd EEG with hydropower
  - Idea: shift consumers from EEG 1 into EEG 2 when, thanks to hydropower, EEG 2 still has surplus during "non-PV times"

- 2 possible conflicts of interest: -> #TODO formalise these rules mathematically
  - too much additional consumption arrives in EEG 2, causing under-coverage there
    - and consequently the consumers from EEG 2 receive less community coverage
  - too much consumption is taken away from EEG 1, causing surplus there
    - and consequently the feed-in points in EEG 1 can distribute less electricity within the EEG (we cause grid feed-in)
    - this aspect is only relevant if EEG 1 also has hydropower
      - because if not, generation during "non-PV times" is 0 anyway, so surplus can never occur

This scenario cannot occur in reality:
- because "shifting energy amounts" between EEGs always technically requires a BEG (larger/umbrella energy community)

### x EEGs + 1 BEG
- the consumers from the EEGs are also members of the BEG
- the BEG has different generation profiles due to hydropower

- Distinction:
  - whether the producers are only in the BEG
  - or whether the producers are also in an EEG -> and consequently the producers also need multiple participation

Concrete optimisation idea: -> #TODO formalise these rules mathematically
- each EEG is optimised individually, based on AP4 -> the result is the grid draw of the consumers
- this grid draw of the individual consumers is then consumed in the BEG
- how much consumption the individual consumers receive from the BEG is optimised in the same way as in the EEGs, i.e. with AP4
- Consideration:
  - this variant treats consumption in the BEG at the metering-point level, each metering point (regardless of its EEG) is treated equally
  - Alternative: the BEG takes into account the originating EEG of the individual metering points, so that each EEG is treated equally in absolute sums
    - in our view problematic, because this favours small EEGs, which runs counter to the fundamental goal definition of EEGs

The following point is only relevant if producers are in both the EEG and the BEG -> #TODO formalise these rules mathematically
- as a consequence of the fact that in reality the PF must be assigned not for 15 minutes but for 1 hour, the following question arises:
  - should optimisation be done from the producers' perspective: so that they sell as much electricity as possible within the BEG through BEG participation
    - with the consequence that under-coverage arises in the EEG, and consequently the consumers from the EEG have less community coverage
  - or from the consumers' perspective, so that they always get maximum community coverage
    - with the consequence that the producer has to sell to the grid as well

Additional complexity factor: -> #TODO formalise these rules mathematically
- in reality it can/will be the case that not all EEG participants are also BEG participants
- consequently these consumers (who are not BEG members) also cannot receive electricity from the BEG
- Question: should the EEG optimisation take this into account?
  - and then, e.g., give these consumers a bit more from the start?

Assumption:
- electricity from the EEG always costs the same as from the BEG -> consequently we only optimise on energy amounts, not costs

Idea:
- storage must not store grid electricity, because it would otherwise be a money-printing machine
- but may storage store BEG electricity?
  - if yes: buy electricity when BEG electricity is cheap, and then sell it expensively in the EEG
    - should not actually be problematic, because it is grid-friendly behaviour -> BEG electricity gets used

Notes:
- hydropower and wind power are to be regarded as "synonyms" here, because the only point is that these generation technologies can also produce electricity when PV does not

### x EEGs + x BEGs
- first intuition: extremely complex (& not the St. Pölten example) -> therefore out of scope for EnPartO

---
## Appendix
Terms/Abbreviations:
- PF ... Participation Factor
- EEG ... Renewable Energy Community
- Households ... set of consumption and potential feed-in metering points
