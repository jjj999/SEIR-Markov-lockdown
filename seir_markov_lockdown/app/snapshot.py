import csv
from pathlib import Path

from .load import load_world
from .utils import (
    check_city_def,
    check_nullable_int,
    check_state,
)
from ..world import World


FIELDS_SNAPSHOTS = (
    "state",
    "city_name",
    "remaining_steps_for_onset",
    "remaining_steps_for_recover",
)


def snapshot_world(world: World, file: Path | str) -> None:
    with open(file, "wt") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(FIELDS_SNAPSHOTS)

        for person in world.people:
            writer.writerow([
                person.state.name,
                person.position.name,
                person.remaining_steps_for_onset,
                person.remaining_steps_for_recover,
            ])


def load_world_from_snapshot(
    file_snapshot: Path | str,
    file_cities: Path | str,
    file_connections: Path | str,
    file_city_groups: Path | str,
    file_people: Path | str,
    skip_rows: int = 1,
) -> World:
    world, _ = load_world(
        file_cities,
        file_connections,
        file_city_groups,
        file_people,
    )

    with open(file_snapshot, "rt") as f:
        reader = csv.reader(f, FIELDS_SNAPSHOTS)

        for i, (person, row) in enumerate(zip(world.people, reader)):
            if i < skip_rows:
                continue
            line = i + 1

            (state, city_name, remaining_steps_for_onset,
             remaining_steps_for_recover) = row

            person._state = check_state(state, file_snapshot, line)
            person._remaining_steps_for_onset = check_nullable_int(
                remaining_steps_for_onset,
                file_snapshot,
                line,
            )
            person._remaining_steps_for_recover = check_nullable_int(
                remaining_steps_for_recover,
                file_snapshot,
                line,
            )
            person._position = check_city_def(
                city_name,
                world.cities,
                file_snapshot,
                line,
            )

    world._lockdown()
    return world
