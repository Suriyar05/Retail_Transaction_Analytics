from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_get_products():
    response = client.get(
        "/api/products",
        params={
            "page": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert "total_products" in data
    assert "data" in data

    assert len(data["data"]) <= 10


def test_product_search():
    response = client.get(
        "/api/products",
        params={
            "search": "bag",
            "page": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data

    for product in data["data"]:
        stock_code = str(product["stock_code"]).lower()
        description = str(product["description"]).lower()

        assert (
            "bag" in stock_code
            or "bag" in description
        )


def test_product_sorting():
    response = client.get(
        "/api/products",
        params={
            "sort_by": "revenue",
            "order": "desc",
            "page": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    revenues = [
        product["total_revenue"]
        for product in data["data"]
    ]

    assert revenues == sorted(
        revenues,
        reverse=True
    )


def test_product_pagination():
    response = client.get(
        "/api/products",
        params={
            "page": 1,
            "page_size": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["data"]) <= 5


def test_get_existing_product():
    response = client.get("/api/products/85099B")

    assert response.status_code == 200

    data = response.json()

    assert data["stock_code"] == "85099B"
    assert "description" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "total_orders" in data


def test_product_not_found():
    response = client.get(
        "/api/products/DOES_NOT_EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data


def test_invalid_page():
    response = client.get(
        "/api/products",
        params={
            "page": 0
        }
    )

    assert response.status_code == 422


def test_invalid_page_size():
    response = client.get(
        "/api/products",
        params={
            "page_size": 500
        }
    )

    assert response.status_code == 422


def test_invalid_sort():
    response = client.get(
        "/api/products",
        params={
            "sort_by": "invalid"
        }
    )

    assert response.status_code == 422