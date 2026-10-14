from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_reports_ok():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recording_a_pay_change_returns_the_new_record(client, asha):
    response = client.post(
        f"/api/employees/{asha.id}/pay",
        json={"amount": "1800000", "effective_from": "2022-04-01", "note": "Promotion"},
    )

    assert response.status_code == 201
    body = response.json()
    assert (body["currency"], body["amount_usd"], body["note"]) == ("INR", "21600.00", "Promotion")


def test_pay_change_for_an_unknown_employee_is_404(client):
    response = client.post(
        "/api/employees/ACME-2021-99999/pay",
        json={"amount": "1800000", "effective_from": "2022-04-01"},
    )

    assert response.status_code == 404


def test_pay_change_that_breaks_a_rule_is_422_with_the_reason(client, asha):
    response = client.post(
        f"/api/employees/{asha.id}/pay", json={"amount": "1800000", "effective_from": "2021-02-28"}
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Pay change on 2021-02-28 is before hire date 2021-03-01"


def test_second_pay_change_on_the_same_day_is_409(client, asha):
    body = {"amount": "1800000", "effective_from": "2022-04-01"}
    client.post(f"/api/employees/{asha.id}/pay", json=body)

    response = client.post(f"/api/employees/{asha.id}/pay", json=body)

    assert response.status_code == 409


def test_filter_options_list_locations_departments_and_levels(client, asha):
    body = client.get("/api/options").json()

    assert body["locations"] == [{"id": 1, "name": "Pune"}]
    assert body["departments"] == [{"id": 1, "name": "Engineering"}]
    assert body["levels"] == ["L1", "L2", "L3", "L4", "L5", "L6"]


def test_every_response_carries_basic_browser_security_headers(client):
    headers = client.get("/api/health").headers

    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "same-origin"


def test_search_text_is_length_limited(client, asha):
    assert client.get("/api/employees", params={"q": "a" * 101}).status_code == 422


def test_an_absurd_pay_amount_is_refused(client, asha):
    response = client.post(
        f"/api/employees/{asha.id}/pay",
        json={"amount": "100000000000", "effective_from": "2022-04-01"},
    )

    assert response.status_code == 422
