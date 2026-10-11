from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_get_customers():
    response = client.get(
        "/api/customers",
        params={
            "page": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert "total_customers" in data
    assert "data" in data

    assert len(data["data"]) <= 10


def test_get_top_customers():
    response = client.get(
        "/api/customers/top",
        params={
            "limit": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 10
    assert "data" in data
    assert len(data["data"]) <= 10

    if data["data"]:
        customer = data["data"][0]

        assert "customer_id" in customer
        assert "total_orders" in customer
        assert "total_quantity" in customer
        assert "total_revenue" in customer


def test_get_existing_customer():
    response = client.get(
        "/api/customers/14646"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == 14646
    assert "total_orders" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "first_purchase" in data
    assert "last_purchase" in data


def test_customer_not_found():
    response = client.get(
        "/api/customers/999999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data


def test_customer_pagination_validation():
    response = client.get(
        "/api/customers",
        params={
            "page": 0
        }
    )

    assert response.status_code == 422