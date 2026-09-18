## 1. Definition of variables and parameters
**Sets**
- $EC$ : energy communities (EC)
- $E$ : feed-in metering points (FMP)
- $V$ : consumption metering points (CMP)
- $Z$ :=  $E \cup V$ (all metering points)
- $T$ : 15-minute time steps
  - $H$ : hours of the day, $H=\{1,\dots ,24\}$
  - $D$ : days in the planning horizon

**Parameters (known data)**
- REC membership parameter
  - $m_{z,ec} \in \{0,1\}$, with $m_{z,ec}=1 \leftrightarrow z \text{ is a member of energy community } ec$
  - Note: since the code will only ever load the relevant data anyway, i.e. only the metering-point data of the energy community in question, this parameter could be dropped, with the goal of parameter reduction.

- Participation factor at the initial state
  - $pf_{z,t,ec}$ : participation factor
  - Initial state in the current data set: $pf_{z,t,ec} = 100, \forall Z,\forall T,\forall EC$

- For every FMP $e \in E$ and time $t \in T$:
  - $g_{e,t,ec}$ : generation (kWh), how much electricity this metering point generated in total
  - $s_{e,t,ec}$ : surplus (kWh), how much of the generated electricity is, in the context of the REC, surplus and fed into the grid
- For every CMP $v \in V$ and time $t \in T$:
  - $c_{v,t,ec}$ : consumption (kWh), how much electricity this metering point consumed in total
  - $cc_{v,t,ec}$ : community coverage (kWh), how much electricity the metering point could draw from the REC
  - $cp_{v,t,ec}$ : community potential (kWh), how much electricity the metering point could have obtained from the REC. Under under-coverage, this equals the community coverage.

All parameters $\ge 0$.

**Computing the totals**
- Total feed-in at $t$: $G_{t,ec} := \sum_{e \in E} g_{e,t,ec}$
- Total consumption at $t$: $C_{t,ec} := \sum_{v \in V} c_{v,t,ec}$
- REC self-coverage ratio: $a_{t,ec} = :min\{1, \frac{G_{t,ec}}{C_{t,ec}}\}, \forall t \in T$

- Total REC coverage at $t$: $CC_{t,ec} := \sum_{v \in V} cc_{v,t,ec}$

- Surplus: $G_{t,ec} \ge C_{t,ec}$
  - Surplus time steps: $T_{ec}^{S} := \{t \in T | G_{t,ec} \ge C_{t,ec}\}$
- Under-coverage: $G_{t,ec} < C_{t,ec}$
  - Under-coverage time steps: $T_{ec}^{U} := \{t \in T | G_{t,ec} < C_{t,ec}\}$

**Decision variable**
- $pf_{z,t,ec}^{\text{*}} \in \mathbb{N}\cap[0,100], \forall{z \in Z}, \forall{t \in T}, \forall{ec \in EC}$ = participation factor for all metering points belonging to those ECs of which the metering point is a member
  - $pf_{z,t,ec}^{\text{*}} \le 100 \cdot m_{z,ec}, \forall z,t,ec$
    - it follows that: if $m_{z,ec}=0 \Rightarrow pf_{z,t,ec} \le 0 \Rightarrow pf_{z,t,ec} = 0$
  - $pf_{z,t,ec}^{\text{*}} \ge m_{z,ec}, \forall z,t,ec$
    - it follows that: if $m_{z,ec}=1 \Rightarrow pf_{z,t,ec} \ge 1$
  - $\sum_{ec \in EC}pf_{z,t,ec}^{\text{*}} \le 100, \forall z,t$

- Daily participation-factor schedules
  - Note: in reality the participation factor can currently only be set on a daily basis, not for each individual quarter-hour
  - let $D$ be the set of days in the schedule, then for each day $d \in D$ the set of 15-minute intervals is: $T_d=\{t\in T ∣ t \text{ lies within day } d\}$
  - Constraint for daily equality:
  - $$\forall z \in Z, \forall d \in D, \forall t_1, t_2 \in T_d: pf_{z,t_1,ec}^{\text{*}} = pf_{z,t_2,ec}^{\text{*}}$$
  - $$pf_{z,t,ec}^{\text{*}} = pf_{z,d,ec}^{\text{*}} , \forall t \in T_d$$
  -
