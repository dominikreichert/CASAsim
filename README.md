# CASAsim — Circular Automotive Steel and Aluminum simulation model

**CASAsim** is a dynamic material flow simulation model with an embedded linear program (LP) for scrap allocation for assessing the closed-loop recycled content of steel and aluminum in new passenger cars. The model integrates vehicle fleet dynamics, end-of-life vehicle (ELV) recycling chains, and a LP allocation step to determine how much post-consumer and pre-consumer scrap can be used in automotive steel and aluminum production under material quality constraints.

---

## Table of Contents

1. [Scientific Background](#1-scientific-background)
2. [Repository Structure](#2-repository-structure)
3. [Requirements and Installation](#3-requirements-and-installation)
4. [How to Run the Model](#4-how-to-run-the-model)
5. [Model Settings](#5-model-settings)
6. [Input Data](#6-input-data)
7. [Model Calculations](#7-model-calculations)
8. [Optimization Model](#8-optimization-model)
9. [Sensitivity Analysis](#9-sensitivity-analysis)
10. [Output and Exported Data](#10-output-and-exported-data)
11. [Multi-Scenario Analysis](#11-multi-scenario-analysis)
12. [License](#12-license)

---

## 1. Scientific Background

This model is a result of the following scientific publication:

> Reichert et al. (2026). *Closing material loops in the European automotive sector: Closed-loop recycled contents of steel and aluminum.* Resources, Conservation & Recycling Advances. [DOI to be added upon publication.]

CASAsim addresses the question of how much closed-loop recycled content — i.e., scrap derived from ELVs re-used in the production of new vehicle steel and aluminum — is achievable under realistic material flow constraints. The model explicitly accounts for:

- Weibull-based vehicle lifetime distributions and fleet dynamics
- Alloy-specific material qualities (flat steel, long steel, wrought aluminum, low-Cu cast aluminum, high-Cu cast aluminum)
- Multi-route steel production (EAF, BOF, etc.) with route-specific scrap limits
- PST (post-shredder technology) recycling with optional mixed or alloy-specific aluminum outputs
- Dismantling-based selective disassembly prior to shredding
- Material quality thresholds as LP constraints to prevent contamination of end products

---

## 2. Repository Structure

```
CASAsim/
│
├── data/                              # Input data folder
│   ├── data.xlsx                      # Single-scenario input file
│   ├── data_01_<ScenarioName>.xlsx    # Multi-scenario input files
│   ├── data_02_<ScenarioName>.xlsx
│   └── ...
│
├── results/                           # Results folder (auto-generated)
│   └── YYYY-MM-DD_HH-MM-SS/          # Results per model run (named by timestamp)
│       ├── scenario_01/               # Individual scenario results
│       │   ├── data_01_<Name>.xlsx    # Copy of input file
│       │   ├── tmp_import.xlsx        # Imported raw data (for verification)
│       │   ├── tmp_calc.xlsx          # Intermediate calculation results
│       │   ├── *.pdf                  # Result plots
│       │   └── sensitivity_analysis/  # SA results (if enabled)
│       │       ├── *.pdf              # SA plots
│       │       └── tmp/               # SA raw data per parameter
│       ├── scenario_02/
│       └── *.pdf                      # Multi-scenario comparison plots
│
├── main.py                            # Main execution file (entry point)
├── reader.py                          # Input data import module
├── calculator.py                      # Core calculation module (steps 1–8)
├── optimizer.py                       # LP optimization module (Gurobi)
├── analyzer.py                        # Sensitivity analysis module
├── plotter.py                         # Single-scenario result plots
├── plotter_sa.py                      # Sensitivity analysis plots
├── plotter_multi.py                   # Multi-scenario comparison plots
├── writer.py                          # Excel result export module
├── writer_sa.py                       # SA result export module
└── README.md                          # This file
```

### Module Descriptions

| File | Description |
|---|---|
| `main.py` | Entry point. Contains all user-configurable settings (Weibull parameters, plot range, SA toggle). Orchestrates all modules. |
| `reader.py` | Reads all sheets from the input `.xlsx` file and returns structured Pandas DataFrames. |
| `calculator.py` | Implements the eight sequential calculation steps: vehicle contents, registrations, fleet, ELVs, recycling, demand/supply, material use (calls optimizer), and closed-loop rates. |
| `optimizer.py` | Formulates and solves the LP model via Gurobi. Returns optimal material allocation and material quality per production route. |
| `analyzer.py` | Implements `run_sa` and `interpret_sa` for one-at-a-time sensitivity analysis. |
| `plotter.py` | Creates all single-scenario result plots (fleet, registrations, material flows, closed-loop rates). |
| `plotter_sa.py` | Creates sensitivity analysis plots (tornado charts, time-series envelopes). |
| `plotter_multi.py` | Creates cross-scenario comparison plots in a dynamic square grid layout. |
| `writer.py` | Exports all simulation results to Excel. |
| `writer_sa.py` | Exports SA data, including per-parameter result files and total min/max recycled content summaries. |

---

## 3. Requirements and Installation

### Python

Python 3.9 or higher is recommended.

### Dependencies

```
pandas
numpy
scipy
matplotlib
openpyxl
gurobipy
```

Install via pip:

```bash
pip install pandas numpy scipy matplotlib openpyxl gurobipy
```

### Gurobi License

The optimization step requires a valid [Gurobi](https://www.gurobi.com/) license. Academic licenses are available free of charge at [gurobi.com/academia](https://www.gurobi.com/academia/academic-program-and-licenses/).

---

## 4. How to Run the Model

1. Place your input file(s) in the `data/` folder (see [Section 6](#6-input-data) for naming conventions).
2. Configure the model settings in `main.py` (see [Section 5](#5-model-settings)).
3. Execute the main file:

```bash
python main.py
```

Results are automatically saved to a timestamped subfolder in `results/`.

---

## 5. Model Settings

The following parameters can be configured directly in `main.py`:

| Parameter | Type | Description |
|---|---|---|
| `SHAPE` | `float` | Weibull shape parameter *k* for vehicle lifetime distribution (default: `3.2`) |
| `SCALE` | `float` | Weibull scale parameter *λ* for vehicle lifetime distribution (default: `16.75`) |
| `PLOTTER_START_YEAR` | `int` | First year shown in result plots (must fall within the model time span) |
| `PLOTTER_END_YEAR` | `int` | Last year shown in result plots (must fall within the model time span) |
| `PERFORM_SA` | `bool` | Whether to perform sensitivity analysis (`True` / `False`) |
| `SENSITIVITY` | `float` | Relative variation applied in SA (e.g., `0.2` = ±20%) |
| `TARGET_YEARS` | `list[int]` | Years highlighted in SA bar charts (e.g., `[2030, 2050]`) |

---

## 6. Input Data

All input data is provided via Excel files (`.xlsx`) stored in the `data/` folder.

### File Naming Convention

| Mode | File name pattern | Example |
|---|---|---|
| Single scenario | `data.xlsx` | `data.xlsx` |
| Multi-scenario | `data_<ID>_<Name>.xlsx` | `data_01_BAU.xlsx`, `data_02_HighRecycling.xlsx` |

The scenario ID (two-digit integer between `_` and `_`) and name (underscores replaced by spaces) are read automatically. All input files must use the same time span.

### Input File Structure

Only cells with a **gray background** in the Excel file are intended for user input. The file contains the following sheets:

---

#### Sheet: `Vehicles`

Defines the model time span and vehicle model specifications.

| Parameter | Description |
|---|---|
| `start_year` | First year of the model time span |
| `end_year` | Last year of the model time span |
| `n_vehicles` | Number of vehicle models (e.g., ICEV, BEV) |
| `total_mass` | Total vehicle mass [kg], per vehicle model and year |
| `steel_content` | Share of steel in total vehicle mass [%] |
| `flatsteel_content` | Share of flat steel in total steel mass [%] |
| `longsteel_content` | Share of long steel in total steel mass [%] |
| `aluminum_content` | Share of aluminum in total vehicle mass [%] |
| `wroughtaluminum_content` | Share of wrought aluminum in total aluminum mass [%] |
| `castaluminum_lowCu_content` | Share of low-Cu cast aluminum in total aluminum mass [%] |
| `castaluminum_highCu_content` | Share of high-Cu cast aluminum in total aluminum mass [%] |

---

#### Sheet: `Registrations`

Defines new vehicle registrations and the compound annual growth rate (CAGR) for forecasting future registrations.

| Parameter | Description |
|---|---|
| `cagr` | Compound annual growth rate [%] for forecasting registrations beyond the last defined year |
| `registrations` | Number of new registrations per vehicle model and year (for years with known data) |

The model automatically detects how many years of registration data are provided (`n_init_years`) and forecasts the remainder using the CAGR.

---

#### Sheet: `Steel-Production`

Defines three steel production routes (s1, s2, s3) and their scrap input constraints, quality thresholds, and production efficiencies.

| Parameter | Description |
|---|---|
| `flatsteel_s1/s2/s3` | Share of flat steel production assigned to route s1, s2, s3 [%] |
| `longsteel_s1/s2/s3` | Share of long steel production assigned to route s1, s2, s3 [%] |
| `flatsteel_threshold` | Maximum allowable contamination factor for flat steel per quality threshold [–]; multiple thresholds separated by `;` |
| `longsteel_threshold` | Maximum allowable contamination factor for long steel per quality threshold [–]; multiple thresholds separated by `;` |
| `virgin_steel_quality` | Contamination factor of virgin steel [–]; multiple values separated by `;` |
| `s1/s2/s3_min_scrap` | Minimum scrap share in total input for route s1, s2, s3 [%] |
| `s1/s2/s3_max_scrap` | Maximum scrap share in total input for route s1, s2, s3 [%] |
| `s1/s2/s3_efficiency` | Material production efficiency for route s1, s2, s3 [%] |
| `s1/s2/s3_scrap_recycling_rate` | Recycling rate of internal production scrap for route s1, s2, s3 [%] |

Multiple quality thresholds can be defined by separating values with `;` (e.g., `0.01; 0.02`). All threshold columns (flat steel, long steel, virgin quality) must define the same number of thresholds.

---

#### Sheet: `Aluminum-Production`

Defines production parameters for wrought aluminum, low-Cu cast aluminum, and high-Cu cast aluminum.

| Parameter | Description |
|---|---|
| `wroughtaluminum_min/max_scrap` | Min/max scrap share for wrought aluminum production [%] |
| `wroughtaluminum_efficiency` | Production efficiency for wrought aluminum [%] |
| `wroughtaluminum_scrap_recycling_rate` | Recycling rate of internal wrought aluminum production scrap [%] |
| `wroughtaluminum_threshold` | Quality threshold(s) for wrought aluminum [–] |
| `virgin_wroughtaluminum_quality` | Contamination factor of virgin wrought aluminum [–] |
| `castaluminum_lowCu_*` | Equivalent parameters for low-Cu cast aluminum |
| `castaluminum_highCu_*` | Equivalent parameters for high-Cu cast aluminum |

---

#### Sheet: `Component-Production`

Defines the efficiency and scrap generation of component manufacturing (stamping, casting, etc.).

| Parameter | Description |
|---|---|
| `flatsteel_efficiency` | Component production efficiency for flat steel [%] |
| `flatsteel_scrap_recycling_rate` | Recycling rate of flat steel pre-consumer scrap [%] |
| `longsteel_efficiency` | Component production efficiency for long steel [%] |
| `longsteel_scrap_recycling_rate` | Recycling rate of long steel pre-consumer scrap [%] |
| `wroughtaluminum_efficiency` | Component production efficiency for wrought aluminum [%] |
| `wroughtaluminum_scrap_recycling_rate` | Recycling rate of wrought aluminum pre-consumer scrap [%] |
| `castaluminum_lowCu_efficiency` | Component production efficiency for low-Cu cast aluminum [%] |
| `castaluminum_lowCu_scrap_recycling_rate` | Recycling rate of low-Cu cast aluminum pre-consumer scrap [%] |
| `castaluminum_highCu_efficiency` | Component production efficiency for high-Cu cast aluminum [%] |
| `castaluminum_highCu_scrap_recycling_rate` | Recycling rate of high-Cu cast aluminum pre-consumer scrap [%] |

---

#### Sheet: `EoL`

Defines all end-of-life vehicle parameters: systemic losses, PST recycling, and dismantling.

**Systemic losses:**

| Parameter | Description |
|---|---|
| `exports` | Share of ELVs exported before entering domestic recycling [%] |
| `unknown_whereabouts` | Share of ELVs with unknown fate (neither recycled nor exported) [%] |

**PST (Post-Shredder Technology) recycling:**

PST produces metal outputs from vehicle bodies after shredding. Either a mixed aluminum output or alloy-specific outputs can be defined — not both.

| Parameter | Description |
|---|---|
| `steel_yield` | PST recovery yield for steel [%] |
| `steel_contamination` | Additional contamination factor of PST steel per quality threshold [–] |
| `mixedaluminum_yield` | PST recovery yield for mixed aluminum (use this OR alloy-specific yields) [%] |
| `mixedaluminum_contamination` | Additional contamination of mixed aluminum per quality threshold [–] |
| `wroughtaluminum_yield` | PST recovery yield for wrought aluminum (alloy-specific) [%] |
| `castaluminum_lowCu_yield` | PST recovery yield for low-Cu cast aluminum (alloy-specific) [%] |
| `castaluminum_highCu_yield` | PST recovery yield for high-Cu cast aluminum (alloy-specific) [%] |
| `*_contamination` | Additional contamination factors for respective alloy-specific PST outputs [–] |

**Dismantling (selective disassembly before shredding):**

| Parameter | Description |
|---|---|
| `flatsteel_yield` | Recycling yield of dismantled flat steel [%] |
| `flatsteel_contamination` | Additional contamination factor of dismantled flat steel per threshold [–] |
| `longsteel_yield` | Recycling yield of dismantled long steel [%] |
| `longsteel_contamination` | Additional contamination factor of dismantled long steel per threshold [–] |
| `wroughtaluminum_yield` | Recycling yield of dismantled wrought aluminum [%] |
| `castaluminum_lowCu_yield` | Recycling yield of dismantled low-Cu cast aluminum [%] |
| `castaluminum_highCu_yield` | Recycling yield of dismantled high-Cu cast aluminum [%] |
| `flatsteel_content` | Share of flat steel mass dismantled per vehicle model [%] |
| `longsteel_content` | Share of long steel mass dismantled per vehicle model [%] |
| `wroughtaluminum_content` | Share of wrought aluminum mass dismantled per vehicle model [%] |
| `castaluminum_lowCu_content` | Share of low-Cu cast aluminum mass dismantled per vehicle model [%] |
| `castaluminum_highCu_content` | Share of high-Cu cast aluminum mass dismantled per vehicle model [%] |

---

## 7. Model Calculations

The model performs eight sequential calculation steps, implemented in `calculator.py`:

### Step 1 — Vehicle Contents (`calc_vehicles`)

Converts percentage-based material contents from the input data into absolute masses [kg] for each vehicle model and year:

```
steel_mass       = total_mass × steel_content / 100
flatsteel_mass   = steel_mass × flatsteel_content / 100
aluminum_mass    = total_mass × aluminum_content / 100
...
```

### Step 2 — Vehicle Registrations (`calc_registrations`)

If registration data does not cover the full model time span, future registrations are extrapolated from the last defined year using:

```
registrations(year) = registrations(init_year) × (1 + CAGR/100)^(year − init_year)
```

### Step 3 — Vehicle Fleet (`calc_fleet`)

Builds a detailed fleet matrix `fleet_detail[vehicle, year_reg, year_now]` by computing the annual stock of each vehicle cohort using the Weibull lifetime distribution:

```
vehicles_exiting(year) = registrations × Weibull_PDF(year − year_reg; k, λ)
stock(year_reg, year_now) = registrations − cumulative_exits
```

A no-negative-stock safeguard prevents mathematical artefacts in extreme Weibull tails. Results are aggregated into a cumulative fleet matrix `fleet[vehicle, year]`.

### Step 4 — End-of-Life Vehicles (`calc_eol`)

Calculates vehicles exiting the fleet and their fate:

```
elvs_exit(year)      = stock(year−1) − stock(year)
elvs_export          = elvs_exit × exports / 100
elvs_unknown         = elvs_exit × unknown_whereabouts / 100
elvs_recycling       = elvs_exit − elvs_export − elvs_unknown
```

### Step 5 — Recycling Outputs (`calc_recycling`)

Computes material-specific recycling inputs from ELVs and recycling outputs via two pathways:

**Dismantling recycling:**
```
dismantling_mass = input_mass × dismantling_content / 100
output_dismantling = dismantling_mass × dismantling_yield / 100
bodies_mass      = input_mass × (1 − dismantling_content / 100)
```

**PST recycling:**
```
output_pst = bodies_mass × pst_yield / 100
```

### Step 6 — Material Demand and Supply (`calc_demandSupply`)

**Demand** is calculated bottom-up through the production chain for each year:

```
vehicles_demand  = Σ (registrations × material_mass_per_vehicle)
component_demand = vehicles_demand / component_efficiency
production_demand = component_demand / production_efficiency
max_scrap_input  = production_demand × max_scrap_share
```

**Supply** is computed from three scrap categories:
- *Internal scrap*: generated during material production, calculated from production losses and internal recycling rates
- *Pre-consumer scrap*: stamping/casting scrap from component production
- *Post-consumer scrap*: recyclates from ELV dismantling and PST recycling (steps 5)

### Step 7 — Material Use by Optimization (`calc_use`)

Calls `run_optimization` in `optimizer.py`. The LP allocates available scrap supplies to meet material production demands, minimizing total virgin material use over the entire time horizon, and respecting quality constraints. See [Section 8](#8-optimization-model) for the full formulation.

### Step 8 — Closed-Loop Rates (`calc_closedloop`)

Computes two key performance indicators for each material and year:

```
postconsumer_rate  = postconsumer_use / production_demand × 100  [%]
recycledcontent    = (preconsumer_use + postconsumer_use) / production_demand × 100  [%]
```

Rates are calculated for flat steel, long steel, wrought aluminum, low-Cu cast aluminum, high-Cu cast aluminum, as well as aggregated totals for steel, aluminum, and all materials combined.

---

## 8. Optimization Model

The LP allocation model in `optimizer.py` is the core of CASAsim. It is formulated as a multi-year, multi-material linear program solved with [Gurobi](https://www.gurobi.com/). Solved simultaneously for all years t ∈ T, it determines how available scrap supplies are allocated to steel and aluminum production processes to minimize virgin material input while respecting demand, supply, minimum/maximum scrap share, and material quality constraints.

Steel and aluminum are treated as two fully independent sub-problems (no shared scrap pools) that are solved jointly within a single model for computational convenience.

---

### 8.1 Sets and Indices

| Symbol | Description |
|---|---|
| T | Set of model years |
| P_s | Steel production processes: {`flatsteel_production_s1`, `flatsteel_production_s2`, `flatsteel_production_s3`, `longsteel_production_s1`, `longsteel_production_s2`, `longsteel_production_s3`} |
| P_a | Aluminum production processes: {`wroughtaluminum_production`, `castaluminum_lowCu_production`, `castaluminum_highCu_production`} |
| I_s | Steel quality threshold indices: {1, …, n_s} |
| I_a | Aluminum quality threshold indices: {1, …, n_a} |
| t | Year index (t ∈ T) |
| p | Production process index (p ∈ P_s or p ∈ P_a) |
| i | Quality threshold index |

---

### 8.2 Decision Variables

All variables are non-negative continuous (lb = 0).

#### Steel Variables (defined for all t ∈ T, p ∈ P_s)

| Code name | Description |
|---|---|
| `virgin_steel[t, p]` | Virgin steel fed into process p in year t [t/yr] |
| `internal_flatsteel_s1[t]` … `internal_longsteel_s3[t]` | Internal (production) steel scrap recycled back into the originating route; one variable per route, **not** indexed by p [t/yr] |
| `preconsumer_flatsteel[t, p]` | Flat-steel pre-consumer scrap allocated to process p [t/yr] |
| `preconsumer_longsteel[t, p]` | Long-steel pre-consumer scrap allocated to process p [t/yr] |
| `postconsumer_dismantling_flatsteel[t, p]` | Flat-steel dismantling recyclate allocated to process p [t/yr] |
| `postconsumer_dismantling_longsteel[t, p]` | Long-steel dismantling recyclate allocated to process p [t/yr] |
| `postconsumer_pst_steel[t, p]` | PST steel recyclate allocated to process p [t/yr] |

#### Aluminum Variables (defined for all t ∈ T, p ∈ P_a)

| Code name | Description |
|---|---|
| `virgin_aluminum[t, p]` | Virgin aluminum fed into process p in year t [t/yr] |
| `internal_wroughtaluminum[t]` | Internal wrought-aluminum scrap recycled back into wrought production; not indexed by p [t/yr] |
| `internal_castaluminum_lowCu[t]` | Internal low-Cu cast-aluminum scrap recycled back into low-Cu cast production [t/yr] |
| `internal_castaluminum_highCu[t]` | Internal high-Cu cast-aluminum scrap recycled back into high-Cu cast production [t/yr] |
| `preconsumer_wroughtaluminum[t, p]` | Wrought-aluminum pre-consumer scrap allocated to process p [t/yr] |
| `preconsumer_castaluminum_lowCu[t, p]` | Low-Cu cast-aluminum pre-consumer scrap allocated to process p [t/yr] |
| `preconsumer_castaluminum_highCu[t, p]` | High-Cu cast-aluminum pre-consumer scrap allocated to process p [t/yr] |
| `postconsumer_dismantling_wroughtaluminum[t, p]` | Wrought-aluminum dismantling recyclate allocated to process p [t/yr] |
| `postconsumer_dismantling_castaluminum_lowCu[t, p]` | Low-Cu cast dismantling recyclate allocated to process p [t/yr] |
| `postconsumer_dismantling_castaluminum_highCu[t, p]` | High-Cu cast dismantling recyclate allocated to process p [t/yr] |
| `postconsumer_pst_mixedaluminum[t, p]` | Mixed-aluminum PST recyclate allocated to process p [t/yr] |
| `postconsumer_pst_wroughtaluminum[t, p]` | Alloy-specific wrought-aluminum PST recyclate allocated to process p [t/yr] |
| `postconsumer_pst_castaluminum_lowCu[t, p]` | Alloy-specific low-Cu cast PST recyclate allocated to process p [t/yr] |
| `postconsumer_pst_castaluminum_highCu[t, p]` | Alloy-specific high-Cu cast PST recyclate allocated to process p [t/yr] |

#### Auxiliary Variables (Smoothness Penalty)

| Code name | Description |
|---|---|
| `delta_steel[k, t, p]` | Linearized absolute year-to-year change in steel scrap flow k at process p in year t; k ∈ {0,…,4} indexes the 5 steel scrap flow types [t/yr] |
| `delta_aluminum[k, t, p]` | Linearized absolute year-to-year change in aluminum scrap flow k at process p in year t; k ∈ {0,…,9} indexes the 10 aluminum scrap flow types [t/yr] |

---

### 8.3 Model Parameters

#### Demand Parameters (computed in `calc_demandSupply`, passed as `material_demand`)

| Code name | Description |
|---|---|
| `flatsteel_production_s1` / `_s2` / `_s3` | Required throughput of flat-steel production route s1/s2/s3 [t/yr] |
| `longsteel_production_s1` / `_s2` / `_s3` | Required throughput of long-steel production route s1/s2/s3 [t/yr] |
| `wroughtaluminum_production` | Required throughput of wrought-aluminum production [t/yr] |
| `castaluminum_lowCu_production` | Required throughput of low-Cu cast-aluminum production [t/yr] |
| `castaluminum_highCu_production` | Required throughput of high-Cu cast-aluminum production [t/yr] |
| `{p}_max_scrap` | Maximum allowable total scrap input to process p [t/yr] = demand × max_scrap_share |
| `{p}_min_scrap` | Minimum required total scrap input to process p [t/yr] = demand × min_scrap_share |

#### Supply Parameters (computed in `calc_demandSupply`, passed as `material_supply`)

| Code name | Description |
|---|---|
| `flatsteel_internal_s1/s2/s3` | Available internal flat-steel scrap per production route [t/yr] |
| `longsteel_internal_s1/s2/s3` | Available internal long-steel scrap per production route [t/yr] |
| `flatsteel_preconsumer` | Available flat-steel pre-consumer (stamping) scrap [t/yr] |
| `longsteel_preconsumer` | Available long-steel pre-consumer scrap [t/yr] |
| `flatsteel_postconsumer_dismantling` | Available flat-steel recyclate from ELV dismantling [t/yr] |
| `longsteel_postconsumer_dismantling` | Available long-steel recyclate from ELV dismantling [t/yr] |
| `steel_postconsumer_pst` | Available steel recyclate from PST recycling [t/yr] |
| `wroughtaluminum_internal` | Available internal wrought-aluminum scrap [t/yr] |
| `castaluminum_lowCu_internal` | Available internal low-Cu cast-aluminum scrap [t/yr] |
| `castaluminum_highCu_internal` | Available internal high-Cu cast-aluminum scrap [t/yr] |
| `wroughtaluminum_preconsumer` | Available wrought-aluminum pre-consumer scrap [t/yr] |
| `castaluminum_lowCu_preconsumer` | Available low-Cu cast-aluminum pre-consumer scrap [t/yr] |
| `castaluminum_highCu_preconsumer` | Available high-Cu cast-aluminum pre-consumer scrap [t/yr] |
| `wroughtaluminum_postconsumer_dismantling` | Available wrought-aluminum recyclate from ELV dismantling [t/yr] |
| `castaluminum_lowCu_postconsumer_dismantling` | Available low-Cu cast recyclate from ELV dismantling [t/yr] |
| `castaluminum_highCu_postconsumer_dismantling` | Available high-Cu cast recyclate from ELV dismantling [t/yr] |
| `mixedaluminum_postconsumer_pst` | Available mixed-aluminum recyclate from PST recycling [t/yr] |
| `wroughtaluminum_postconsumer_pst` | Available alloy-specific wrought-aluminum recyclate from PST [t/yr] |
| `castaluminum_lowCu_postconsumer_pst` | Available alloy-specific low-Cu cast recyclate from PST [t/yr] |
| `castaluminum_highCu_postconsumer_pst` | Available alloy-specific high-Cu cast recyclate from PST [t/yr] |

#### Quality Parameters

Quality factors (qf) and contamination offsets (c) are scalar values per quality threshold index i. Lower values denote higher material quality (less contamination).

| Source | Code name | Description |
|---|---|---|
| `steel_production` | `flatsteel_threshold[i]` | Quality threshold for flat steel at threshold i [–] |
| `steel_production` | `longsteel_threshold[i]` | Quality threshold for long steel at threshold i [–] |
| `steel_production` | `virgin_steel_quality[i]` | Quality factor of virgin steel at threshold i [–] |
| `aluminum_production` | `wroughtaluminum_threshold[i]` | Quality threshold for wrought aluminum at threshold i [–] |
| `aluminum_production` | `castaluminum_lowCu_threshold[i]` | Quality threshold for low-Cu cast aluminum at threshold i [–] |
| `aluminum_production` | `castaluminum_highCu_threshold[i]` | Quality threshold for high-Cu cast aluminum at threshold i [–] |
| `aluminum_production` | `virgin_wroughtaluminum_quality[i]` | Quality factor of virgin wrought aluminum [–] |
| `aluminum_production` | `virgin_castaluminum_lowCu_quality[i]` | Quality factor of virgin low-Cu cast aluminum [–] |
| `aluminum_production` | `virgin_castaluminum_highCu_quality[i]` | Quality factor of virgin high-Cu cast aluminum [–] |
| `eol_dismantling_recycling` | `flatsteel_contamination[i]` | Additional contamination introduced by dismantling recycling of flat steel [–] |
| `eol_dismantling_recycling` | `longsteel_contamination[i]` | Additional contamination introduced by dismantling recycling of long steel [–] |
| `eol_dismantling_recycling` | `wroughtaluminum_contamination[i]` | Additional contamination from dismantling recycling of wrought aluminum [–] |
| `eol_dismantling_recycling` | `castaluminum_lowCu_contamination[i]` | Additional contamination from dismantling recycling of low-Cu cast aluminum [–] |
| `eol_dismantling_recycling` | `castaluminum_highCu_contamination[i]` | Additional contamination from dismantling recycling of high-Cu cast aluminum [–] |
| `eol_pst` | `steel_quality[i]` | Quality factor of PST steel recyclate (pre-computed as mass-weighted average of flat/long steel bodies) [–] |
| `eol_pst` | `steel_contamination[i]` | Additional contamination introduced by PST recycling of steel [–] |
| `eol_pst` | `mixedaluminum_quality[i]` | Quality factor of mixed-aluminum PST recyclate (pre-computed as mass-weighted average over all aluminum alloy bodies) [–] |
| `eol_pst` | `mixedaluminum_contamination[i]` | Additional contamination of mixed-aluminum PST recyclate [–] |
| `eol_pst` | `wroughtaluminum_contamination[i]` | Additional contamination of alloy-specific wrought-aluminum PST recyclate [–] |
| `eol_pst` | `castaluminum_lowCu_contamination[i]` | Additional contamination of alloy-specific low-Cu cast PST recyclate [–] |
| `eol_pst` | `castaluminum_highCu_contamination[i]` | Additional contamination of alloy-specific high-Cu cast PST recyclate [–] |

#### Penalty Coefficients

| Code name | Value | Description |
|---|---|---|
| `EPSILON` (ε) | 1×10⁻⁷ | Secondary penalty on post-consumer scrap use; breaks ties by preferring pre-consumer over post-consumer scrap |
| `DELTA_STEEL` (δ_s) | 1×10⁻⁷ | Penalty for year-to-year variation in steel scrap allocation; promotes temporally smooth trajectories |
| `DELTA_ALUMINUM` (δ_a) | 1×10⁻⁵ | Penalty for year-to-year variation in aluminum scrap allocation |

---

### 8.4 Objective Function

The model minimizes total virgin material use across all years and production processes. Two secondary penalty terms resolve degeneracy and promote smooth scrap allocation over time. The penalty terms do not change total virgin material use; they only select among allocations with equal virgin material use.

```
min   Σ_{t∈T} Σ_{p∈P_s}  virgin_steel[t,p]
    + Σ_{t∈T} Σ_{p∈P_a}  virgin_aluminum[t,p]

    + ε · Σ_{t∈T} Σ_{p∈P_s} [ postconsumer_dismantling_flatsteel[t,p]
                               + postconsumer_dismantling_longsteel[t,p]
                               + postconsumer_pst_steel[t,p] ]

    + ε · Σ_{t∈T} Σ_{p∈P_a} [ postconsumer_dismantling_wroughtaluminum[t,p]
                               + postconsumer_dismantling_castaluminum_lowCu[t,p]
                               + postconsumer_dismantling_castaluminum_highCu[t,p]
                               + postconsumer_pst_mixedaluminum[t,p]
                               + postconsumer_pst_wroughtaluminum[t,p]
                               + postconsumer_pst_castaluminum_lowCu[t,p]
                               + postconsumer_pst_castaluminum_highCu[t,p] ]

    + δ_s · Σ_{k} Σ_{t∈T} Σ_{p∈P_s}  delta_steel[k,t,p]

    + δ_a · Σ_{k} Σ_{t∈T} Σ_{p∈P_a}  delta_aluminum[k,t,p]
```

**Interpretation:**
- The primary objective (rows 1–2) minimizes the use of primary (virgin) raw materials.
- The ε-terms (rows 3–8) act as a weak secondary objective: when multiple solutions tie on virgin material use, the solver prefers solutions that minimize post-consumer scrap input, prioritizing pre-consumer scrap in indifferent model states. Pre-consumer scrap does not carry this penalty and is therefore preferred over post-consumer scrap in tie-breaking.
- The δ-terms (rows 9–10) penalize year-to-year oscillations in scrap allocation, promoting physically plausible and temporally smooth production trajectories.

---

### 8.5 Constraints

For compact notation, define the total scrap input to a steel process p as:

```
X_s(t,p) = internal_steel[t,p]
          + preconsumer_flatsteel[t,p]  + preconsumer_longsteel[t,p]
          + postconsumer_dismantling_flatsteel[t,p]  + postconsumer_dismantling_longsteel[t,p]
          + postconsumer_pst_steel[t,p]
```

And the total scrap input to an aluminum process p as:

```
X_a(t,p) = internal_aluminum[t,p]
          + preconsumer_wroughtaluminum[t,p]  + preconsumer_castaluminum_lowCu[t,p]  + preconsumer_castaluminum_highCu[t,p]
          + postconsumer_dismantling_wroughtaluminum[t,p]  + postconsumer_dismantling_castaluminum_lowCu[t,p]  + postconsumer_dismantling_castaluminum_highCu[t,p]
          + postconsumer_pst_mixedaluminum[t,p]  + postconsumer_pst_wroughtaluminum[t,p]
          + postconsumer_pst_castaluminum_lowCu[t,p]  + postconsumer_pst_castaluminum_highCu[t,p]
```

where `internal_steel[t,p]` and `internal_aluminum[t,p]` denote the route-specific internal scrap variables (e.g., `internal_flatsteel_s1[t]` for process `flatsteel_production_s1`).

#### (C1) Demand Constraint

Each production process must exactly meet its calculated material demand in every year. Demand is satisfied by the sum of all scrap inputs and virgin material:

```
∀ t ∈ T, p ∈ P_s:    virgin_steel[t,p]    + X_s(t,p)  =  D(t,p)
∀ t ∈ T, p ∈ P_a:    virgin_aluminum[t,p] + X_a(t,p)  =  D(t,p)
```

where D(t,p) = `material_demand[t, p]` is the production throughput demand for process p in year t.

#### (C2) Maximum Scrap Constraint

The total scrap input per process must not exceed the defined maximum scrap share:

```
∀ t ∈ T, p ∈ P_s:    X_s(t,p)  ≤  D_max(t,p)
∀ t ∈ T, p ∈ P_a:    X_a(t,p)  ≤  D_max(t,p)
```

where D_max(t,p) = `material_demand[t, {p}_max_scrap]` = D(t,p) × max_scrap_share.

#### (C3) Minimum Scrap Constraint

The total scrap input per process must meet a minimum scrap share. To avoid infeasibility during the early model years when scrap supply has not yet built up, the requirement is linearly ramped up over the first 15 model years:

```
∀ t ∈ T, p ∈ P_s:    D_min(t,p) · ramp(t)  ≤  X_s(t,p)
∀ t ∈ T, p ∈ P_a:    D_min(t,p) · ramp(t)  ≤  X_a(t,p)
```

with:

```
ramp(t) = min(1,  (t − t₀) / 15)
```

where t₀ is the first model year, and D_min(t,p) = `material_demand[t, {p}_min_scrap]` = D(t,p) × min_scrap_share.

#### (C4) Supply Constraints

The total allocation from each scrap source across all receiving processes cannot exceed the available supply from that source. Internal scrap variables are route-specific (one bound per route); all other scrap pools are shared across all receiving processes of the same metal (steel or aluminum).

**Steel (∀ t ∈ T):**

```
internal_flatsteel_s1[t]                              ≤  S(t, flatsteel_internal_s1)     [analogously s2, s3]
internal_longsteel_s1[t]                              ≤  S(t, longsteel_internal_s1)     [analogously s2, s3]

Σ_{p∈P_s}  preconsumer_flatsteel[t,p]                ≤  S(t, flatsteel_preconsumer)
Σ_{p∈P_s}  preconsumer_longsteel[t,p]                ≤  S(t, longsteel_preconsumer)

Σ_{p∈P_s}  postconsumer_dismantling_flatsteel[t,p]   ≤  S(t, flatsteel_postconsumer_dismantling)
Σ_{p∈P_s}  postconsumer_dismantling_longsteel[t,p]   ≤  S(t, longsteel_postconsumer_dismantling)

Σ_{p∈P_s}  postconsumer_pst_steel[t,p]               ≤  S(t, steel_postconsumer_pst)
```

**Aluminum (∀ t ∈ T):**

```
internal_wroughtaluminum[t]                                    ≤  S(t, wroughtaluminum_internal)
internal_castaluminum_lowCu[t]                                 ≤  S(t, castaluminum_lowCu_internal)
internal_castaluminum_highCu[t]                                ≤  S(t, castaluminum_highCu_internal)

Σ_{p∈P_a}  preconsumer_wroughtaluminum[t,p]                   ≤  S(t, wroughtaluminum_preconsumer)
Σ_{p∈P_a}  preconsumer_castaluminum_lowCu[t,p]                ≤  S(t, castaluminum_lowCu_preconsumer)
Σ_{p∈P_a}  preconsumer_castaluminum_highCu[t,p]               ≤  S(t, castaluminum_highCu_preconsumer)

Σ_{p∈P_a}  postconsumer_dismantling_wroughtaluminum[t,p]      ≤  S(t, wroughtaluminum_postconsumer_dismantling)
Σ_{p∈P_a}  postconsumer_dismantling_castaluminum_lowCu[t,p]   ≤  S(t, castaluminum_lowCu_postconsumer_dismantling)
Σ_{p∈P_a}  postconsumer_dismantling_castaluminum_highCu[t,p]  ≤  S(t, castaluminum_highCu_postconsumer_dismantling)

Σ_{p∈P_a}  postconsumer_pst_mixedaluminum[t,p]                ≤  S(t, mixedaluminum_postconsumer_pst)
Σ_{p∈P_a}  postconsumer_pst_wroughtaluminum[t,p]              ≤  S(t, wroughtaluminum_postconsumer_pst)
Σ_{p∈P_a}  postconsumer_pst_castaluminum_lowCu[t,p]           ≤  S(t, castaluminum_lowCu_postconsumer_pst)
Σ_{p∈P_a}  postconsumer_pst_castaluminum_highCu[t,p]          ≤  S(t, castaluminum_highCu_postconsumer_pst)
```

where S(t, ·) = `material_supply[t, ·]` is the available scrap supply from the respective source.

#### (C5) Quality Constraint

For each production process, the mass-weighted contamination of all material inputs must not exceed the alloy-specific quality threshold. One inequality is added per quality threshold i, per process p, and per year t.

**Steel (∀ t ∈ T, p ∈ P_s, i ∈ I_s):**

Let qf_p denote the threshold vector for process p (flatsteel_threshold or longsteel_threshold), and let qf_fs, qf_ls be the corresponding quality factors of flat/long steel. Then:

```
  internal_steel[t,p]                       · qf_p[i]
+ preconsumer_flatsteel[t,p]                · qf_fs[i]
+ preconsumer_longsteel[t,p]                · qf_ls[i]
+ postconsumer_dismantling_flatsteel[t,p]   · (qf_fs[i] + c_dis_fs[i])
+ postconsumer_dismantling_longsteel[t,p]   · (qf_ls[i] + c_dis_ls[i])
+ postconsumer_pst_steel[t,p]               · (qf_pst_s[i] + c_pst_s[i])
+ virgin_steel[t,p]                         · qf_virgin_s[i]
  ≤  qf_p[i]  ·  D(t,p)
```

**Aluminum (∀ t ∈ T, p ∈ P_a, i ∈ I_a):**

Let qf_p denote the threshold vector for process p (wroughtaluminum_threshold, castaluminum_lowCu_threshold, or castaluminum_highCu_threshold). Then:

```
  internal_aluminum[t,p]                              · qf_p[i]
+ preconsumer_wroughtaluminum[t,p]                    · qf_wa[i]
+ preconsumer_castaluminum_lowCu[t,p]                 · qf_cl[i]
+ preconsumer_castaluminum_highCu[t,p]                · qf_ch[i]
+ postconsumer_dismantling_wroughtaluminum[t,p]        · (qf_wa[i] + c_dis_wa[i])
+ postconsumer_dismantling_castaluminum_lowCu[t,p]     · (qf_cl[i] + c_dis_cl[i])
+ postconsumer_dismantling_castaluminum_highCu[t,p]    · (qf_ch[i] + c_dis_ch[i])
+ postconsumer_pst_mixedaluminum[t,p]                  · (qf_pst_ma[i] + c_pst_ma[i])
+ postconsumer_pst_wroughtaluminum[t,p]                · (qf_wa[i]  + c_pst_wa[i])
+ postconsumer_pst_castaluminum_lowCu[t,p]             · (qf_cl[i]  + c_pst_cl[i])
+ postconsumer_pst_castaluminum_highCu[t,p]            · (qf_ch[i]  + c_pst_ch[i])
+ virgin_aluminum[t,p]                                 · qf_virgin_p[i]
  ≤  qf_p[i]  ·  D(t,p)
```

**Interpretation:** The left-hand side is the total contamination load contributed by all inputs. The right-hand side is the maximum permissible contamination load, given that the entire throughput D(t,p) would consist of material at exactly the threshold quality. Pre-consumer scrap is assumed to be at the quality threshold of its alloy of origin, without additional contamination. Internal scrap is also assigned the process threshold quality. The contamination terms c_dis_* and c_pst_* represent additional impurities introduced by the respective recycling process.

**Pre-computation:** PST steel quality `qf_pst_s[i]` is computed before optimization as a mass-weighted average of flat-steel and long-steel body qualities. Mixed-aluminum PST quality `qf_pst_ma[i]` is computed as a mass-weighted average over all three aluminum alloy body types.

#### (C6) Internal Scrap Priority Constraint

Internal (production) scrap use is fixed at its maximum possible level, given supply, maximum scrap input and demand:

```
∀ t ∈ T, p ∈ P_s:    internal_steel[t,p]    ≥  min( S_int_s(t,p),  D_max(t,p),  D(t,p) )
∀ t ∈ T, p ∈ P_a:    internal_aluminum[t,p] ≥  min( S_int_a(t,p),  D_max(t,p),  D(t,p) )
```

---

### 8.6 Smoothness Penalty Constraints

The delta variables in the objective are defined via the following linearized absolute-value constraints, applied for each scrap flow variable x, each pair of consecutive years (t−1, t), and each process p:

```
x[t,p] − x[t−1,p]  ≤  delta[k,t,p]
x[t−1,p] − x[t,p]  ≤  delta[k,t,p]
```

These encode `delta[k,t,p] ≥ |x[t,p] − x[t−1,p]|`. The steel penalty covers k ∈ {0,…,4} (pre-consumer flatsteel, pre-consumer longsteel, dismantling flatsteel, dismantling longsteel, PST steel). The aluminum penalty covers k ∈ {0,…,9} (pre-consumer wrought, pre-consumer lowCu cast, pre-consumer highCu cast, dismantling wrought, dismantling lowCu cast, dismantling highCu cast, PST mixed, PST wrought, PST lowCu cast, PST highCu cast).

---

### 8.7 Infeasibility Handling

If the LP is detected as infeasible, the model is re-solved without Gurobi's presolve (`Presolve=0`) and an Irreducible Infeasible Subsystem (IIS) is computed and printed to identify the conflicting constraints.

---

## 9. Sensitivity Analysis

The sensitivity analysis (SA) module in `analyzer.py` performs a one-at-a-time (OAT) parameter variation. All model parameters are varied individually by ±`SENSITIVITY`% from their base-case values.

### Analyzed Parameters

The SA covers 16 parameter groups by default, including:
- Vehicle mass, steel content, aluminum content, and alloy content shares
- Future vehicle registrations (CAGR)
- ELV systemic losses (exports, unknown whereabouts)
- Dismantling contents per alloy type
- Dismantling recycling yields
- Dismantling recycling contamination levels
- PST recycling yields
- PST contamination levels
- Steel production routes
- Steel production configuration (efficiencies, min/max scrap shares)
- Steel quality thresholds
- Virgin steel quality
- Aluminum production configuration (efficiencies, min/max scrap shares)
- Aluminum quality thresholds
- Virgin aluminum quality
- Component production configuration (efficiencies, scrap recycling rates)

### Scenario-Specific SA Configuration

The SA is configured via an `sa_config` matrix defined in `analyzer.py`. Each row corresponds to one SA parameter group; each column corresponds to one scenario. A `True` entry enables variation of that parameter for that scenario; `False` skips it. This allows different scenarios to investigate different parameter subsets.

### SA Outputs

For each parameter and direction (+ / −), the full model is re-run. Results include:
- Per-parameter closed-loop rate and recycled content time series
- Min/max envelopes across all SA iterations
- Infeasible run tracking

Exported data includes Excel files per SA parameter (`tmp/` folder) and summary files with the minimum and maximum recycled content across all parameters for steel and aluminum (`_total_recycledcontent_steel.xlsx`, `_total_recycledcontent_aluminum.xlsx`).

---

## 10. Output and Exported Data

All outputs are stored in `results/<timestamp>/` (single scenario) or `results/<timestamp>/scenario_<ID>/` (multi-scenario).

### Per Scenario

| File/Folder | Content |
|---|---|
| `data_*.xlsx` | Copy of the input file used for this run |
| `tmp_import.xlsx` | All raw imported data for verification |
| `tmp_calc.xlsx` | Intermediate calculation results (vehicles, fleet, ELV, demand/supply, material use, closed-loop rates) |
| `*.pdf` | Result plots: registrations, fleet, ELV flows, material demand/supply, material use, closed-loop rates |
| `sensitivity_analysis/` | SA plots and raw data (only if `PERFORM_SA = True`) |
| `sensitivity_analysis/tmp/` | Per-parameter SA result files (plus/minus direction, all model outputs) |
| `sensitivity_analysis/_infeasible_sa_runs.xlsx` | List of SA parameter variations that led to infeasible LP models |
| `sensitivity_analysis/_total_recycledcontent_steel.xlsx` | Min/max recycled content across all SA runs for steel |
| `sensitivity_analysis/_total_recycledcontent_aluminum.xlsx` | Min/max recycled content across all SA runs for aluminum |

### Key Output Variables

| Variable | Description |
|---|---|
| `fleet[vehicle, year]` | Annual vehicle stock, exits, exports, unknowns, and recycling inputs |
| `eol[year]` | Aggregated ELV material inputs, dismantling outputs, and PST recycling outputs |
| `material_demand[year]` | Production-level material demand per alloy and production route |
| `material_supply[year]` | Available internal, pre-consumer, and post-consumer scrap per alloy |
| `material_use[year]` | LP-optimized scrap and virgin material allocation per process |
| `closedloop[year]` | Post-consumer recycled content rate [%] and total recycled content rate [%] per alloy |

---

## 11. Multi-Scenario Analysis

When multiple input files are detected in `data/`, the model runs all scenarios sequentially and generates additional cross-scenario comparison plots in `results/<timestamp>/`.

The multi-scenario plot module (`plotter_multi.py`) creates subplots arranged in a square grid layout that scales automatically to the number of scenarios. Up to 8 scenarios are supported by the built-in color palette.

---

## 12. License

Copyright 2026 Dominik Reichert  
Technical University of Munich  
Contact: dominik.reichert@tum.de

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
