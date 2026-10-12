import pytest

from app import create_app, db


@pytest.fixture()
def client():
    app = create_app("sqlite:///:memory:")
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()


def make(client, **body):
    return client.post("/items", json={"name": "Widget", "description": "A thing", **body})


def test_create_returns_201_and_item(client):
    r = make(client)
    assert r.status_code == 201
    assert r.json["id"] == 1 and r.json["name"] == "Widget" and r.json["description"] == "A thing"


def test_create_requires_name(client):
    r = client.post("/items", json={"description": "no name"})
    assert r.status_code == 400 and "name" in r.json["error"]


def test_create_rejects_non_json_and_unknown_fields(client):
    assert client.post("/items", data="oops", content_type="text/plain").status_code == 400
    assert make(client, price=5).status_code == 400


def test_list_and_get(client):
    make(client); make(client, name="Gadget")
    assert [i["name"] for i in client.get("/items").json] == ["Widget", "Gadget"]
    assert client.get("/items/2").json["name"] == "Gadget"


def test_get_missing_is_404(client):
    r = client.get("/items/99")
    assert r.status_code == 404 and r.json["error"] == "Item 99 not found."


def test_update_partial(client):
    make(client)
    r = client.put("/items/1", json={"description": "Updated"})
    assert r.status_code == 200 and r.json["name"] == "Widget" and r.json["description"] == "Updated"


def test_update_validation_and_404(client):
    make(client)
    assert client.put("/items/1", json={}).status_code == 400
    assert client.put("/items/1", json={"name": "  "}).status_code == 400
    assert client.put("/items/42", json={"name": "x"}).status_code == 404


def test_delete(client):
    make(client)
    assert client.delete("/items/1").status_code == 204
    assert client.get("/items/1").status_code == 404
    assert client.delete("/items/1").status_code == 404
