# sjn-edf-scheduling
Dynamic Hybrid SJN EDF Scheduling Algorithm for Real Time Systems

COSC 6352: Advanced Operating Systems, Texas A&M University-Corpus Christi
Instructor: Ismail Alihan Hadimlioglu

📌 Overview
This project presents a discrete-event CPU scheduling framework designed to bridge the gap between predictable real-time deadline guarantees and high-throughput execution tracking. Standard Shortest Job Next (SJN) scheduling minimizes average waiting time but lacks deadline awareness, leading to high miss rates and task starvation under heavy core loads. Conversely, dynamic algorithms like Earliest Deadline First (EDF) prioritize deadline proximity but suffer from a catastrophic "domino effect" during transient overloads.

We propose a Dynamic Hybrid SJN-EDF Algorithm that dynamically balances task urgency (remaining laxity) and execution duration (CPU burst estimates) using continuous CPU load-scaling factors.

👥 Authors
Alihan Guler — Department of Computer Science, Texas A&M University-Corpus Christi
Siddhartha Rao Sandineni — Department of Computer Science, Texas A&M University-Corpus Christi
Zhiwen Zhong — Department of Computer Science, Texas A&M University-Corpus Christi

🎯 Key Objectives
1- Algorithm Design: Develop a convex priority model balancing task duration and remaining deadline laxity.
2- C++ Simulator (or Python): Build a modular discrete-event CPU scheduler simulator in C++ capable of modeling synthetic task sets with configurable execution jitter, periodicity, and arrival distributions.
3- Deadline Miss Reduction: Achieve a ≥15% reduction in hard deadline miss rates compared to standard EDF under high CPU utilization (U>85%).
4- Overhead Control: Preserve system throughput by keeping context switch frequency within 10% of Rate Monotonic (RM) scheduling.
5- Empirical Benchmarking: Evaluate performance across 5 distinct workload benchmarks.
