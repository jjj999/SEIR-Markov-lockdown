import multiprocessing as mp
from pathlib import Path
import time

from PIL import Image
import japanize_matplotlib
import matplotlib as mpl
import matplotlib.animation as anim
import matplotlib.pyplot as plt
from seir_markov_lockdown import (
    City,
    Person,
    PersonState,
)
from seir_markov_lockdown.app import (
    DEFAULT_PERSON_ALPHAS,
    DEFAULT_PERSON_COLORS,
    init_draw_axis,
    draw_interpolation,
    draw_people,
    load_world_from_snapshot,
    load_world_from_snapshot,
)


def plot_anim_frame_with_interpolation(
    i: int,
    fig: mpl.figure.Figure,
    axis: mpl.axes.Axes,
    dir_cond: Path,
    files_snapshot: list[Path],
    background: Image,
    cities: list[City],
    cities_pos: dict[str, tuple[float, float]],
    next_people: list[Person],
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

    axis.imshow(background, extent=[0, 200, 0, 150], alpha=0.5)

    axis.text(140, 100, "墨田区")
    axis.text(137, 70, "江東区")
    axis.text(122, 93, "台東区")
    axis.text(122, 105, "荒川区")
    axis.text(116, 70, "中央区")
    axis.text(102, 79, "千代田区")
    axis.text(98, 96, "文京区")
    axis.text(87, 105, "豊島区")
    axis.text(87, 88, "新宿区")
    axis.text(70, 76, "渋谷区")
    axis.text(94, 58, "港区")
    axis.text(83, 45, "品川区")
    axis.text(72, 53, "目黒区")

    axis = init_draw_axis(
        axis,
        cities,
        cities_pos,
        xlim=xlim,
        ylim=ylim,
        city_color=city_color,
        city_size=city_size,
        person_size=person_size,
        person_colors=person_colors,
    )

    if i % interpolation_frames == 0:
        axis = draw_people(
            axis,
            next_people,
            cities_pos,
            person_radius=person_radius,
            person_size=person_size,
            person_colors=person_colors,
            person_alphas=person_alphas,
        )

        prev_people.clear()
        prev_people.extend(next_people)
        world, _ = load_world_from_snapshot(
            files_snapshot[i // interpolation_frames],
            dir_cond / "cities.csv",
            dir_cond / "connections.csv",
            dir_cond / "city_groups.csv",
            dir_cond / "people.csv",
        )

        next_people.clear()
        next_people.extend(world.people)

        cities.clear()
        cities.extend(world.cities)
    else:
        axis = draw_interpolation(
            axis,
            next_people,
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
        fig.legend(loc="lower left", bbox_to_anchor=(0.07, 0.1, 1, 1))


def plot_anim(
    dir_cond: Path,
) -> None:
    dir_snapshots = dir_cond / "snapshots"
    files_snapshot = list(dir_snapshots.iterdir())

    world, cities_pos = load_world_from_snapshot(
        files_snapshot[0],
        dir_cond / "cities.csv",
        dir_cond / "connections.csv",
        dir_cond / "city_groups.csv",
        dir_cond / "people.csv",
    )
    im = Image.open("tokyo.png")
    interpolation_frames = 3
    fig, axis = plt.subplots()

    ani = anim.FuncAnimation(
        fig,
        plot_anim_frame_with_interpolation,
        frames=5000 * interpolation_frames + 1,
        interval=100 // interpolation_frames,
        fargs=(
            fig,
            axis,
            dir_cond,
            files_snapshot,
            im,
            list(world.cities),
            cities_pos,
            list(world.people),
            [],
            interpolation_frames,
            (70, 150),
            (40, 110),
            "black",
            100,
            20,
            2,
        ),
    )

    ani.save(dir_cond / "result.mp4", dpi=100)


def main(*dirs_cond: str, num_processes: int = 6) -> None:
    dirs_cond = [Path(dir_cond) for dir_cond in dirs_cond]
    next_cond = 0

    processes: list[mp.Process] = []
    for _ in range(num_processes):
        ps = mp.Process(target=plot_anim, args=(dirs_cond[next_cond],))
        ps.start()
        processes.append(ps)
        next_cond += 1

    while next_cond < len(dirs_cond):
        for i, ps in enumerate(processes):
            if ps.is_alive():
                continue

            new_ps = mp.Process(target=plot_anim, args=(dirs_cond[next_cond],))
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