- Hourly participation-factor schedules
  - Note: soon, once legislation changes, the participation factor should also be settable hourly, so we should already compute solutions for that now
  - let $H$ be the set of hours in the schedule, then for each hour $h \in H$ the set of 15-minute intervals is: $T_h=\{t\in T ∣ t \text{ lies within hour } h\}$
  - Constraint for hourly equality:
  - $$\forall z \in Z, \forall h \in H, \forall t_1, t_2 \in T_h: pf_{z,t_1,ec}^{\text{*}} = pf_{z, t_2,ec}^{\text{*}}$$
  - $$pf_{z,t,ec}^{\text{*}} = pf_{z,h,ec}^{\text{*}} , \forall t \in T_h$$


**Derived variables**

- $g_{e,t,ec}^{\text{*}} := g_{e,t,ec} \cdot \frac{pf_{e,t,ec}^{\text{*}}}{100}$, optimised generation
- $c_{v,t,ec}^{\text{*}} := c_{v,t,ec} \cdot \frac{pf_{v,t,ec}^{\text{*}}}{100}$, optimised consumption
- Total feed-in after optimisation (via the participation factor): $G_{t,ec}^{\text{*}} = \sum_{e \in E} g_{e,t,ec}^{\text{*}}$
- Total consumption after optimisation: $C_{t,ec}^{\text{*}} := \sum_{v \in V} c_{v,t,ec}^{\text{*}}$
- REC self-coverage ratio after optimisation: $a_{t,ec}^{\text{*}} := min\{1, \frac{G_{t,ec}^{\text{*}}}{C_{t,ec}^{\text{*}}}\}, \forall t \in T$
- REC surplus ratio after optimisation: $u_{t,ec}^{\text{*}} := max\{0, \frac{G_{t,ec}^{\text{*}}-C_{t,ec}^{\text{*}}}{G_{t,ec}^{\text{*}}}\}, \forall t \in T$

- $s_{e,t,ec}^{\text{*}} := g_{e,t,ec}^{\text{*}} \cdot u_{t,ec}^{\text{*}}$, optimised surplus
- $cc_{v,t,ec}^{\text{*}} := c_{v,t,ec}^{\text{*}} \cdot a_{t,ec}^{\text{*}}$, optimised community coverage
- $cp_{v,t,ec}^{\text{*}} := c_{v,t,ec}^{\text{*}} \cdot \frac{G_{t,ec}^{\text{*}}}{C_{t,ec}^{\text{*}}}$, optimised community potential

- Total REC coverage after optimisation: $CC_{t,ec}^{\text{*}} = \sum_{v \in V} cc_{v,t,ec}^{\text{*}}$

## 2. Constraints
### 2.1 Hard constraints
- All parameters $\ge 0$

- $cc_{v,t,ec}^{*} \le c_{v,t,ec}^{*}$
- $c_{v,t,ec}^{*} \le c_{v,t,ec}$
  - should hold anyway, since $pf_{v,t,ec}^{*} \le 100$

- on energy community sums:
  - $CC_{t,ec}^{*} \le C_{t,ec}^{*}$
  - $CC_{t,ec}^{*} \le G_{t,ec}^{*}$
  - $S_{t,ec}^{*} = min(0, G_{t,ec}^{*} - C_{t,ec}^{*})$

### 2.2 Soft constraints
- Surplus must be preserved
  - If $G_{t,ec} \ge C_{t,ec} \Rightarrow G_{t,ec}^{\text{*}} \ge C_{t,ec}^{\text{*}}$
    - alternative annotation: $\forall t \in T^{S} : G_{t,ec}^{\text{*}} \ge C_{t,ec}^{\text{*}}$
- Under-coverage must be preserved
  - If $G_{t,ec} < C_{t,ec} \Rightarrow G_{t,ec}^{\text{*}} < C_{t,ec}^{\text{*}}$
    - alternative annotation: $\forall t \in T^{U} : G_{t,ec}^{\text{*}} < C_{t,ec}^{\text{*}}$

