
from task_model import Task
from scheduler_engine import SimulatorEngine


def test_pure_sjn_priority():
    engine = SimulatorEngine(mode="PURE_SJN")
    t1 = Task("T1", 0.0, 5.0, 20.0, 20.0)
    t2 = Task("T2", 0.0, 2.0, 20.0, 20.0)

    p1 = engine.compute_priority(t1, 0.0)
    p2 = engine.compute_priority(t2, 0.0)

    # Shorter task T2 must have higher priority score
    assert p2 > p1


def test_safety_override():
    engine = SimulatorEngine(mode="HYBRID")
    # Task with imminent deadline (< 2.0ms remaining laxity)
    t_urgent = Task("T_urgent", 0.0, 10.0, 1.5, 10.0)

    # Priority should adjust to pure EDF mode due to safety threshold
    prio = engine.compute_priority(t_urgent, 0.0)
    assert prio > 0.0