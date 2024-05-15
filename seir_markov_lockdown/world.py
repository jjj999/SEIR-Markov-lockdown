from .city import (
    City,
    CityGroup,
)
from .person import (
    CountsPeople_t,
    Person,
    PersonState,
)


class World:

    def __init__(
        self,
        people: list[Person],
        cities: list[City],
        city_groups: list[CityGroup],
    ) -> None:
        self._people = people
        self._cities = cities
        self._city_groups = city_groups

    @property
    def people(self) -> tuple[Person]:
        return tuple(self._people)

    @property
    def cities(self) -> tuple[City]:
        return tuple(self._cities)

    @property
    def city_groups(self) -> tuple[CityGroup]:
        return tuple(self._city_groups)

    def update(self) -> None:
        self._lockdown()

        for person in self._people:
            person.update_position()

        for city in self.cities:
            counts = self._count_people_in_city(city)
            for person in self._get_people_in_city(city):
                person.eval_next_state(counts)

        for person in self._people:
            person.update_state()

    def _get_people_in_same_city(self, person: Person) -> list[Person]:
        result = []
        for someone in self._people:
            if someone == person:
                continue
            if someone.position == person.position:
                result.append(someone)
        return result

    def _lockdown(self) -> None:
        for city_group in self._city_groups:
            counts = self._count_people_in_city_group(city_group)
            num_people = sum(counts.values())
            if num_people == 0:
                continue

            rate_infected = counts[PersonState.I] / num_people
            if rate_infected >= city_group.lockdown_regulation:
                city_group.lock(self._cities)
            else:
                city_group.unlock(self._cities)

    def _get_people_in_city(self, city: City) -> list[Person]:
        return [person for person in self._people if person.position == city]

    def _count_people_in_city(self, city: City) -> CountsPeople_t:
        result = {
            PersonState.S: 0,
            PersonState.E: 0,
            PersonState.I: 0,
            PersonState.R: 0,
        }
        for person in self._get_people_in_city(city):
            result[person.state] += 1
        return result

    def _count_people_in_city_group(
        self,
        city_group: CityGroup,
    ) -> CountsPeople_t:
        result = {
            PersonState.S: 0,
            PersonState.E: 0,
            PersonState.I: 0,
            PersonState.R: 0,
        }
        for city in city_group.cities:
            for person in self._get_people_in_city(city):
                result[person.state] += 1
        return result
