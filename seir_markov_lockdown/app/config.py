from pathlib import Path

import pydantic
import yaml


class PlotConfig(pydantic.BaseModel):

    # input settings
    file_cities: str
    file_connections: str
    file_city_groups: str
    file_people: str
    steps: int

    # output settings
    file_output: str
    dpi: int = 100

    # plot settings
    xlim_min: int | float = 0.
    xlim_max: int | float = 100.
    ylim_min: int | float = 0.
    ylim_max: int | float = 100.

    city_color: str = "black"
    city_size: int = 300

    person_size: int = 100
    person_radius: float = 8.

    interval_per_step: int | float = 500    # ms
    interpolation_frames: int = 10          # if < 1, no interpolation.


def load_plot_config(file_config: Path | str) -> PlotConfig:
    with open(file_config, "rt") as f:
        config = yaml.safe_load(f)

    return PlotConfig(**config)
