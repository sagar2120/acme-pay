"""Plain-English questions. The language model only picks filters; every number comes from SQL."""

import pytest
from fastapi.testclient import TestClient

from app.ask import Interpretation, interpret_with_gemini
from app.main import create_app


def fake_interpreter(answer: Interpretation):
    def interpret(question: str, options: dict) -> Interpretation:
        return answer

    return interpret


@pytest.fixture
def ask(session_factory, asha):
    def _ask(question: str, interpretation: Interpretation):
        app = create_app(session_factory, interpreter=fake_interpreter(interpretation))
        return TestClient(app).post("/api/pay/ask", json={"question": question})

    return _ask


def test_the_answer_comes_from_the_database_using_the_filters_the_model_picked(ask, session, asha):
    from datetime import date
    from decimal import Decimal

    from app.pay import record_pay_change

    record_pay_change(session, asha.id, Decimal("1800000"), date(2022, 4, 1))
    picked = Interpretation(group_by="level", location="Pune", department=None, level=None)

    response = ask("what do we pay in Pune by level?", picked)

    body = response.json()
    assert response.status_code == 200
    assert body["filters"] == {
        "group_by": "level",
        "location_id": 1,
        "department_id": None,
        "level": None,
        "location_name": "Pune",
        "department_name": None,
    }
    assert body["summary"]["groups"][0] == {
        "name": "L3",
        "headcount": 1,
        "payroll_usd": "21600.00",
        "min_usd": "21600.00",
        "p25_usd": "21600.00",
        "median_usd": "21600.00",
        "p75_usd": "21600.00",
        "max_usd": "21600.00",
    }


def test_a_place_the_company_does_not_have_is_refused_not_guessed(ask, asha):
    picked = Interpretation(group_by="location", location="Mumbai", department=None, level=None)

    response = ask("pay in Mumbai", picked)

    assert response.status_code == 422
    assert "Mumbai" in response.json()["detail"]


def test_a_question_that_is_not_about_pay_is_refused(ask, asha):
    picked = Interpretation(group_by=None, location=None, department=None, level=None, unclear=True)

    response = ask("what is the weather", picked)

    assert response.status_code == 422


def test_questions_are_length_limited(ask, asha):
    picked = Interpretation(group_by="location", location=None, department=None, level=None)

    assert ask("x" * 501, picked).status_code == 422


def test_without_a_key_the_feature_says_so_instead_of_failing(session_factory, asha, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(create_app(session_factory))

    response = client.post("/api/pay/ask", json={"question": "pay in Pune"})

    assert response.status_code == 503
    assert "not set up" in response.json()["detail"]


def test_without_a_chosen_model_gemini_3_6_flash_is_asked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    asked = {}

    class Reply:
        def raise_for_status(self):
            pass

        def json(self):
            picked = '{"group_by": "level", "unclear": false}'
            return {"candidates": [{"content": {"parts": [{"text": picked}]}}]}

    def fake_post(url, **kwargs):
        asked["url"] = url
        return Reply()

    monkeypatch.setattr("app.ask.httpx.post", fake_post)
    options = {"locations": ["Pune"], "departments": ["Engineering"], "levels": ["L3"]}

    interpret_with_gemini("what do we pay in Pune by level", options)

    assert "/models/gemini-3.6-flash:generateContent" in asked["url"]


def test_the_real_interpreter_is_the_default(session_factory):
    app = create_app(session_factory)

    assert app.state.interpreter is interpret_with_gemini
