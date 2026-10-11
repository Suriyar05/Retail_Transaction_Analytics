import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the transformed retail transaction data.
    """

    result = df.copy()

    # 1. Remove exact duplicate records
    result = result.drop_duplicates()

    # 2. Remove records with invalid negative prices
    result = result[result["unit_price"] >= 0]

    # 3. Keep missing customer IDs
    # Customer ID is not required for transaction-level analysis.
    # Do not remove these records.

    # 4. Keep missing descriptions
    # Description can potentially be recovered/handled later
    # using product-level information.

    # 5. Recalculate transaction value after cleaning
    result["transaction_value"] = (
        result["quantity"] * result["unit_price"]
    )

    # Reset index
    result = result.reset_index(drop=True)

    return result