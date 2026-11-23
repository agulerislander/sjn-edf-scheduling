# # v1
# import heapq
# from typing import List, Tuple, Dict
# from task_model import Task


# class SimulatorEngine:
#     def __init__(self, mode: str, avg_E: float = 10.0, avg_D: float = 40.0):
#         """
#         mode options:
#         - 'PURE_EDF' : Priority based strictly on absolute deadline proximity.
#         - 'PURE_SJN' : Priority based strictly on shortest estimated execution burst.
#         - 'HYBRID'   : Priority based on dynamic alpha-weighted formula.
#         """
#         self.mode = mode
#         self.avg_E = avg_E
#         self.avg_D = avg_D
#         self.ready_queue: List[Tuple[float, float, Task]] = []
#         self.missed_deadlines = 0
#         self.total_completed = 0
#         self.total_waiting_time = 0.0

#     def compute_priority(self, task: Task, current_time: float) -> float:
#         laxity = max(0.001, task.absolute_deadline - current_time)

#         if self.mode == "PURE_EDF":
#             # Smaller deadline value = Higher urgency
#             return 1.0 / laxity

#         elif self.mode == "PURE_SJN":
#             # Smaller estimated burst = Higher priority
#             return 1.0 / max(0.001, task.estimated_burst)

#         elif self.mode == "HYBRID":
#             # Calculate core utilization U(t)
#             u_sum = sum(
#                 t.true_burst / max(0.001, t.absolute_deadline - current_time)
#                 for _, _, t in self.ready_queue
#             )
#             u_sum = min(1.5, u_sum)

#             # Determine alpha load regime
#             if u_sum < 0.70:
#                 alpha = 0.70
#             elif u_sum < 0.85:
#                 alpha = 0.50
#             else:
#                 alpha = 0.00

#             # Absolute Safety threshold override
#             if laxity < 2.0:
#                 alpha = 0.0

#             sjn_term = self.avg_E / max(0.001, task.estimated_burst)
#             edf_term = self.avg_D / laxity
#             return (alpha * sjn_term) + ((1.0 - alpha) * edf_term)

#         return 0.0

#     def run(self, task_list: List[Task]) -> Dict[str, float]:
#         current_time = 0.0
#         arrival_list = sorted(
#             [t.copy() for t in task_list], key=lambda x: x.arrival_time
#         )

#         while arrival_list or self.ready_queue:
#             # 1. Admit arrived tasks
#             while arrival_list and arrival_list[0].arrival_time <= current_time:
#                 arrived = arrival_list.pop(0)
#                 prio = -self.compute_priority(arrived, current_time)
#                 heapq.heappush(
#                     self.ready_queue, (prio, arrived.arrival_time, arrived)
#                 )

#             if not self.ready_queue and arrival_list:
#                 current_time = arrival_list[0].arrival_time
#                 continue

#             # 2. Rebalance queue at discrete event tick
#             rebalanced = []
#             while self.ready_queue:
#                 _, arr, task = heapq.heappop(self.ready_queue)
#                 prio = -self.compute_priority(task, current_time)
#                 rebalanced.append((prio, arr, task))
#             heapq.heapify(rebalanced)
#             self.ready_queue = rebalanced

#             # 3. Dispatch highest priority task
#             _, arrival, current_task = heapq.heappop(self.ready_queue)

#             # Record metrics
#             waiting_time = current_time - arrival
#             self.total_waiting_time += max(0.0, waiting_time)

#             current_time += current_task.true_burst
#             self.total_completed += 1

#             if current_time > current_task.absolute_deadline:
#                 self.missed_deadlines += 1

#         dmr = (
#             (self.missed_deadlines / self.total_completed * 100)
#             if self.total_completed
#             else 0.0
#         )
#         awt = (
#             (self.total_waiting_time / self.total_completed)
#             if self.total_completed
#             else 0.0
#         )

#         return {"DMR": dmr, "AWT": awt}




# # v2
# import heapq
# from typing import List, Tuple, Dict
# from task_model import Task


# class SimulatorEngine:
#     EPS = 1e-9  # Floating-point tolerance for event timestamps

#     def __init__(self, mode: str, avg_E: float = 10.0, avg_D: float = 40.0):
#         """
#         mode options:
#         - 'PURE_EDF' : Preemptive EDF based on absolute deadline proximity.
#         - 'PURE_SJN' : Preemptive SJN (SRTF) based on remaining estimated burst.
#         - 'HYBRID'   : Preemptive dynamic alpha-weighted SJN-EDF formula.
#         """
#         self.mode = mode
#         self.avg_E = avg_E
#         self.avg_D = avg_D
#         self.ready_queue: List[Tuple[float, float, int, Task]] = []
#         self.missed_deadlines = 0
#         self.total_completed = 0
#         self.total_waiting_time = 0.0

