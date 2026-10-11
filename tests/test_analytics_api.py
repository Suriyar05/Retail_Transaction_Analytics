from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Retail Transaction Analytics API is running"


def test_summary_endpoint():
    response = client.get("/api/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert "transaction_records" in data
    assert "unique_invoices" in data
    assert "unique_customers" in data
    assert "unique_products" in data
    assert "unique_countries" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "average_order_value" in data


def test_monthly_sales_endpoint():
    response = client.get("/api/analytics/monthly-sales")

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)

    if data["data"]:
        row = data["data"][0]

        assert "month" in row
        assert "unique_invoices" in row
        assert "total_quantity" in row
        assert "total_revenue" in row


def test_country_sales_endpoint():
    response = client.get("/api/analytics/country-sales")

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert isinstance(data["data"], list)

    if data["data"]:
        row = data["data"][0]

        assert "country" in row
        assert "unique_invoices" in row
        assert "total_quantity" in row
        assert "total_revenue" in row


def test_top_products_endpoint():
    response = client.get(
        "/api/analytics/top-products?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert len(data["data"]) <= 5

    if data["data"]:
        row = data["data"][0]

        assert "stock_code" in row
        assert "description" in row
        assert "total_quantity" in row
        assert "total_revenue" in row


def test_date_range_endpoint():
    response = client.get(
        "/api/analytics/date-range",
        params={
            "start_date": "2010-01-01",
            "end_date": "2010-03-31"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["start_date"] == "2010-01-01"
    assert data["end_date"] == "2010-03-31"

    assert "transaction_records" in data
    assert "unique_invoices" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "average_order_value" in data