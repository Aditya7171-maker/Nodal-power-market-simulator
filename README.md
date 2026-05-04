# Nodal-power-market-simulator
A PyPSA-based nodal electricity market simulator modeling dispatch, congestion, and price formation with renewable integration (Delhi–Mumbai case study).
# ⚡ Delhi–Mumbai Electricity Market Model

> **A two-bus power system optimisation study simulating economic dispatch, transmission congestion, and locational marginal pricing across India's two largest metropolitan grids — built entirely in Python using PyPSA.**


---

## 📌 What This Project Does

This project models **how electricity is generated, priced, and traded** between Delhi and Mumbai for a full 24-hour period (15 January 2024). It answers the question every grid operator faces every day:

> *Which power plants should run, at what output, and at what price — to serve everyone's electricity needs at the lowest possible cost?*

Using **linear programming optimisation**, the model dispatches 9 real Indian power plants across 24 hourly time steps, subject to a 2,000 MW transmission constraint between the two cities.

---

## 🧠 Core Concepts Demonstrated

| Concept | What the Model Shows |
|---|---|
| **Merit Order Dispatch** | Zero-cost renewables → nuclear → coal → gas (never needed) |
| **Locational Marginal Pricing (LMP)** | Delhi = ₹2,200/MWh · Mumbai = ₹2,333/MWh (avg) |
| **Transmission Congestion** | Delhi–Mumbai line hits 2,000 MW from 08:00 → price splits |
| **Renewable Integration** | Solar/wind profiles dispatch whenever available |
| **Shadow Prices** | LP dual variables yield electricity prices automatically |
| **Economic Dispatch** | HiGHS solver minimises ₹485 million/day system cost |

---

## 📊 Key Results — 15 January 2024

```
┌─────────────────────────────────────────────────────────────┐
│              SIMULATION RESULTS SUMMARY                      │
├────────────────────────────┬────────────────────────────────┤
│  Total Energy Served       │  279.4 GWh                     │
│  Peak Demand               │  14,500 MW (at 18:00)          │
│  Average Demand            │  11,642 MW                     │
│  System Operating Cost     │  ₹48.54 Crore / day            │
│  Delhi Avg Price (LMP)     │  ₹2,200 / MWh (flat)           │
│  Mumbai Avg Price (LMP)    │  ₹2,333 / MWh                  │
│  Congestion Premium        │  ₹133 / MWh (Mumbai pays more) │
│  Delhi → Mumbai Export     │  24 / 24 hours                 │
│  Line Congestion Hours     │  16 / 24 hours (from 08:00)    │
│  Gas Plants Dispatched     │  0 hours (too expensive)       │
└────────────────────────────┴────────────────────────────────┘
```

---

## 🏭 Power Plants Modelled

### Delhi Grid
| Plant | Capacity | Cost (₹/MWh) | Fuel | Dispatched |
|---|---|---|---|---|
| Dadri NTPC | 22,637 MW | ₹2,200 | Coal | ✅ 24h — primary balancer |
| Pragati Power | 1,500 MW | ₹6,500 | Gas | ❌ Too expensive |
| Rewa Solar PPA | 1,200 MW | ₹0 | Solar | ✅ Daytime only |
| Bhakra Hydro | 800 MW | ₹500 | Hydro | ✅ Flat 800 MW all day |

### Mumbai Grid
| Plant | Capacity | Cost (₹/MWh) | Fuel | Dispatched |
|---|---|---|---|---|
| Tarapur Nuclear | 1,400 MW | ₹800 | Nuclear | ✅ Full output, 24h |
| Trombay TPS | 22,800 MW | ₹2,400 | Coal | ✅ From 08:00 (congestion) |
| ReNew Solar | 600 MW | ₹0 | Solar | ✅ Daytime only |
| Uran Gas NTPC | 900 MW | ₹6,800 | Gas | ❌ Too expensive |
| Maharashtra Wind | 450 MW | ₹0 | Wind | ✅ 60–90% capacity all day |

---

## 📈 Dashboard Preview

The model generates a fully interactive **4-panel HTML dashboard**:

