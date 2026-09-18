**Features**:
- Comparing the hourly representation via .max
	- effect of comparing 15min to hourly, however these are computed
- Analyse daily PFS potential across multiple RECs and multiple time horizons
- Implement capped water-filling
- Show status quo
- Order of applying the optimisation algorithms / pipeline to the energy data:
	1. Different time horizons of org_id=1
	2. Different org_id -> find peculiarities

**Metrics**:
([[251218 Linear Optimisation with Martin Lackner]] -> strict separation of metrics and optimisation algorithms)
- Use several metrics (3-5) to assess the PF schedule
	- Gini(absolute comm_cov)
	- Gini(relative comm_cov coverage of cons)
		- should be 0 at the baseline
	- Absolute "unused/lost" comm_cov/cons_gen
	- Relative "unused/lost" comm_cov/cons_gen
	- min, max, range, q1,2,3, std, mean, median of ..... per metering point
		- relative comm_cov coverage of cons
		- relative delta of cc coverage to cc* coverage of cons
		- + absolute differences / possibly scale?, and absolute delta
- Dependency of Gini on the exhausted potential of comm_cov

**Pipeline**
- Load raw energy data, params + db -> feather
	- schema: ...
- Clean energy data, feather -> feather
- Calculate participation-factor schedule, feather + OptAlgo -> feather
	- schema: org_id:int, mp_id:int, timestamp:datetime(15min, hourly, daily), pf: float
- Apply PFS to simulate energy data, feather + feather -> feather
	- schema: ...
	- artifact metadata: org_id of the energy data (ed), time horizon of ed, opt algo (+ version), preprocessing (+ v)
- Evaluate single PFS with simulated energy data, feather -> html plotly dashboard
- Compare multiple PFS on the same energy data, feather X -> html plotly dashboard
(? comparison of the same/or multiple PFS optimisation algorithms on different EEGs)
!create draw.io diagram


**Software engineering:**
- Managing optimisation-algorithm logic:
	- each different approach is its own class
	- ``class OptAlgo(params dict):
		- ``calculateParticipationFactorSchedule(energy_data dataframe)
	- Input is always the whole energy data with all timestamps and all metering points. Same for output. Different hard rules for different subgroups of time and/or metering points have to be managed within the optimisation-algorithm implementation. The class/methods above check the completeness of the input data
- Managing persistence of data analysis:
	- Notebooks are used exclusively for prototyping. "Final" results must not be notebooks.
	- The artifact results of any analysis (of source data, PFS evaluations & comparisons, ...) are stored as Plotly HTML files with unique filenames
		- (i.e. execution timestamp / or just an ID with a metadata dict, depending on how many metadata fields exist per dashboard)
- Creating a persistent and efficiently reusable Plotly dashboard
	- Plotly charts are no longer built entirely within a single function as is currently the case. Instead the individual steps/layers of a chart (structure, colours, text, layout) are built step by step by separate functions/interfaces. The same applies to later assembly into a full dashboard/HTML export
	- This should make it easier to create new dashboards and later uniformly change colour, text, etc. across all charts


**Literature research**
*on Martin's topics, + algorithm implementation*
1. "(Fair) Public Decision Making", "Collective Utility Function"
2. Reference book: Moulin, Axioms of Cooperative Decision Making
3. Papers:
	1. Conitzer, V.; Freeman, R.; and Shah, N. 2017. Fair public decision making. In Proceedings of the 2017 ACM Conference on Economics and Computation, 629–646.
	2. Freeman, R.; Zahedi, S. M.; and Conitzer, V. 2017. Fair and efficient social choice in dynamic settings. In Proceedings of the 26th International Joint Conference on Artificial Intelligence (IJCAI-2017), 4580–4587. ijcai.org.
	3. Freeman, R.; Zahedi, S. M.; Conitzer, V.; and Lee, B. C. 2. Dynamic proportional sharing: A game-theoretic approach. Proceedings of the ACM on Measurement and Analysis of Computing Systems, 2(1): 3:1–3:36.



**Back office**
1. Code documentation
	1. Structure of the csv/parquet files and artifacts within the pipeline
	2. Execution of the scripts, details on the logic
	3. Required params, etc...
2. Document the application of the code + interpret and document the evaluations
