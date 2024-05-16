import csv
from pathlib import Path

from .. import (
    City,
    CityGroup,
    Person,
    PersonState,
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

            # checking x
            try:
                x = float(row["x"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file_cities)}' line {i + 2}: could not convert "
                    f"string to float: '{row['x']}'."
                ) from e

            # checking y
            try:
                y = float(row["y"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file_cities)}' line {i + 2}: could not convert "
                    f"string to float: '{row['y']}'."
                ) from e

            city = City(row["name"])
            if row["name"] in cities:
                raise ValueError(
                    f"'{str(file_cities)}' line {i + 2}: duplicated city "
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

            if row["from"] not in cities:
                raise ValueError(
                    f"'{str(file_cities)}' line {i + 2}: city '{row['from']}'"
                    " is not defined."
                )
            if row["to"] not in cities:
                raise ValueError(
                    f"'{str(file_cities)}' line {i + 2}: city '{row['to']}'"
                    " is not defined."
                )

            city_from = cities[row["from"]]
            city_to = cities[row["to"]]
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

            if row["city"] not in cities:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: city '{row['city']}' is "
                    "not defined."
                )
            city = cities[row["city"]]

            try:
                lockdown_regulation = float(row["lockdown_regulation"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to float: '{row['lockdown_regulation']}'."
                ) from e

            if row["name"] in city_groups:
                city_group = city_groups[row["name"]]
                if city_group.lockdown_regulation != lockdown_regulation:
                    raise ValueError(
                        f"'{str(file)}' line {i + 2}: Lockdown regulation is "
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

            # checking city
            if row["city_name"] not in cities:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: city '{row['city_name']}' "
                    "is not defined."
                )
            city = cities[row["city_name"]]

            # checking initial state
            if row["init_state"] in PersonState.__members__.keys():
                init_state = PersonState.__members__[row["init_state"]]
            else:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: init_state"
                    f"'{row['init_state']}' is not supported."
                )

            # checking p_infection
            try:
                p_infection = float(row["p_infection"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to float: '{row['p_infection']}'."
                ) from e

            # checking p_staying
            try:
                p_staying = float(row["p_staying"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to float: '{row['p_staying']}'."
                ) from e

            # checking action_regulation
            try:
                action_regulation = float(row["action_regulation"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to float: '{row['action_regulation']}'."
                ) from e

            # checking steps_for_onset
            try:
                steps_for_onset = int(row["steps_for_onset"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to int: '{row['steps_for_onset']}'."
                ) from e
            if steps_for_onset < 1:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: steps_for_onset must be a "
                    "positive number."
                )

            # checking steps_for_recover
            try:
                steps_for_recover = int(row["steps_for_recover"])
            except ValueError as e:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: could not convert string "
                    f"to int: '{row['steps_for_recover']}'."
                ) from e
            if steps_for_recover < 1:
                raise ValueError(
                    f"'{str(file)}' line {i + 2}: steps_for_recover must be a "
                    "positive number."
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
