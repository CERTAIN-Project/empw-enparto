# EnPartO

Optimisation of participation factors for renewable energy communities (RECs).

## What this is

A REC (in Austria: *Erneuerbare-Energie-Gemeinschaft*, EEG) lets members share locally
generated electricity among themselves before drawing the remainder from the grid. Each
metering point's share of that shared energy is controlled by its **participation factor**
(`pf`), an integer between 1 and 100. This project develops and evaluates optimisation
algorithms that compute participation-factor schedules for one or more RECs, and a set of
fairness metrics to assess how those schedules distribute energy across members.

See `docs/AP_41_Problem_Formalization.md` for the formal problem statement
(variables, constraints, algorithm definitions) and `docs/AP_41_Optimization_Definitions.md`
for the extended design notes (single-REC and multi-REC scenarios).

## Repository structure

- `src/modules/optimization_algorithms/` — participation-factor optimisation algorithms
  (equal/capped water-filling, fair-share, Nash product and its extended variant).
- `src/modules/fairness_metric_calculator/` — fairness metrics used to evaluate a
  participation-factor schedule (Gini coefficient, Atkinson index, Jain's fairness index,
  Theil index), each with an interpretation table for its output range.
- `src/modules/participation_factor_schedule_evaluator/` — evaluators that apply a fairness
  metric to the resulting energy flow.
- `src/modules/reinforcement_learning/` — a reinforcement-learning environment prototype for
  the same optimisation problem (exploratory; the linear/game-theoretic algorithms above are
  the primary approach — see the design notes for why RL was not pursued further).
- `src/pipeline/` — pipeline scripts wiring the modules above together:
  `02_calculate_pfs.py` and `03_apply_pfs_on_energy_data.py` call the optimisation and
  application logic; `00_extract_energy_data.py`, `01_transform_energy_data.py` and
  `04_analyse_algorithms.py` are placeholders (not yet implemented).
- `src/notebooks/` — exploratory data analysis and prototyping notebooks.
- `docs/` — problem formalisation, design notes, and setup instructions.
- `config/` — pipeline and notebook configuration.

## Setup

See `docs/setup.md` for environment setup and `docs/files.md` for a short guide to the
repository layout.

## License

To be determined.
