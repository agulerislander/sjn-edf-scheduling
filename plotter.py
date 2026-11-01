import random
import matplotlib.pyplot as plt
from scheduler_engine import SimulatorEngine
from task_model import generate_uunifast_workload


def run_benchmark_and_plot():
    utilization_levels = [0.60, 0.75, 0.85, 0.95, 1.10, 1.25]
    NUM_RUNS = 100

    edf_dmrs, hyb_dmrs, sjn_dmrs = [], [], []
    edf_awts, hyb_awts, sjn_awts = [], [], []

    for U in utilization_levels:
        sjn_d, edf_d, hyb_d = [], [], []
        sjn_a, edf_a, hyb_a = [], [], []

        for seed in range(NUM_RUNS):
            random.seed(seed)
            tasks = generate_uunifast_workload(
                num_tasks=20, total_utilization=U
            )

            res_sjn = SimulatorEngine(mode="PURE_SJN").run(tasks)
            res_edf = SimulatorEngine(mode="PURE_EDF").run(tasks)
            res_hyb = SimulatorEngine(mode="HYBRID").run(tasks)

            sjn_d.append(res_sjn["DMR"])
            edf_d.append(res_edf["DMR"])
            hyb_d.append(res_hyb["DMR"])

            sjn_a.append(res_sjn["AWT"])
            edf_a.append(res_edf["AWT"])
            hyb_a.append(res_hyb["AWT"])

        sjn_dmrs.append(sum(sjn_d) / NUM_RUNS)
        edf_dmrs.append(sum(edf_d) / NUM_RUNS)
        hyb_dmrs.append(sum(hyb_d) / NUM_RUNS)

        sjn_awts.append(sum(sjn_a) / NUM_RUNS)
        edf_awts.append(sum(edf_a) / NUM_RUNS)
        hyb_awts.append(sum(hyb_a) / NUM_RUNS)

    labels = [f"{int(u*100)}%" for u in utilization_levels]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Deadline Miss Ratio
    ax1.plot(labels, sjn_dmrs, "r--o", label="Pure SJN")
    ax1.plot(labels, edf_dmrs, "b-s", label="Pure EDF")
    ax1.plot(labels, hyb_dmrs, "g-^", label="Hybrid SJN-EDF")
    ax1.set_title("Deadline Miss Ratio (DMR) vs. CPU Load")
    ax1.set_xlabel("CPU Utilization Load")
    ax1.set_ylabel("DMR (%)")
    ax1.grid(True)
    ax1.legend()

    # Plot 2: Average Waiting Time
    ax2.plot(labels, sjn_awts, "r--o", label="Pure SJN")
    ax2.plot(labels, edf_awts, "b-s", label="Pure EDF")
    ax2.plot(labels, hyb_awts, "g-^", label="Hybrid SJN-EDF")
    ax2.set_title("Average Waiting Time (AWT) vs. CPU Load")
    ax2.set_xlabel("CPU Utilization Load")
    ax2.set_ylabel("AWT (ms)")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("benchmark_results.png")
    print("Benchmark plots saved to benchmark_results.png")


if __name__ == "__main__":
    run_benchmark_and_plot()