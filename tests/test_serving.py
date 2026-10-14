from fastapi.testclient import TestClient

from app.main import create_app


def test_the_screens_are_served_for_any_address_outside_the_api(tmp_path, session_factory):
    (tmp_path / "index.html").write_text("<title>ACME Pay</title>")
    (tmp_path / "assets").mkdir()
    client = TestClient(create_app(session_factory, static_dir=tmp_path))

    assert "ACME Pay" in client.get("/").text
    assert "ACME Pay" in client.get("/people?location_id=1").text
    assert client.get("/api/no-such-thing").status_code == 404


def test_on_start_an_empty_database_is_created_and_seeded(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'acme.db'}")

    with TestClient(create_app()) as client:
        total = client.get("/api/employees", params={"page_size": 1}).json()["total"]

    assert total > 9_000  # 10,000 seeded, minus the 3% who have left