```
┌──────────────────────┬──────────────────────┐
│  Generator Dispatch  │  Cost Stack —        │
│  by City (MW)        │  Who's Cheapest?     │
│  [Stacked Bar]       │  [Bar Chart]         │
├──────────────────────┼──────────────────────┤
│  Merit Order Curve   │  Merit Order Curve   │
│  Delhi               │  Mumbai              │
│  [Step Function]     │  [Step Function]     │
└──────────────────────┴──────────────────────┘
```

**Chart 1 — Generator Dispatch:** Stacked bars showing avg MW output per plant per city. Delhi's bar is coal-dominated; Mumbai shows a more diverse nuclear/coal/renewables mix.

**Chart 2 — Cost Stack:** All 9 plants ordered cheapest to most expensive. The visual height gap between coal (₹2,200) and gas (₹6,500) explains why gas ran zero hours.

**Chart 3 & 4 — Merit Order Curves:** Step-function supply curves for each city. The intersection of the demand line (red) with the curve sets the market price (green) — exactly how IEX India works.

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install pypsa pandas plotly highspy numpy
```

### Run the Model
```bash
python p3_electricity_market.py
```

The script will:
1. Build the two-bus PyPSA network
2. Optimise dispatch using HiGHS LP solver
3. Print all results to terminal
4. Open the interactive dashboard in your browser (`delhi_mumbai_market.html`)

---

## 📁 Project Structure

```
GridIQ/
└── energy_modeling/
    └── projects_3-8/
        ├── p3_electricity_market.py      # Main model script
        └── delhi_mumbai_market.html      # Interactive dashboard (auto-generated)
```

---

## 🏗️ How the Model Works — Step by Step

```
Step 1: Create PyPSA Network (24-hour time horizon)
         │
Step 2: Add Buses (Delhi + Mumbai as grid nodes at 400 kV)
         │
Step 3: Add Loads (time-varying hourly demand profiles)
         │
Step 4: Add Generators (9 plants with capacity, cost, fuel type)
         │         + solar/wind availability profiles
Step 5: Add Transmission Line (Delhi–Mumbai, 2,000 MW limit)
         │
Step 6: n.optimize() → HiGHS LP Solver
         │   Minimise: Σ (output × marginal_cost) for all plants, all hours
         │   Subject to: Power balance | Generator limits | Line limits
         │
Step 7: Read Results
         │   n.generators_t.p     → dispatch (MW per plant per hour)
         │   n.lines_t.p0         → transmission flow (MW per hour)
         │   n.buses_t.marginal_price → LMP prices (₹/MWh per city)
         │
Step 8: Build Plotly Dashboard → delhi_mumbai_market.html
```

---

## 💡 Why This Matters

This model replicates the exact economic logic used in:

- **IEX India** (Indian Energy Exchange) — Day-Ahead Market clearing
- **POSOCO** (Power System Operation Corporation) — national grid scheduling
- **PJM** (USA) and **EPEX** (Europe) — real-time electricity markets

The same merit order, LMP pricing, and congestion analysis are used by real grid operators to schedule ₹thousands of crores of electricity every day.

---

## 🔮 Future Extensions

- [ ] Add more cities (Bangalore, Chennai, Kolkata) → multi-bus national grid
- [ ] Model a full year (8,760 hours) for seasonal analysis
- [ ] Add battery storage and study price smoothing effects
- [ ] Implement unit commitment (MILP) for realistic coal start/stop
- [ ] Connect real IEX market data for model validation
- [ ] Add CO₂ emissions tracking per generator

---



## 🛠️ Tech Stack

```
PyPSA        → Power system network modelling + optimisation
Pandas       → Time series data management (24-hour snapshots)
Plotly       → Interactive HTML dashboard (4-panel)
HiGHS        → Open-source LP solver (University of Edinburgh)
linopy       → LP model builder (used internally by PyPSA)
NumPy        → Numerical arrays for renewable profiles
```


## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

<div align="center">
<sub>Built with PyPSA · Inspired by real Indian electricity market design ·</sub>
</div>