- Absolute REC coverage must not have decreased
  - $CC_{t,ec}^{\text{*}} \ge CC_{t,ec}$

- If surplus exists, no participation factor of the consumers is changed
  - If $G_{t,ec} \ge C_{t,ec} \Rightarrow pf_{v,t,ec}^{\text{*}} = pf_{v,t,ec}$
    - alternative annotation: $\forall t \in T^{S}, \forall v \in V: pf_{v,t,ec}^{\text{*}} = pf_{v,t,ec}$
- If under-coverage exists, no participation factor of the feed-in points is changed
  - If $G_{t,ec} < C_{t,ec} \Rightarrow pf_{e,t,ec}^{\text{*}} = pf_{v,t,ec}$
    - alternative annotation: $\forall t \in T^{U}, \forall e \in E: pf_{e,t,ec}^{\text{*}} = pf_{v,t,ec}$

## 3. Optimisation
### 3.1 Scenario: optimisation within a single REC

General goals:
- As much electricity as possible should be distributed and drawn within the REC, and as little as possible from the grid.
- It follows that the consumers' goal is compatible with the producers' goal, and both groups follow a common objective.
  - Consumer perspective: want to draw as much electricity as possible from the REC and not from the grid
  - Producer perspective: want to distribute/"sell" as much electricity as possible within the REC and not feed it into the grid

#### 3.1.1 Optimisation goal: equality of the allocated absolute community coverage
Problem description:
- every consumption metering point $v \in V$ should receive the same absolute amount of electricity (kWh) from the energy community $cc_{v,t,ec}$. Metering points that need less electricity (their consumption $c_{v,t,ec}$) cannot receive more electricity from the REC either (constraint: $cc_{v,t,ec} \le c_{v,t,ec}$). Consequently the resulting *remainder* is again distributed equally to all other metering points.
- Note: currently we have solved this optimisation goal iteratively for every single quarter-hour. Our next goals are:
  - 1. to have a formalisation for linear optimisation instead of the iterative approach
  - 2. to compute this absolute equal distribution not on a quarter-hour basis, but to be able to choose larger time horizons. From a domain perspective, daily and monthly horizons are particularly interesting, because currently the quarter-hour-optimised values do not lead to an hourly or daily optimum. (see screenshots further below)

- with the "water-filling"/"equal-share" problem
$k_t = \frac{G_t}{|V_t|}$

1. Initialisation
   - $a_{v,t}^{(0)} \leftarrow 0, \forall v \in V$ (amount allocated so far)
   - $r_{v,t}^{(0)} \leftarrow c_{v,t}, \forall v \in V$ (full demand)
   - Set $R_t^{(0)} := G_t$ (amount of electricity still to be distributed)
   - Set $U^{(0)} := V$ (CMPs that can still receive electricity / are not yet *saturated*)
2. Iteration $i=0,1,2,\dots$ while $R_t^{(i+1)} > 0$ or $U^{(i+1)} \ne \emptyset$
   1. Fair-share amount for the current round
      - $a_t^{(i)} = \frac{R_t^{(i)}}{|U^{(i)}|}$
   2. Allocation for each still-active consumer
      - $a_{v,t}^{(i+1)} = min(r_{v,t}^{(i)}, a_t^{(i)}), \forall v \in U^{(i)}$
   3. Update the remaining open demand
      - $r_{v,t}^{(i+1)} = r_{v,t}^{(i)} - a_{v,t}^{(i+1)}, \forall v \in U^{(i)}$
   4. Update the remaining amount still to be distributed
      - $R_t^{(i+1)} = R_t^{(i)} - \sum_{v \in U^{i}} a_{v,t}^{(i+1)}$
   5. Update the set of CMPs that can still receive a remainder
      - $U^{(i+1)} = \{v \in U^{(i)} | r_{v,t}^{(i+1)} > 0\}$
   6. Result:
      - $a_{v,t} = \sum_{i \ge 0}a_{v,t}^{(i)}, \forall v \in V$
      - $pf_{v,t}^{\text{*}}  = \frac{a_{v,t}}{c_{v,t}} \cdot 100$

