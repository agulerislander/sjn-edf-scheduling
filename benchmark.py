import time
import random
from task_model import generate_uunifast_workload
from scheduler_engine import SimulatorEngine

if __name__ == "__main__":
    # Generate a unique seed using system timestamp
    base_seed = int(time.time())
    random.seed(base_seed)
    
    utilization_levels = [0.60, 0.75, 0.85, 0.95, 1.10, 1.25]
    NUM_RUNS = 100
    
    print("=" * 80)
    print(f"      MULTI-SEED MONTE CARLO BENCHMARK (Base Seed: {base_seed})")
    print("=" * 80)
    print(f"{'CPU Load':<10} | {'Metric':<6} | {'Pure SJN':<12} | {'Pure EDF':<12} | {'Hybrid SJN-EDF':<15}")
    print("-" * 80)

    for U in utilization_levels:
        sjn_dmr_list, edf_dmr_list, hyb_dmr_list = [], [], []
        sjn_awt_list, edf_awt_list, hyb_awt_list = [], [], []

        for _ in range(NUM_RUNS):
            tasks = generate_uunifast_workload(num_tasks=20, total_utilization=U)
            
            res_sjn = SimulatorEngine(mode='PURE_SJN').run(tasks)
            res_edf = SimulatorEngine(mode='PURE_EDF').run(tasks)
            res_hyb = SimulatorEngine(mode='HYBRID').run(tasks)
            
            sjn_dmr_list.append(res_sjn['DMR'])
            edf_dmr_list.append(res_edf['DMR'])
            hyb_dmr_list.append(res_hyb['DMR'])
            
            sjn_awt_list.append(res_sjn['AWT'])
            edf_awt_list.append(res_edf['AWT'])
            hyb_awt_list.append(res_hyb['AWT'])

        avg_sjn_dmr = sum(sjn_dmr_list) / NUM_RUNS
        avg_edf_dmr = sum(edf_dmr_list) / NUM_RUNS
        avg_hyb_dmr = sum(hyb_dmr_list) / NUM_RUNS

        avg_sjn_awt = sum(sjn_awt_list) / NUM_RUNS
        avg_edf_awt = sum(edf_awt_list) / NUM_RUNS
        avg_hyb_awt = sum(hyb_awt_list) / NUM_RUNS

        load_label = f"{int(U*100)}%"
        print(f"{load_label:<10} | DMR %  | {avg_sjn_dmr:<12.2f} | {avg_edf_dmr:<12.2f} | {avg_hyb_dmr:<15.2f}")
        print(f"{'':<10} | AWT ms | {avg_sjn_awt:<12.2f} | {avg_edf_awt:<12.2f} | {avg_hyb_awt:<15.2f}")
        print("-" * 80)