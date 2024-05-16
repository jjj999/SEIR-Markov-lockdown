import click

from .app import (
    load_plot_config,
    plot_anim,
)


@click.command()
@click.argument("file_config", type=click.Path(exists=True))
def main(file_config: str) -> None:
    """Run simulation of 'SEIR Markov lockdown' model with the config in
    FILE_CONFIG.
    """
    config = load_plot_config(file_config)
    plot_anim(config)


main()