#     def _safety_margin(self, task: Task) -> float:
#         # Reserve at least 2.0 ms or 25% of estimated burst to absorb estimation error
#         return max(2.0, 0.25 * task.estimated_burst)

#     def _compute_queue_alpha(self, current_time: float) -> float:
#         if self.mode == "PURE_EDF":
#             return 0.0
#         if self.mode == "PURE_SJN":
#             return 1.0
#         if not self.ready_queue:
#             return 0.80

#         u_sum = 0.0
#         min_excess_slack = float("inf")

#         for _, _, _, t in self.ready_queue:
#             time_left = max(0.001, t.absolute_deadline - current_time)
#             slack = (t.absolute_deadline - current_time) - t.rem_est
#             excess_slack = slack - self._safety_margin(t)

#             u_sum += t.rem_true / time_left
#             min_excess_slack = min(min_excess_slack, excess_slack)

#         # Queue-wide safety override: if ANY task enters its danger zone,
#         # switch the entire queue to alpha = 0.0 (exact Pure EDF ordering)
#         if min_excess_slack <= self.EPS or u_sum >= 0.90:
#             return 0.0

#         # Smoothly blend from SJN-dominant (0.80) toward EDF (0.0) as load or slack tightens
#         load_factor = max(0.0, 1.0 - (u_sum / 0.90))
#         slack_factor = min(1.0, min_excess_slack / max(0.001, self.avg_E))
#         return 0.80 * load_factor * slack_factor

#     def compute_priority(
#         self, task: Task, current_time: float, alpha: float = 0.5
#     ) -> float:
#         time_left = max(0.001, task.absolute_deadline - current_time)
#         rem_est = max(0.001, getattr(task, "rem_est", task.estimated_burst))

#         if self.mode == "PURE_EDF":
#             return 1.0 / time_left

#         elif self.mode == "PURE_SJN":
#             return 1.0 / rem_est

#         elif self.mode == "HYBRID":
#             # When alpha == 0.0, this reduces to an exact scalar multiple of PURE_EDF
#             sjn_term = self.avg_E / rem_est
#             edf_term = self.avg_D / time_left
#             return (alpha * sjn_term) + ((1.0 - alpha) * edf_term)

#         return 0.0

#     def run(self, task_list: List[Task]) -> Dict[str, float]:
#         self.ready_queue = []
#         self.missed_deadlines = 0
#         self.total_completed = 0
#         self.total_waiting_time = 0.0

#         current_time = 0.0
#         seq_counter = 0

#         arrival_list: List[Task] = []
#         for t in sorted(task_list, key=lambda x: x.arrival_time):
#             task_copy = t.copy()
#             task_copy.rem_true = float(task_copy.true_burst)
#             task_copy.rem_est = float(task_copy.estimated_burst)
#             task_copy.last_ready = float(task_copy.arrival_time)
#             arrival_list.append(task_copy)

#         while arrival_list or self.ready_queue:
#             # 1. Admit all tasks that have arrived by current_time
#             while (
#                 arrival_list
#                 and arrival_list[0].arrival_time <= current_time + self.EPS
#             ):
#                 arrived = arrival_list.pop(0)
#                 heapq.heappush(
#                     self.ready_queue,
#                     (0.0, arrived.arrival_time, seq_counter, arrived),
#                 )
#                 seq_counter += 1

#             if not self.ready_queue and arrival_list:
#                 current_time = arrival_list[0].arrival_time
#                 continue

#             # 2. Rebalance queue with a single queue-wide alpha at this event tick
#             alpha = self._compute_queue_alpha(current_time)
#             rebalanced = []
#             while self.ready_queue:
#                 _, arr, seq, task = heapq.heappop(self.ready_queue)
#                 prio = -self.compute_priority(task, current_time, alpha)
#                 rebalanced.append((prio, arr, seq, task))
#             heapq.heapify(rebalanced)
#             self.ready_queue = rebalanced

#             # 3. Dispatch highest priority task
#             _, arrival, seq, current_task = heapq.heappop(self.ready_queue)
#             self.total_waiting_time += max(
#                 0.0, current_time - current_task.last_ready
#             )

