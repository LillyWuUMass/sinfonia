from typing import List, Callable
from multiprocessing import Process


_jobs: List[Callable] = []


def register(f: Callable):
    _jobs.append(f)


def start():
    """Start registered daemons (sub-processes)"""
    for j in _jobs:
        p = Process(target=j, daemon=True)
        p.start()
        