#### 3.1.2 Optimisation goal: equality of the distributed absolute consumed generation
Consumed generation: how much of the generated electricity was consumed within the EC
- $cg_{g,t,ec} := g_{e,t,ec}  - s_{e,t,ec}$

Problem description:
- every feed-in metering point $e \in E$ should distribute/sell the same absolute amount of electricity (kWh) to the energy community $cg_{e,t,ec}$. Metering points that generate less electricity (their generation $g_{e,t,ec}$) cannot distribute more electricity to the REC either (constraint: $gc_{e,t,ec} \le g_{e,t,ec}$). Consequently the resulting *remainder* of generated electricity still to be distributed is again distributed equally to all other feed-in metering points.

- with the "water-filling"/"equal-share" problem
$f_t = \frac{C_t}{|E_t|}$

1. Initialisation
   - $a_{e,t}^{(0)} \leftarrow 0, \forall e \in E$ (amount to be distributed so far)
   - $r_{e,t}^{(0)} \leftarrow g_{v,t}, \forall e \in E$ (full generation -> maximum amount that can be distributed)
   - Set $R_t^{(0)} := C_t$ (amount of electricity still to be covered)
   - Set $U^{(0)} := E$ (FMPs that can still distribute electricity / are not yet *exhausted*)
2. Iteration $i=0,1,2,\dots$ while $R_t^{(i+1)} > 0$ or $U^{(i+1)} \ne \emptyset$
   1. Fair-share amount for the current round
      - $a_t^{(i)} = \frac{R_t^{(i)}}{|U^{(i)}|}$
   2. Allocation for each still-active producer
      - $a_{e,t}^{(i+1)} = min(r_{e,t}^{(i)}, a_t^{(i)}), \forall e \in U^{(i)}$
   3. Update the remaining open demand
      - $r_{e,t}^{(i+1)} = r_{e,t}^{(i)} - a_{e,t}^{(i+1)}, \forall e \in U^{(i)}$
   4. Update the remaining amount still to be distributed
      - $R_t^{(i+1)} = R_t^{(i)} - \sum_{e \in U^{i}} a_{e,t}^{(i+1)}$
   5. Update the set of CMPs that can still receive a remainder
      - $U^{(i+1)} = \{e \in U^{(i)} | r_{e,t}^{(i+1)} > 0\}$
3. Result:
      - $a_{e,t} = \sum_{i \ge 0}a_{e,t}^{(i)}, \forall e \in E$
      - $pf_{e,t}^{\text{*}}  = \frac{a_{e,t}}{g_{e,t}} \cdot 100$

#### 3.1.3 Optimisation goal: Nash social welfare
Weighting parameter $\alpha$:= $0 <= \alpha <= ...$

1. Initialisation
    -  $d_{v} \leftarrow c_{v}, \forall v \in V$ (demand, how much can at most be allocated to a metering point)
    -  $n = |V|$ (number of participants)
    - $d_i \in \mathbb{R}_{\ge 0}$


Objective function: $\max_{A} \sum_{i}w_{i} \cdot \log(A_{i})$
- Corresponds to maximising the weighted Nash product
- Promotes proportional fairness

Constraints:
- Individual demand limit
  - No participant may receive more than their demand
  - $A_i \le d_i, \forall i \in V$
- Global resource limit
  - The total distributed resource must not exceed the pool
  - $\sum_{i \in V} A_i \le P$
- Non-negativity
  - $A_i \ge 0, \forall i \in V$

Full optimisation problem
$$
\begin{aligned}
\max_{A_{1}, \dots, A_{n}} \quad
& \sum_{i \in V} w_i \cdot \log(A_i) \\[0.5em]
\text{s.t.} \quad
& A_i \le d_i, \quad \forall i \in V \\[0.3em]
& \sum_{i \in V} A_i \le P \\[0.3em]
& A_i \ge 0, \quad \forall i \in V
\end{aligned}
$$
