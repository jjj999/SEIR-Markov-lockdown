from pathlib import Path

from ..city import City
from ..person import PersonState


def check_float(raw: str, file: Path | str, line: int) -> float:
    try:
        val = float(raw)
    except ValueError as e:
        raise ValueError(
            f"'{str(file)}' line {line}: could not convert string to "
            f"float: '{raw}'."
        ) from e
    return val


def check_prob(raw: str, file: Path | str, line: int) -> float:
    val = check_float(raw, file, line)
    if not (0 <= val <= 1):
        raise ValueError(
            f"'{str(file)}' line {line}: must be within [0, 1]: '{raw}'."
        )
    return val


def check_int(
    raw: str,
    file: Path | str,
    line: int,
    positive: bool = False,
) -> int:
    try:
        val = int(raw)
    except ValueError as e:
        raise ValueError(
            f"'{str(file)}' line {line}: could not convert string to "
            f"int: '{raw}'."
        ) from e

    if positive:
        if val < 1:
            raise ValueError(
                f"'{str(file)}' line {line}: a positive number expected: "
                f"'{raw}'."
            )

    return val


def check_nullable_int(
    raw: str,
    file: Path | str,
    line: int,
    positive: bool = False,
) -> float:
    if raw == "":
        return None
    return check_int(raw, file, line, positive=positive)


def check_city_def(
    city_name: str,
    cities: dict[str, City],
    file: Path | str,
    line: int,
) -> City:
    if city_name not in cities:
        raise ValueError(
                f"'{str(file)}' line {line}: city '{city_name}' is not "
                "defined."
            )
    return cities[city_name]


def check_state(state_name: str, file: Path | str, line: int) -> PersonState:
    if state_name not in PersonState.__members__.keys():
        raise ValueError(
            f"'{str(file)}' line {line}: state '{state_name}' is not defined."
        )
    return PersonState.__members__[state_name]
