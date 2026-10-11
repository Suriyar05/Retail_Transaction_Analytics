import hashlib
import pandas as pd


HASH_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "source_sheet",
]


def normalize_value(value):
    if pd.isna(value):
        return "<NULL>"

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return str(value).strip()


def generate_record_hash(row) -> str:
    values = [
        normalize_value(row[column])
        for column in HASH_COLUMNS
    ]

    record_string = "|".join(values)

    return hashlib.sha256(
        record_string.encode("utf-8")
    ).hexdigest()


def add_record_hash(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["record_hash"] = result.apply(
        generate_record_hash,
        axis=1
    )

    return result