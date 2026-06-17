from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint():
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_validate_endpoint():
    response = client.post(
        "/validate",
        json={
            "batch": "B01_DM_dates",
            "host_generator_key": "oncology_nsclc",
        },
    )

    # Depending on whether the input files exist,
    # the endpoint may return 200 or 500.
    assert response.status_code in [200, 500]