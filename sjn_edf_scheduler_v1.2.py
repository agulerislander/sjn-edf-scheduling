import heapq
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

@dataclass
class Task:
    task_id: str
    arrival_time: float
    true_burst: float
    relative_deadline: float
    period: float
    
    # Dynamic runtime state
    estimated_burst: float = field(init=False)
    absolute_deadline: float = field(init=False)
    
    def __post_init__(self):
        self.estimated_burst = self.true_burst
        self.absolute_deadline = self.arrival_time + self.relative_deadline

    def copy(self):
        """Creates a clean duplicate for parallel scheduler runs."""
        return Task(
            task_id=self.task_id,
            arrival_time=self.arrival_time,
            true_burst=self.true_burst,
            relative_deadline=self.relative_deadline,
            period=self.period
        )

class SimulatorEngine:
    def __init__(self, mode: str, avg_E: float = 10.0, avg_D: float = 40.0):
        """
        mode options:
        - 'PURE_EDF' : Priority based strictly on absolute deadline proximity.
        - 'PURE_SJN' : Priority based strictly on shortest estimated execution burst.
        - 'HYBRID'   : Priority based on dynamic alpha-weighted formula.
        """
        self.mode = mode
        self.avg_E = avg_E
        self.avg_D = avg_D
        self.ready_queue: List[Tuple[float, float, Task]] = []
        self.missed_deadlines = 0
        self.total_completed = 0
        self.total_waiting_time = 0.0

    def compute_priority(self, task: Task, current_time: float) -> float:
        laxity = max(0.001, task.absolute_deadline - current_time)
        
        if self.mode == 'PURE_EDF':
            # Smaller deadline value = Higher urgency
            return 1.0 / laxity
            
        elif self.mode == 'PURE_SJN':
            # Smaller estimated burst = Higher priority
            return 1.0 / max(0.001, task.estimated_burst)
            
        elif self.mode == 'HYBRID':
            # Calculate core utilization U(t)
            u_sum = sum(t.true_burst / max(0.001, t.absolute_deadline - current_time) for _, _, t in self.ready_queue)
            u_sum = min(1.5, u_sum)
            
            # Determine alpha load regime
            if u_sum < 0.70:
                alpha = 0.70
            elif u_sum < 0.85:
                alpha = 0.50
            else:
                alpha = 0.00
                
            # Safety threshold override
            if laxity < 2.0:
                alpha = 0.0
                
            sjn_term = self.avg_E / max(0.001, task.estimated_burst)
            edf_term = self.avg_D / laxity
            return (alpha * sjn_term) + ((1.0 - alpha) * edf_term)

    def run(self, task_list: List[Task]) -> Dict[str, float]:
        current_time = 0.0
        arrival_list = sorted([t.copy() for t in task_list], key=lambda x: x.arrival_time)
        
        while arrival_list or self.ready_queue:
            # 1. Admit arrived tasks
            while arrival_list and arrival_list[0].arrival_time <= current_time:
                arrived = arrival_list.pop(0)
                prio = -self.compute_priority(arrived, current_time)
                heapq.heappush(self.ready_queue, (prio, arrived.arrival_time, arrived))

            if not self.ready_queue and arrival_list:
                current_time = arrival_list[0].arrival_time
                continue

            # 2. Rebalance queue at event tick
            rebalanced = []
            while self.ready_queue:
                _, arr, task = heapq.heappop(self.ready_queue)
                prio = -self.compute_priority(task, current_time)
                rebalanced.append((prio, arr, task))
            heapq.heapify(rebalanced)
            self.ready_queue = rebalanced

            # 3. Dispatch highest priority task
            _, arrival, current_task = heapq.heappop(self.ready_queue)
            
            # Record metrics
            waiting_time = current_time - arrival
            self.total_waiting_time += max(0.0, waiting_time)
            
            current_time += current_task.true_burst
            self.total_completed += 1
            
            if current_time > current_task.absolute_deadline:
                self.missed_deadlines += 1

        dmr = (self.missed_deadlines / self.total_completed * 100) if self.total_completed else 0.0
        awt = (self.total_waiting_time / self.total_completed) if self.total_completed else 0.0
        
        return {"DMR": dmr, "AWT": awt}

