from __future__ import annotations
import typing as t


class City:

    def __init__(
        self,
        name: str,
    ) -> None:
        self._name = name
        self._initial_visitables: t.Optional[set[City]] = None
        self._current_visitables: t.Optional[set[City]] = None
        self._in_lockdown = False

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, city: City) -> bool:
        return self.name == city.name

    def __hash__(self) -> int:
        return hash(self._name)

    def __str__(self) -> str:
        return self._name

    def setup_initial_visitables(self, *visitables: City) -> None:
        if self._initial_visitables is not None:
            raise ValueError("Initial visitables have already been set.")

        self._initial_visitables = set(visitables)
        self._current_visitables = set(visitables)

    @property
    def initial_visitables(self) -> tuple[City]:
        assert self._initial_visitables is not None
        return tuple(self._initial_visitables)

    @property
    def current_visitables(self) -> tuple[City]:
        assert self._current_visitables is not None
        return tuple(self._current_visitables)

    @property
    def in_lockdown(self) -> bool:
        return self._in_lockdown

    def lock(self) -> None:
        assert self._current_visitables is not None
        self._current_visitables.clear()
        self._in_lockdown = True

    def unlock(self) -> None:
        assert self._initial_visitables is not None

        visitable = set()
        for possible in self._initial_visitables:
            if not possible.in_lockdown:
                visitable.add(possible)

        self._current_visitables = visitable
        self._in_lockdown = False

    def reset_visitables(self) -> None:
        assert self._initial_visitables is not None
        self._current_visitables = self._initial_visitables.copy()

    def add_visitable(self, city: City) -> None:
        assert self._current_visitables is not None
        self._current_visitables.add(city)

    def remove_visitable(self, city: City) -> None:
        assert self._current_visitables is not None
        self._current_visitables.remove(city)


class CityGroup:

    def __init__(
        self,
        name: str,
        cities: list[City],
        lockdown_regulation: float,
        in_lockdown: bool = False,
    ) -> None:
        self._name = name
        self._cities = set(cities)
        self._lockdown_regulation = lockdown_regulation
        self._in_lockdown = in_lockdown

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, city_group: CityGroup) -> bool:
        return self.name == city_group.name

    @property
    def cities(self) -> tuple[City]:
        return tuple(self._cities)

    def has_city(self, city: City) -> bool:
        return city in self._cities

    @property
    def lockdown_regulation(self) -> float:
        return self._lockdown_regulation

    @property
    def in_lockdown(self) -> bool:
        return self._in_lockdown

    def lock(self, cities: list[City]) -> None:
        self._in_lockdown = True

        for city in cities:
            # Restricting locked -> unlocked.
            if city in self._cities:
                city.lock()
            # Resricting unlocked -> locked.
            else:
                for city_lockdowned in self._cities:
                    if city_lockdowned in city._current_visitables:
                        city.remove_visitable(city_lockdowned)

    def unlock(self, cities: list[City]) -> None:
        self._in_lockdown = False

        for city in cities:
            # Enabling locked -> unlocked.
            if city in self._cities:
                city.unlock()
            # Enabling unlocked -> locked.
            else:
                for city_lockdowned in self._cities:
                    if city_lockdowned in city._initial_visitables:
                        city.add_visitable(city_lockdowned)
