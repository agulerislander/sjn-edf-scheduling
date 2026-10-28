import random
from dataclasses import dataclass, field
from typing import List

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
            period=self.period,
        )


def generate_uunifast_workload(
    num_tasks: int, total_utilization: float
) -> List[Task]:
    """Generates synthetic task sets using the UUnifast algorithm with execution jitter."""
    utilizations = []
    sum_u = total_utilization

    for i in range(1, num_tasks):
        next_sum_u = sum_u * (random.random() ** (1.0 / (num_tasks - i)))
        utilizations.append(sum_u - next_sum_u)
        sum_u = next_sum_u
    utilizations.append(sum_u)

    tasks = []
    for idx, u_i in enumerate(utilizations):
        period = random.choice([10.0, 20.0, 50.0, 100.0])
        jitter = random.uniform(0.90, 1.10)  # +/- 10% execution jitter
        true_burst = max(0.5, (u_i * period) * jitter)
        relative_deadline = period * random.uniform(0.85, 1.0)
        arrival_time = random.uniform(0.0, 20.0)

        tasks.append(
            Task(
                task_id=f"T_{idx+1}",
                arrival_time=arrival_time,
                true_burst=true_burst,
                relative_deadline=relative_deadline,
                period=period,
            )
        )
    return tasks