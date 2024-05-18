import csv
from pathlib import Path

from .utils import (
    check_city_def,
    check_float,
    check_int,
    check_prob,
    check_state,
)
from .. import (
    City,
    CityGroup,
    Person,
    World,
)


FIELDS_CITIES = ("name", "x", "y")
FIELDS_CONNECTIONS = ("from", "to")
FIELDS_CITY_GROUPS = ("name", "city", "lockdown_regulation")
FIELDS_PEOPLE = (
    "city_name",
    "init_state",
    "p_infection",
    "p_staying",
    "action_regulation",
    "steps_for_onset",
    "steps_for_recover",
)


def load_cities(
    file_cities: Path | str,
    file_connections: Path | str,
    skip_rows: int = 1,
) -> tuple[dict[str, City], dict[str, tuple[float, float]]]:
    cities: dict[str, City] = {}
    connections: dict[City, set[City]] = {}
    cities_pos: dict[str, tuple[float, float]] = {}

    with open(file_cities, "rt") as f:
        reader = csv.DictReader(f, FIELDS_CITIES)

        for i, row in enumerate(reader):
            if i < skip_rows:
                continue
            line = i + 1

            # checking values of x and y
            x = check_float(row["x"], file_cities, line)
            y = check_float(row["y"], file_cities, line)

            city = City(row["name"])
            if row["name"] in cities:
                raise ValueError(
                    f"'{str(file_cities)}' line {line}: duplicated city "
                    f"name '{row['name']}' is found."
                )

            cities[row["name"]] = city
            connections[city] = set()
            cities_pos[row["name"]] = (x, y)

    with open(file_connections, "rt") as f:
        reader = csv.DictReader(f, FIELDS_CONNECTIONS)

        for i, row in enumerate(reader):
            if i < skip_rows:
                continue
            line = i + 1

            city_from = check_city_def(
                row["from"],
                cities,
                file_connections,
                line,
            )
            city_to = check_city_def(
                row["to"],
                cities,
                file_connections,
                line,
            )
            connections[city_from].add(city_to)

    for city, visitables in connections.items():
        city.setup_initial_visitables(*visitables)

    return cities, cities_pos


def load_city_groups(
    file: Path | str,
    cities: dict[str, City],
    skip_rows: int = 1,
) -> set[CityGroup]:
    city_groups: dict[str, CityGroup] = {}
    with open(file, "rt") as f:
        reader = csv.DictReader(f, FIELDS_CITY_GROUPS)

        for i, row in enumerate(reader):
            if i < skip_rows:
                continue
            line = i + 1

            city = check_city_def(row["city"], cities, file, line)
            lockdown_regulation = check_float(
                row["lockdown_regulation"],
                file,
                line,
            )

            if row["name"] in city_groups:
                city_group = city_groups[row["name"]]
                if city_group.lockdown_regulation != lockdown_regulation:
                    raise ValueError(
                        f"'{str(file)}' line {line}: Lockdown regulation is "
                        "not consistent for all definitions."
                    )

                city_group.add_city(city)
            else:
                city_group = CityGroup(
                    row["name"],
                    [city],
                    lockdown_regulation=lockdown_regulation,
                )
                city_groups[row["name"]] = city_group

    return set(city_groups.values())


def load_people(
    file: Path | str,
    cities: dict[str, City],
    skip_rows: int = 1,
) -> list[Person]:
    people: list[Person] = []

    with open(file, "rt") as f:
        reader = csv.DictReader(f, FIELDS_PEOPLE)

        for i, row in enumerate(reader):
            if i < skip_rows:
                continue
            line = i + 1

            city = check_city_def(row["city_name"], cities, file, line)
            init_state = check_state(row["init_state"], file, line)
            p_infection = check_prob(row["p_infection"], file, line)
            p_staying = check_prob(row["p_staying"], file, line)
            action_regulation = check_prob(
                row["action_regulation"],
                file,
                line,
            )
            steps_for_onset = check_int(
                row["steps_for_onset"],
                file,
                line,
                positive=True
            )
            steps_for_recover = check_int(
                row["steps_for_recover"],
                file,
                line,
                positive=True,
            )

            person = Person(
                city,
                init_state,
                p_infection,
                p_staying,
                action_regulation,
                steps_for_onset,
                steps_for_recover,
            )
            people.append(person)

    return people


def load_world(
    file_cities: Path | str,
    file_connections: Path | str,
    file_city_groups: Path | str,
    file_people: Path | str,
    skip_rows: int = 1,
) -> tuple[World, dict[str, tuple[float, float]]]:
    cities, cities_pos = load_cities(
        file_cities,
        file_connections,
        skip_rows=skip_rows,
    )
    city_groups = load_city_groups(
        file_city_groups,
        cities,
        skip_rows=skip_rows,
    )
    people = load_people(file_people, cities, skip_rows=skip_rows)
    return World(people, set(cities.values()), city_groups), cities_pos
