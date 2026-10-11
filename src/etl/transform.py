import pandas as pd


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic transformations on the retail dataset.
    """

    result = df.copy()

    # Standardize column names
    result = result.rename(
        columns={
            "Invoice": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "Price": "unit_price",
            "Customer ID": "customer_id",
            "Country": "country",
            "SourceSheet": "source_sheet"
        }
    )

    # Invoice numbers can contain numeric values and values
    # with prefixes such as 'C', so store them as strings.
    result["invoice_no"] = (
        result["invoice_no"]
        .astype("string")
        .str.strip()
    )

    # Standardize stock code
    result["stock_code"] = (
        result["stock_code"]
        .astype("string")
        .str.strip()
    )

    # Standardize description
    result["description"] = (
        result["description"]
        .astype("string")
        .str.strip()
    )

    # Ensure date type
    result["invoice_date"] = pd.to_datetime(
        result["invoice_date"],
        errors="coerce"
    )

    # Calculate transaction value
    result["transaction_value"] = (
        result["quantity"] * result["unit_price"]
    )

    # Identify invoices starting with C
    result["is_cancelled_invoice"] = (
        result["invoice_no"]
        .str.startswith("C", na=False)
    )

    # Identify negative quantity
    result["is_negative_quantity"] = (
        result["quantity"] < 0
    )

    return result