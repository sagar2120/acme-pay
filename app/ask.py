"""Plain-English pay questions.

The language model does one narrow job: turn the question into filters we
already support (group by what, which location, department, level). It never
sees pay data and never produces a number. The database answers, as it does
for the filters on the page. If the model cannot map the question, or names a
place or team ACME does not have, the question is refused rather than guessed.
"""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass

import httpx

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.6-flash"
MAX_QUESTION_CHARS = 500


class AskNotSetUp(RuntimeError):
    pass


class QuestionNotUnderstood(ValueError):
    pass


@dataclass(frozen=True)
class Interpretation:
    group_by: str | None
    location: str | None
    department: str | None
    level: str | None
    unclear: bool = False


Interpreter = Callable[[str, dict], Interpretation]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "group_by": {"type": "string", "enum": ["location", "department", "level"]},
        "location": {"type": "string", "nullable": True},
        "department": {"type": "string", "nullable": True},
        "level": {"type": "string", "nullable": True},
        "unclear": {"type": "boolean"},
    },
    "required": ["group_by", "unclear"],
}


def interpret_with_gemini(question: str, options: dict) -> Interpretation:
    """Ask Gemini which of our filters the question maps to. Strict JSON out, nothing else."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise AskNotSetUp("Questions in plain English are not set up: GEMINI_API_KEY is missing.")
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    prompt = (
        "You translate an HR manager's question about pay into filters for a report. "
        "Pick group_by (how to break the answer down) and, only if the question names them, "
        "a location, department or level from these lists; use null otherwise.\n"
        f"Locations: {', '.join(options['locations'])}\n"
        f"Departments: {', '.join(options['departments'])}\n"
        f"Levels: {', '.join(options['levels'])}\n"
        "Set unclear=true if the question is not about pay at ACME or cannot be mapped. "
        "Never invent a name that is not in the lists.\n"
        f"Question: {question}"
    )
    response = httpx.post(
        GEMINI_URL.format(model=model),
        params={"key": key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "responseSchema": RESPONSE_SCHEMA,
            },
        },
        timeout=15,
    )
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    picked = json.loads(text)
    return Interpretation(
        group_by=picked.get("group_by"),
        location=picked.get("location") or None,
        department=picked.get("department") or None,
        level=picked.get("level") or None,
        unclear=bool(picked.get("unclear")),
    )


def filters_from(picked: Interpretation, options: dict, question: str = "") -> dict:
    """Turn names the model picked into the ids the summary needs; refuse anything unknown.

    A name the HR manager actually typed wins over the model's pick: the model
    may fill in what the question leaves open, never contradict what it says.
    """
    picked = _as_written(question, picked, options)
    if picked.unclear or picked.group_by not in ("location", "department", "level"):
        raise QuestionNotUnderstood(
            "I can only answer questions about ACME pay by location, department or level. "
            "Try: what do we pay senior engineers in Pune?"
        )
    return {
        "group_by": picked.group_by,
        "location_id": _id_for(picked.location, options["locations"], "location"),
        "department_id": _id_for(picked.department, options["departments"], "department"),
        "level": _level(picked.level, options["levels"]),
    }


def _id_for(name: str | None, known: dict[str, int], kind: str) -> int | None:
    if name is None:
        return None
    for known_name, id_ in known.items():
        if known_name.lower() == name.lower():
            return id_
    raise QuestionNotUnderstood(f"ACME has no {kind} called {name}. Known: {', '.join(known)}.")


def _level(level: str | None, known: list[str]) -> str | None:
    if level is None:
        return None
    if level.upper() in known:
        return level.upper()
    raise QuestionNotUnderstood(f"Levels are {', '.join(known)}; {level} is not one of them.")


def _as_written(question: str, picked: Interpretation, options: dict) -> Interpretation:
    words = f" {question.lower()} "
    location = _only_one_named(words, options["locations"]) or picked.location
    department = _only_one_named(words, options["departments"]) or picked.department
    level = _only_one_named(words, options["levels"]) or picked.level
    unclear = picked.unclear and not (location or department or level)
    return Interpretation(picked.group_by or "location", location, department, level, unclear)


def _only_one_named(words: str, known) -> str | None:
    named = [name for name in known if f" {name.lower()} " in words or f" {name.lower()}," in words]
    return named[0] if len(named) == 1 else None