#             # 4. Find earliest preemption point:
#             #    (a) next task arrival, or
#             #    (b) exact timestamp when a waiting task crosses its safety slack margin
#             next_arrival = (
#                 arrival_list[0].arrival_time if arrival_list else float("inf")
#             )
#             next_safety_time = float("inf")

#             if self.mode == "HYBRID":
#                 for _, _, _, waiting_task in self.ready_queue:
#                     margin = self._safety_margin(waiting_task)
#                     slack = (
#                         waiting_task.absolute_deadline - current_time
#                     ) - waiting_task.rem_est
#                     if slack > margin + self.EPS:
#                         t_crit = (
#                             waiting_task.absolute_deadline
#                             - waiting_task.rem_est
#                             - margin
#                         )
#                         if t_crit < next_safety_time:
#                             next_safety_time = t_crit

#             next_interrupt = min(next_arrival, next_safety_time)
#             time_to_interrupt = next_interrupt - current_time

#             if current_task.rem_true > time_to_interrupt + self.EPS:
#                 # Preempt running task and return it to the ready queue
#                 run_duration = time_to_interrupt
#                 current_time = next_interrupt
#                 current_task.rem_true -= run_duration
#                 current_task.rem_est = max(
#                     0.001, current_task.rem_est - run_duration
#                 )
#                 current_task.last_ready = current_time

#                 heapq.heappush(
#                     self.ready_queue, (0.0, arrival, seq, current_task)
#                 )
#             else:
#                 # Task finishes before any preemption event
#                 current_time += current_task.rem_true
#                 current_task.rem_true = 0.0
#                 self.total_completed += 1

#                 if current_time > current_task.absolute_deadline + self.EPS:
#                     self.missed_deadlines += 1

#         dmr = (
#             (self.missed_deadlines / self.total_completed * 100)
#             if self.total_completed
#             else 0.0
#         )
#         awt = (
#             (self.total_waiting_time / self.total_completed)
#             if self.total_completed
#             else 0.0
#         )

#         return {"DMR": dmr, "AWT": awt}



# v3
import heapq
from typing import List, Tuple, Dict, Hashable, Optional
from task_model import Task


