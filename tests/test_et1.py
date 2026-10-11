import pandas as pd
import pytest

from src.etl.validate import validate_data
from src.etl.transform import transform_data
from src.etl.clean import clean_data
from src.etl.data_quality import generate_quality_report


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Invoice": ["10001", "10002", "10002", "10003"],
        "StockCode": ["A001", "A002", "A002", "A003"],
        "Description": [
            "Product A",
            "Product B",
            "Product B",
            "Product C"
        ],
        "Quantity": [2, 3, 3, -1],
        "InvoiceDate": pd.to_datetime([
            "2010-01-01 10:00:00",
            "2010-01-02 11:00:00",
            "2010-01-02 11:00:00",
            "2010-01-03 12:00:00"
        ]),
        "Price": [10.0, 20.0, 20.0, 5.0],
        "Customer ID": [101, 102, 102, 103],
        "Country": ["United Kingdom"] * 4,
        "SourceSheet": ["Test Sheet"] * 4
    })


def test_validate_data(sample_data):
    validate_data(sample_data)


def test_transform_data(sample_data):
    transformed = transform_data(sample_data)

    expected_columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
        "source_sheet",
        "transaction_value",
        "is_cancelled_invoice",
        "is_negative_quantity"
    ]

    for column in expected_columns:
        assert column in transformed.columns

    assert transformed.loc[0, "transaction_value"] == 20.0
    assert transformed.loc[3, "is_negative_quantity"] == True


def test_data_quality_report(sample_data):
    transformed = transform_data(sample_data)

    report = generate_quality_report(transformed)

    assert report["total_records"] == 4
    assert report["duplicate_records"] == 1
    assert report["negative_quantity"] == 1
    assert report["zero_quantity"] == 0
    assert report["negative_price"] == 0


def test_clean_data(sample_data):
    transformed = transform_data(sample_data)

    cleaned = clean_data(transformed)

    # One exact duplicate should be removed
    assert len(cleaned) == 3

    # No negative prices should remain
    assert (cleaned["unit_price"] < 0).sum() == 0