import os
import multiprocessing as mp
from pathlib import Path
import time

from seir_markov_lockdown.app import (
    load_snapshot_config,
    run_with_snapshots,
)


def run_simulation(dir_cond: Path) -> None:
    os.chdir(dir_cond)
    config = load_snapshot_config("snapshot_config.yaml")
    run_with_snapshots(config)


def main(*dirs_cond: str, num_processes: int = 6) -> None:
    dirs_cond = [Path(dir_cond) for dir_cond in dirs_cond]
    next_cond = 0

    processes: list[mp.Process] = []
    for _ in range(num_processes):
        ps = mp.Process(target=run_simulation, args=(dirs_cond[next_cond],))
        ps.start()
        processes.append(ps)
        next_cond += 1

    while next_cond < len(dirs_cond):
        for i, ps in enumerate(processes):
            if ps.is_alive():
                continue

            new_ps = mp.Process(
                target=run_simulation,
                args=(dirs_cond[next_cond],),
            )
            new_ps.start()
            processes[i] = new_ps
            next_cond += 1

        time.sleep(0.1)


if __name__ == "__main__":
    main(
        "a=0.0,p_infection=0.3,lockdown_regulation=0.1",
        "a=0.0,p_infection=0.3,lockdown_regulation=0.3",
        "a=0.0,p_infection=0.3,lockdown_regulation=0.5",
        "a=0.0,p_infection=0.5,lockdown_regulation=0.1",
        "a=0.0,p_infection=0.5,lockdown_regulation=0.3",
        "a=0.0,p_infection=0.5,lockdown_regulation=0.5",
        "a=0.0,p_infection=0.7,lockdown_regulation=0.1",
        "a=0.0,p_infection=0.7,lockdown_regulation=0.3",
        "a=0.0,p_infection=0.7,lockdown_regulation=0.5",
        "a=0.5,p_infection=0.3,lockdown_regulation=0.1",
        "a=0.5,p_infection=0.3,lockdown_regulation=0.3",
        "a=0.5,p_infection=0.3,lockdown_regulation=0.5",
        "a=0.5,p_infection=0.5,lockdown_regulation=0.1",
        "a=0.5,p_infection=0.5,lockdown_regulation=0.3",
        "a=0.5,p_infection=0.5,lockdown_regulation=0.5",
        "a=0.5,p_infection=0.7,lockdown_regulation=0.1",
        "a=0.5,p_infection=0.7,lockdown_regulation=0.3",
        "a=0.5,p_infection=0.7,lockdown_regulation=0.5",
        "a=1.0,p_infection=0.3,lockdown_regulation=0.1",
        "a=1.0,p_infection=0.3,lockdown_regulation=0.3",
        "a=1.0,p_infection=0.3,lockdown_regulation=0.5",
        "a=1.0,p_infection=0.5,lockdown_regulation=0.1",
        "a=1.0,p_infection=0.5,lockdown_regulation=0.3",
        "a=1.0,p_infection=0.5,lockdown_regulation=0.5",
        "a=1.0,p_infection=0.7,lockdown_regulation=0.1",
        "a=1.0,p_infection=0.7,lockdown_regulation=0.3",
        "a=1.0,p_infection=0.7,lockdown_regulation=0.5",
    )
