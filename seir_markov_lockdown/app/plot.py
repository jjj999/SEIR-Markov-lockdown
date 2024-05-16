import math
import typing as t

import matplotlib as mpl
import matplotlib.animation as anim
import matplotlib.pyplot as plt

from .. import (
    Person,
    PersonState,
    City,
)


DEFAULT_PERSON_COLORS = {
    PersonState.S: "blue",
    PersonState.E: "orange",
    PersonState.I: "red",
    PersonState.R: "green",
}


def init_draw_axis(
    axis: mpl.axes.Axes,
    cities: t.Sequence[City],
    cities_pos: dict[str, tuple[float, float]],
    xlim: tuple[float, float] = (0., 100.),
    ylim: tuple[float, float] = (0., 100.),
    city_color: str = "black",
    city_size: int = 300,
    person_size: int = 100,
    person_colors: dict[PersonState, str] = DEFAULT_PERSON_COLORS,
) -> mpl.axes.Axes:
    axis.set_xlim(*xlim)
    axis.set_ylim(*ylim)
    axis.set_aspect("equal")

    for city in cities:
        if city.in_lockdown:
            facecolors=city_color
        else:
            facecolors="none"

        x, y = cities_pos[city.name]
        axis.scatter(
            x,
            y,
            s=city_size,
            facecolors=facecolors,
            edgecolors=city_color,
        )

        for visitable in city.current_visitables:
            x_visitable, y_visitable = cities_pos[visitable.name]
            axis.plot(
                (x, x_visitable),
                (y, y_visitable),
                color="black",
            )

    # dummy plots for legend
    # NOTE the magic numbers might be defined more strictly.
    # Now dummy points are plotted outside in left bottom of the axis.
    dummy_plot_pos = (axis.get_xlim()[0] - 10, axis.get_ylim()[0] - 10)
    for state, color in person_colors.items():
        axis.scatter(
            *dummy_plot_pos,
            s=person_size,
            color=color,
            label=state.name,
        )

    return axis


def calc_person_position(
    center_pos: tuple[float, float],
    radius: float,
    total_num: int,
    index: int,
) -> tuple[float, float]:
    angle = 2 * math.pi * index / total_num
    x = center_pos[0] + radius * math.cos(angle)
    y = center_pos[1] + radius * math.sin(angle)
    return (x, y)


def draw_people(
    axis: mpl.axes.Axes,
    people: t.Sequence[Person],
    cities_pos: dict[str, tuple[float, float]],
    person_radius: float = 8.,
    person_size: int = 100,
    person_colors: dict[PersonState, str] = DEFAULT_PERSON_COLORS,
) -> mpl.axes.Axes:
    population = len(people)
    for i, person in enumerate(people):
        axis.scatter(
            *calc_person_position(
                cities_pos[person.position.name],
                person_radius,
                population,
                i,
            ),
            s=person_size,
            color=person_colors[person.state],
        )
    return axis


def draw_interpolation(
    axis: mpl.axes.Axes,
    next_people: list[Person],
    prev_people: list[Person],
    cities_pos: dict[str, tuple[float, float]],
    interpolation_frames: int,
    step: int,
    person_radius: float = 8.,
    person_size: int = 100,
    person_colors: dict[PersonState, str] = DEFAULT_PERSON_COLORS,
) -> mpl.axes.Axes:
    population = len(next_people)
    for i, person in enumerate(zip(next_people, prev_people)):
        next_person, previous_person = person

        if next_person.position == previous_person.position:
            x, y = calc_person_position(
                cities_pos[next_person.position.name],
                person_radius,
                population,
                i,
            )
            color=person_colors[next_person.state]
        else:
            next_pos = calc_person_position(
                cities_pos[next_person.position.name],
                person_radius,
                population,
                i,
            )
            prev_pos = calc_person_position(
                cities_pos[previous_person.position.name],
                person_radius,
                population,
                i,
            )
            slope = (next_pos[1] - prev_pos[1]) / (next_pos[0] - prev_pos[0])
            delta_x = (next_pos[0] - prev_pos[0]) / interpolation_frames

            if step < (interpolation_frames / 2):
                color = person_colors[next_person.state]
            else:
                color = person_colors[previous_person.state]

            x = prev_pos[0] + delta_x * step
            y = prev_pos[1] + slope * delta_x * step

        axis.scatter(x, y, s=person_size, color=color)

    return axis
