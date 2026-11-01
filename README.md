# Adapting Shortest Job Next (SJN) Scheduling for Real-Time Environments
> **A Dynamic Hybrid SJN-EDF Approach to Minimize Deadline Misses**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://www.python.org/)
[![Course: COSC 6352](https://img.shields.io/badge/TAMUCC-COSC%206352-maroon.svg)](https://www.tamucc.edu/)

---

## 📌 Overview

This repository contains the simulation framework and empirical evaluation harness for a novel **Dynamic SJN-EDF Hybrid Scheduler**. Developed for **COSC 6352: Advanced Operating Systems** at Texas A&M University–Corpus Christi, this project resolves the trade-off between the throughput efficiency of Shortest Job Next (SJN) and the temporal determinism of Earliest Deadline First (EDF) in Real-Time Operating Systems (RTOS).

### Key Features
- **Multi-Objective Priority Formulation ($P_i(t)$):** Dynamically balances task execution length against deadline proximity.
- **Adaptive Core-Load Scaling ($\alpha(t)$):** Shifts scheduling priorities across three core utilization regimes ($U < 70\%$, $70\% \le U < 85\%$, $U \ge 85\%$).
- **EWMA Execution Burst Estimation:** Employs Exponential Weighted Moving Average ($\beta = 0.3$) tracking to dynamically estimate future task execution durations under processing jitter.
- **Absolute Safety Override:** Reverts task priority to pure EDF if remaining laxity falls below a critical safety threshold ($\Delta t_{\text{safety}}$).
- **$O(\log N)$ Event-Driven Min-Heap:** Utilizes discrete-event priority evaluation to eliminate continuous priority-recalculation overhead.

---

## 📐 Mathematical Formulation

At any scheduling instant $t$, process priority $P_i(t)$ for task $T_i$ is evaluated via a dimensionless convex formulation:

$$P_i(t) = \alpha(t) \cdot \left( \frac{\bar{E}}{E_i} \right) + (1 - \alpha(t)) \cdot \left( \frac{\bar{D}}{D_i - t} \right)$$

Where:
- $E_i$: Predicted remaining execution burst time (SJN term).
- $D_i - t$: Remaining deadline laxity (EDF term).
- $\bar{E}, \bar{D}$: System baseline normalization factors.
- $\alpha(t) \in [0, 1]$: Dynamic load-scaling parameter based on core utilization $U(t)$.

---

## 📁 Repository Structure

```text
sjn-edf-scheduling/
│
├── task_model.py         # Task data structures & UUnifast workload generator
├── scheduler_engine.py   # Discrete-event engine (Pure SJN, Pure EDF, Hybrid)
├── benchmark.py          # Multi-seed Monte Carlo simulation harness (100 iterations)
├── plotter.py            # Performance plotting script (matplotlib)
├── tests/                # Unit test suite
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
└── LICENSE               # MIT License
🚀 Quick Start & Installation
Prerequisites
Python 3.11 or higher
Git
Installation & Execution
Clone the repository:
Bash
git clone [https://github.com/agulerislander/sjn-edf-scheduling.git](https://github.com/agulerislander/sjn-edf-scheduling.git)
cd sjn-edf-scheduling
Install dependencies:
Bash
pip install -r requirements.txt
Run the Monte Carlo benchmark suite:
Bash
python benchmark.py
Generate visualization charts:
Bash
python plotter.py

👥 Authors & Academic Attribution
Alihan Güler – Department of Computer Science, Texas A&M University–Corpus Christi
Siddhartha Rao Sandineni – Department of Computer Science, Texas A&M University–Corpus Christi
Zhiwen Zhong – Department of Computer Science, Texas A&M University–Corpus Christi
Course: COSC 6352: Advanced Operating Systems
Instructor: Ismail Alihan Hadimlioglu
Institution: Texas A&M University–Corpus Christi