class SimulatorEngine:
    EPS = 1e-9  # Floating-point tolerance for discrete event timestamps

    def __init__(
        self,
        mode: str,
        avg_E: float = 10.0,
        avg_D: float = 40.0,
        min_quantum: float = 0.5,
        ewma_beta: float = 0.3,
        enable_ewma: bool = True,
    ):
        """
        mode options:
        - 'PURE_EDF' : Preemptive Earliest Deadline First.
        - 'PURE_SJN' : Preemptive Shortest Job Next (SRTF) using estimated bursts.
        - 'PURE_RM'  : Preemptive Rate Monotonic (static priority ~ 1 / period).
        - 'HYBRID'   : Dynamic alpha-weighted SJN-EDF with EWMA & domino protection.
        """
        self.mode = mode.upper()
        self.avg_E = avg_E
        self.avg_D = avg_D
        self.min_quantum = max(0.0, min_quantum)
        self.ewma_beta = min(0.4, max(0.2, ewma_beta))  # Bounded to [0.2, 0.4]
        self.enable_ewma = enable_ewma

        self.ready_queue: List[Tuple[float, float, int, Task]] = []
        self.missed_deadlines = 0
        self.total_completed = 0
        self.total_waiting_time = 0.0
        self.total_dispatch_latency = 0.0
        self.context_switches = 0

    def _task_stream_key(self, task: Task) -> Hashable:
        """Identify recurring task streams for EWMA burst history tracking."""
        for attr in ("task_id", "id", "pid", "name"):
            val = getattr(task, attr, None)
            if val is not None:
                return val
        period = getattr(task, "period", round(task.absolute_deadline - task.arrival_time, 6))
        return (period, round(task.estimated_burst, 6))

    def _task_period(self, task: Task) -> float:
        """Extract task period T_i for Rate Monotonic priority assignment."""
        period = getattr(task, "period", None)
        if period is not None and period > 0:
            return float(period)
        rel_deadline = getattr(task, "relative_deadline", None)
        if rel_deadline is not None and rel_deadline > 0:
            return float(rel_deadline)
        return max(0.001, float(task.absolute_deadline - task.arrival_time))

    def _safety_margin(self, task: Task) -> float:
        """Safety buffer (Delta t_safety) to guard against burst underestimation."""
        return max(2.0, 0.25 * task.predicted_burst)

    def _compute_queue_alpha(self, current_time: float) -> float:
        """
        Compute adaptive weight alpha(t) across the three proposal load regimes
        plus overload domino-effect protection.
        """
        if self.mode == "PURE_EDF":
            return 0.0
        if self.mode in ("PURE_SJN", "PURE_RM", "RM"):
            return 1.0
        if not self.ready_queue:
            return 0.70

        u_sum = 0.0
        min_feasible_excess_slack = float("inf")
        has_feasible_task = False

        for _, _, _, t in self.ready_queue:
            time_left = max(0.001, t.absolute_deadline - current_time)
            slack = (t.absolute_deadline - current_time) - t.rem_est
            u_sum += t.rem_true / time_left

            # Only protect tasks that can still mathematically meet their deadline
            if slack >= -self.EPS:
                has_feasible_task = True
                excess_slack = slack - self._safety_margin(t)
                min_feasible_excess_slack = min(min_feasible_excess_slack, excess_slack)

        # 1. Safety override: force alpha = 0.0 if a feasible task is near its deadline
        if has_feasible_task and min_feasible_excess_slack <= self.EPS:
            return 0.0

        # 2. Transient overload domino-effect breaker (U > 100%):
        # Retain a 0.25 SJN weight so short jobs complete instead of cascading failures
        if u_sum > 1.00:
            return 0.25

        # 3. Proposal three-regime utilization scaling:
        #    Light (<70%): ~0.70 | Balanced (70%-85%): ~0.50 | Saturation (>=85%): -> 0.0
        if u_sum < 0.70:
            base_alpha = 0.70
        elif u_sum < 0.85:
            base_alpha = 0.50
        else:
            # Smoothly decay from 0.50 down to 0.0 between 85% and 100% load
            base_alpha = 0.50 * max(0.0, (1.00 - u_sum) / 0.15)

        if has_feasible_task and min_feasible_excess_slack < self.avg_E:
            slack_scale = max(0.0, min_feasible_excess_slack / max(0.001, self.avg_E))
            return base_alpha * slack_scale

        return base_alpha

    def compute_priority(
        self, task: Task, current_time: float, alpha: float = 0.5
    ) -> float:
        time_left = max(0.001, task.absolute_deadline - current_time)
        rem_est = max(0.001, getattr(task, "rem_est", task.estimated_burst))

        if self.mode == "PURE_EDF":
            return 1.0 / time_left

        elif self.mode == "PURE_SJN":
            return 1.0 / rem_est

        elif self.mode in ("PURE_RM", "RM"):
            return 1.0 / self._task_period(task)

        elif self.mode == "HYBRID":
            sjn_term = self.avg_E / rem_est
            edf_term = self.avg_D / time_left
            score = (alpha * sjn_term) + ((1.0 - alpha) * edf_term)

            # Domino-effect guard: demote tasks whose deadline is already impossible
            # so they do not starve feasible tasks during severe overload
            slack = (task.absolute_deadline - current_time) - rem_est
            if slack < -self.EPS:
                score *= 0.10

            return score

        return 0.0

    def run(self, task_list: List[Task]) -> Dict[str, float]:
        self.ready_queue = []
        self.missed_deadlines = 0
        self.total_completed = 0
        self.total_waiting_time = 0.0
        self.total_dispatch_latency = 0.0
        self.context_switches = 0

        current_time = 0.0
        seq_counter = 0
        ewma_estimates: Dict[Hashable, float] = {}

        # Clone tasks and attach mutable runtime tracking attributes
        arrival_list: List[Task] = []
        for idx, t in enumerate(sorted(task_list, key=lambda x: x.arrival_time)):
            task_copy = t.copy()
            task_copy.job_uid = idx
            task_copy.stream_key = self._task_stream_key(task_copy)
            task_copy.rem_true = float(task_copy.true_burst)
            task_copy.predicted_burst = float(task_copy.estimated_burst)
            task_copy.rem_est = float(task_copy.estimated_burst)
            task_copy.last_ready = float(task_copy.arrival_time)
            task_copy.first_dispatched = False
            arrival_list.append(task_copy)

        last_job_uid: Optional[int] = None
        protected_until: float = 0.0

        while arrival_list or self.ready_queue:
            # 1. Admit all tasks arrived by current_time and apply EWMA burst prediction
            while (
                arrival_list
                and arrival_list[0].arrival_time <= current_time + self.EPS
            ):
                arrived = arrival_list.pop(0)
                if self.enable_ewma:
                    if arrived.stream_key in ewma_estimates:
                        est = ewma_estimates[arrived.stream_key]
                        arrived.predicted_burst = est
                        arrived.rem_est = est
                    else:
                        ewma_estimates[arrived.stream_key] = arrived.predicted_burst

                heapq.heappush(
                    self.ready_queue,
                    (0.0, arrived.arrival_time, seq_counter, arrived),
                )
                seq_counter += 1

            # Fast-forward clock to next arrival when CPU is idle
            if not self.ready_queue and arrival_list:
                current_time = arrival_list[0].arrival_time
                last_job_uid = None
                continue

            # 2. Event-driven min-heap priority rebalance (O(N) rebuild at discrete ticks)
            alpha = self._compute_queue_alpha(current_time)
            rebalanced = []
            while self.ready_queue:
                _, arr, seq, task = heapq.heappop(self.ready_queue)
                prio = -self.compute_priority(task, current_time, alpha)
                rebalanced.append((prio, arr, seq, task))
            heapq.heapify(rebalanced)
            self.ready_queue = rebalanced

            # 3. Dispatch highest-priority task & record latency/context-switch metrics
            _, arrival, seq, current_task = heapq.heappop(self.ready_queue)

            self.total_waiting_time += max(
                0.0, current_time - current_task.last_ready
            )

            if not current_task.first_dispatched:
                self.total_dispatch_latency += max(
                    0.0, current_time - current_task.arrival_time
                )
                current_task.first_dispatched = True

            # Enforce non-preemptable Minimum Execution Quantum (Delta t_min) on new dispatch
            if current_task.job_uid != last_job_uid:
                if last_job_uid is not None:
                    self.context_switches += 1
                last_job_uid = current_task.job_uid
                protected_until = current_time + min(
                    self.min_quantum, current_task.rem_true
                )

            # 4. Compute earliest preemption interrupt point
            next_arrival = (
                arrival_list[0].arrival_time if arrival_list else float("inf")
            )
            next_safety_time = float("inf")

            if self.mode == "HYBRID":
                for _, _, _, waiting_task in self.ready_queue:
                    margin = self._safety_margin(waiting_task)
                    slack = (
                        waiting_task.absolute_deadline - current_time
                    ) - waiting_task.rem_est
                    if slack > margin + self.EPS:
                        t_crit = (
                            waiting_task.absolute_deadline
                            - waiting_task.rem_est
                            - margin
                        )
                        if t_crit < next_safety_time:
                            next_safety_time = t_crit

            raw_interrupt = min(next_arrival, next_safety_time)
            # Clamp interrupt so the running task cannot be preempted before protected_until
            effective_interrupt = max(raw_interrupt, protected_until)
            time_to_interrupt = effective_interrupt - current_time

            if current_task.rem_true > time_to_interrupt + self.EPS:
                # Preempt running task after its protected quantum expires
                run_duration = time_to_interrupt
                current_time = effective_interrupt
                current_task.rem_true -= run_duration

                # Guard against underestimated bursts collapsing rem_est to ~0
                if current_task.rem_est > run_duration + self.EPS:
                    current_task.rem_est -= run_duration
                else:
                    current_task.rem_est = max(0.5, 0.25 * current_task.predicted_burst)

                current_task.last_ready = current_time
                heapq.heappush(
                    self.ready_queue, (0.0, arrival, seq, current_task)
                )
            else:
                # Task completes uninterrupted
                current_time += current_task.rem_true
                current_task.rem_true = 0.0
                self.total_completed += 1

                if current_time > current_task.absolute_deadline + self.EPS:
                    self.missed_deadlines += 1

                # Update EWMA burst prediction for future instances of this task
                if self.enable_ewma:
                    prev_est = ewma_estimates.get(
                        current_task.stream_key, current_task.predicted_burst
                    )
                    ewma_estimates[current_task.stream_key] = (
                        self.ewma_beta * current_task.true_burst
                        + (1.0 - self.ewma_beta) * prev_est
                    )

        dmr = (
            (self.missed_deadlines / self.total_completed * 100)
            if self.total_completed
            else 0.0
        )
        awt = (
            (self.total_waiting_time / self.total_completed)
            if self.total_completed
            else 0.0
        )
        adl = (
            (self.total_dispatch_latency / self.total_completed)
            if self.total_completed
            else 0.0
        )
        csf = (self.context_switches / current_time) if current_time > 0 else 0.0

        return {
            "DMR": dmr,
            "AWT": awt,
            "context_switches": self.context_switches,
            "CSF": csf,
            "ADL": adl,
        }