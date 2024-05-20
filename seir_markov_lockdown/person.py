from __future__ import annotations
import enum
import random
import typing as t

from .city import City


class PersonState(enum.Enum):

    S = enum.auto()
    E = enum.auto()
    I = enum.auto()
    R = enum.auto()


CountsPeople_t = dict[PersonState, int]


class Person:

    def __init__(
        self,
        position: City,
        state: PersonState,
        p_infection: float,
        p_staying: float,
        action_regulation: float,
        steps_for_onset: int,
        steps_for_recover: int,
    ) -> None:
        if not (0 <= p_infection <= 1):
            raise ValueError("'p_infection' must be in range [0, 1].")
        if not (0 <= p_staying <= 1):
            raise ValueError("'p_staying' must be in range [0, 1].")
        if not (0 <= action_regulation <= 1):
            raise ValueError("'action_regulation' must be in range [0, 1].")

        self._position = position
        self._state = state
        self._p_infection = p_infection
        self._p_staying = p_staying
        self._action_regulation = action_regulation
        self._steps_for_onset = steps_for_onset
        self._steps_for_recover = steps_for_recover

        self._next_state: t.Optional[PersonState] = None
        self._remaining_steps_for_onset: t.Optional[int] = None
        self._remaining_steps_for_recover: t.Optional[int] = None

    @property
    def position(self) -> City:
        return self._position

    def update_position(self) -> Person:
        next_cities = [self.position]
        next_cities.extend(self.position.current_visitables)
        num_next = len(next_cities)

        if num_next == 1:
            return self

        p_staying = self._p_staying
        weight_others = (1 - self._p_staying) / (num_next - 1)
        if self.state == PersonState.I:
            weight_others = self._action_regulation * weight_others
            p_staying = 1 - (num_next - 1) * weight_others

        weights = [p_staying]
        weights.extend([weight_others for _ in range(num_next - 1)])

        next_city = random.choices(next_cities, weights=weights)[0]
        self._position = next_city
        return self

    @property
    def state(self) -> PersonState:
        return self._state

    @property
    def remaining_steps_for_onset(self) -> t.Optional[int]:
        return self._remaining_steps_for_onset

    @property
    def remaining_steps_for_recover(self) -> t.Optional[int]:
        return self._remaining_steps_for_recover

    def eval_next_state(self, counts: CountsPeople_t) -> Person:
        # Taking self counting into account.
        counts[self.state] -= 1

        if self.state is PersonState.S:
            self._eval_next_state_when_S(counts)
        elif self.state is PersonState.E:
            self._eval_next_state_when_E(counts)
        elif self.state is PersonState.I:
            self._eval_next_state_when_I(counts)
        else:
            self._eval_next_state_when_R(counts)

        return self

    def _eval_next_state_when_S(self, counts_others: CountsPeople_t) -> None:
        if counts_others[PersonState.I] > 0:
            possible_states = (PersonState.S, PersonState.E)
            weights = (1 - self._p_infection, self._p_infection)
            self._next_state = random.choices(possible_states, weights)[0]

            if self._next_state is PersonState.E:
                self._remaining_steps_for_onset = self._steps_for_onset
        else:
            self._next_state = PersonState.S

    def _eval_next_state_when_E(self, counts_others: CountsPeople_t) -> None:
        self._remaining_steps_for_onset -= 1
        if self._remaining_steps_for_onset <= 0:
            self._next_state = PersonState.I
            self._remaining_steps_for_onset = None
            self._remaining_steps_for_recover = self._steps_for_recover
        else:
            self._next_state = PersonState.E

    def _eval_next_state_when_I(self, counts_others: CountsPeople_t) -> None:
        self._remaining_steps_for_recover -= 1
        if self._remaining_steps_for_recover <= 0:
            self._next_state = PersonState.R
            self._remaining_steps_for_recover = None
        else:
            self._next_state = PersonState.I

    def _eval_next_state_when_R(self, counts_others: CountsPeople_t) -> None:
        self._next_state = PersonState.R

    def update_state(self) -> Person:
        if self._next_state is None:
            raise ValueError("The next state has not been evaluated yet.")

        self._state = self._next_state
        self._next_state = None
        return self


class PopulationDependentPerson(Person):

    def _eval_next_state_when_S(self, counts_others: CountsPeople_t) -> None:
        num_infected = counts_others[PersonState.I]
        possible_states = (PersonState.S, PersonState.E)
        weight_for_S = (1 - self._p_infection)**num_infected
        weights = (weight_for_S, 1 - weight_for_S)
        self._next_state = random.choices(possible_states, weights)[0]
