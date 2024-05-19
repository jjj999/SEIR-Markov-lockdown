import copy
import math
import typing as t

import matplotlib as mpl
import matplotlib.animation as anim
import matplotlib.pyplot as plt

from .config import PlotConfig
from .load import load_world
from .. import (
    City,
    Person,
    PersonState,
    World,
)


DEFAULT_PERSON_COLORS: dict[PersonState, str] = {
    PersonState.S: "blue",
    PersonState.E: "orange",
    PersonState.I: "red",
    PersonState.R: "green",
}
DEFAULT_PERSON_ALPHAS: dict[PersonState, float] = {
    PersonState.S: 0.1,
    PersonState.E: 0.5,
    PersonState.I: 1.0,
    PersonState.R: 0.1,
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
    person_alphas: dict[PersonState, float] = DEFAULT_PERSON_ALPHAS,
) -> mpl.axes.Axes:
    population = len(people)
    state_xy = {
        PersonState.S: [[], []],
        PersonState.E: [[], []],
        PersonState.I: [[], []],
        PersonState.R: [[], []],
    }

    for i, person in enumerate(people):
        x, y = calc_person_position(
            cities_pos[person.position.name],
            person_radius,
            population,
            i,
        )
        state_xy[person.state][0].append(x)
        state_xy[person.state][1].append(y)

    for state, (x, y) in state_xy.items():
        axis.scatter(
            x,
            y,
            s=person_size,
            color=person_colors[state],
            alpha=person_alphas[state],
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
    person_alphas: dict[PersonState, str] = DEFAULT_PERSON_ALPHAS,
) -> mpl.axes.Axes:
    population = len(next_people)
    state_xy = {
        PersonState.S: [[], []],
        PersonState.E: [[], []],
        PersonState.I: [[], []],
        PersonState.R: [[], []],
    }

    for i, person in enumerate(zip(next_people, prev_people)):
        next_person, previous_person = person

        if next_person.position == previous_person.position:
            x, y = calc_person_position(
                cities_pos[next_person.position.name],
                person_radius,
                population,
                i,
            )
            state = next_person.state
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

            if next_pos[0] - prev_pos[0] == 0:
                delta_y = (next_pos[1] - prev_pos[1]) / interpolation_frames
                x = prev_pos[0]
                y = prev_pos[1] + delta_y * step
            else:
                slope = (next_pos[1] - prev_pos[1]) / (next_pos[0] - prev_pos[0])
                delta_x = (next_pos[0] - prev_pos[0]) / interpolation_frames
                x = prev_pos[0] + delta_x * step
                y = prev_pos[1] + slope * delta_x * step

            if step < (interpolation_frames / 2):
                state = next_person.state
            else:
                state = previous_person.state

        state_xy[state][0].append(x)
        state_xy[state][1].append(y)

    for state, (x, y) in state_xy.items():
        axis.scatter(
            x,
            y,
            s=person_size,
            color=person_colors[state],
            alpha=person_alphas[state],
        )

    return axis


def plot_anim_frame(
    i: int,
    fig: mpl.figure.Figure,
    axis: mpl.axes.Axes,
    world: World,
    cities_pos: dict[str, tuple[float, float]],
    xlim: tuple[float, float] = (0., 100.),
    ylim: tuple[float, float] = (0., 100.),
    city_color: str = "black",
    city_size: int = 300,
    person_size: int = 100,
    person_radius: float = 8.,
    person_colors: dict[PersonState, str] = DEFAULT_PERSON_COLORS,
    person_alphas: dict[PersonState, str] = DEFAULT_PERSON_ALPHAS,
) -> None:
    axis.cla()
    axis = fig.get_axes()[0]

    axis = init_draw_axis(
        axis,
        world.cities,
        cities_pos,
        xlim=xlim,
        ylim=ylim,
        city_color=city_color,
        city_size=city_size,
        person_size=person_size,
        person_colors=person_colors,
    )
    axis = draw_people(
        axis,
        world.people,
        cities_pos,
        person_radius=person_radius,
        person_size=person_size,
        person_colors=person_colors,
        person_alphas=person_alphas,
    )

    axis.set_title(f"Step: {i + 1}")
    axis.tick_params(
        bottom=False, left=False, right=False, top=False,
        labelbottom=False, labelleft=False, labelright=False, labeltop=False,
    )
    if i == 0:
        fig.legend(loc="lower left", bbox_to_anchor=(0.1, 0.1, 1, 1))

    world.update()


def plot_anim_frame_with_interpolation(
    i: int,
    fig: mpl.figure.Figure,
    axis: mpl.axes.Axes,
    world: World,
    cities_pos: dict[str, tuple[float, float]],
    prev_people: list[Person],
    interpolation_frames: int,
    xlim: tuple[float, float] = (0., 100.),
    ylim: tuple[float, float] = (0., 100.),
    city_color: str = "black",
    city_size: int = 300,
    person_size: int = 100,
    person_radius: float = 8.,
    person_colors: dict[PersonState, str] = DEFAULT_PERSON_COLORS,
    person_alphas: dict[PersonState, str] = DEFAULT_PERSON_ALPHAS,
) -> None:
    axis.cla()
    axis = fig.get_axes()[0]

    axis = init_draw_axis(
        axis,
        world.cities,
        cities_pos,
        xlim=xlim,
        ylim=ylim,
        city_color=city_color,
        city_size=city_size,
        person_size=person_size,
        person_colors=person_colors,
    )

    if i % interpolation_frames == 0:
        prev_people.clear()
        prev_people.extend([copy.copy(p) for p in world.people])
        axis = draw_people(
            axis,
            world.people,
            cities_pos,
            person_radius=person_radius,
            person_size=person_size,
            person_colors=person_colors,
            person_alphas=person_alphas,
        )
        world.update()
    else:
        axis = draw_interpolation(
            axis,
            world.people,
            prev_people,
            cities_pos,
            interpolation_frames,
            i % interpolation_frames,
            person_radius=person_radius,
            person_size=person_size,
            person_colors=person_colors,
            person_alphas=person_alphas,
        )

    axis.set_title(f"Step: {i // interpolation_frames + 1}")
    axis.tick_params(
        bottom=False, left=False, right=False, top=False,
        labelbottom=False, labelleft=False, labelright=False, labeltop=False,
    )
    if i == 0:
        fig.legend(loc="lower left", bbox_to_anchor=(0.1, 0.1, 1, 1))


def plot_anim(config: PlotConfig) -> None:
    world, cities_pos = load_world(
        config.file_cities,
        config.file_connections,
        config.file_city_groups,
        config.file_people,
    )
    fig, axis = plt.subplots()

    if config.interpolation_frames > 0:
        ani = anim.FuncAnimation(
            fig,
            plot_anim_frame_with_interpolation,
            frames=config.steps * config.interpolation_frames,
            interval=config.interval_per_step // config.interpolation_frames,
            fargs=(
                fig,
                axis,
                world,
                cities_pos,
                [],
                config.interpolation_frames,
                (config.xlim_min, config.xlim_max),
                (config.ylim_min, config.ylim_max),
                config.city_color,
                config.city_size,
                config.person_size,
                config.person_radius,
            ),
        )
    else:
        ani = anim.FuncAnimation(
            fig,
            plot_anim_frame,
            frames=config.steps,
            interval=config.interval_per_step,
            fargs=(
                fig,
                axis,
                world,
                cities_pos,
                (config.xlim_min, config.xlim_max),
                (config.ylim_min, config.ylim_max),
                config.city_color,
                config.city_size,
                config.person_size,
                config.person_radius,
            ),
        )

    ani.save(config.file_output, dpi=config.dpi)
