"""Remembered pay answers.

Answers change only when pay changes, so each (grouping, filters) answer is
kept in memory until the next pay write. Measured on the free host: the
summary took ~1 s of CPU there against 57 ms locally; this removes it from
every repeat view. One process, one dict; a second process would need a
shared cache, which is the change noted in docs/performance.md.
"""

_answers: dict[tuple, dict] = {}


def remembered(key: tuple) -> dict | None:
    return _answers.get(key)


def remember(key: tuple, answer: dict) -> dict:
    _answers[key] = answer
    return answer


def forget_answers() -> None:
    """Call after any pay write; the next request recomputes."""
    _answers.clear()
