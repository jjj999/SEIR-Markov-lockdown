from pathlib import Path

import click

from .app import (
    load_plot_config,
    load_snapshot_config,
    load_world,
    plot_anim,
    snapshot_world,
)


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("file_config", type=click.Path(exists=True))
def plot(file_config: str) -> None:
    """Run simulation of 'SEIR Markov lockdown' model and plot the results
    with the config in FILE_CONFIG.
    """
    config = load_plot_config(file_config)
    plot_anim(config)


@main.command()
@click.argument("file_config", type=click.Path(exists=True))
def snapshot(file_config: str) -> None:
    """Run simulation of 'SEIR Markov lockdown' model and take snapshots of
    the results with the config in FILE_CONFIG.
    """
    config = load_snapshot_config(file_config)
    digits = len(str(config.steps))

    dir_snapshots = Path(config.dir_snapshots).resolve()
    if not dir_snapshots.exists():
        dir_snapshots.mkdir()

    world, _ = load_world(
        config.file_cities,
        config.file_connections,
        config.file_city_groups,
        config.file_people,
    )
    for i in range(0, config.steps + 1):
        path_snapshot = dir_snapshots / f"{str(i).zfill(digits)}.csv"
        if i == 0:
            snapshot_world(world, path_snapshot)

        world.update()
        snapshot_world(world, path_snapshot)


main()
