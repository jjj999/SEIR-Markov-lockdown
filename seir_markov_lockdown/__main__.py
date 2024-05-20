import click

from .app import (
    load_plot_config,
    load_snapshot_config,
    plot_anim,
    run_with_snapshots,
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
    run_with_snapshots(config)


main()
