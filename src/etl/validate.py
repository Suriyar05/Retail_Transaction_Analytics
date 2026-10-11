import pandas as pd


REQUIRED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country"
]


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate that all required columns are present.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_data_types(df: pd.DataFrame) -> None:
    """
    Basic validation of important data types.
    """

    if not pd.api.types.is_numeric_dtype(df["Quantity"]):
        raise TypeError("Quantity must be numeric.")

    if not pd.api.types.is_numeric_dtype(df["Price"]):
        raise TypeError("Price must be numeric.")

    if not pd.api.types.is_datetime64_any_dtype(
        df["InvoiceDate"]
    ):
        raise TypeError("InvoiceDate must be datetime.")


def validate_data(df: pd.DataFrame) -> None:
    """
    Run all validation checks.
    """

    validate_columns(df)
    validate_data_types(df)