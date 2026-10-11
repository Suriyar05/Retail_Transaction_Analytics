import pandas as pd
from sqlalchemy import text

from src.api.database import engine
from src.etl.incremental import add_record_hash


PARQUET_PATH = "data/processed/cleaned_retail.parquet"


def backfill_hashes():
    print("Loading processed Parquet file...")

    df = pd.read_parquet(PARQUET_PATH)

    print(f"Records loaded: {len(df)}")

    df = add_record_hash(df)

    print("Record hashes generated.")

    with engine.begin() as connection:

        update_sql = text("""
            UPDATE transactions
            SET record_hash = :record_hash
            WHERE transaction_id = :transaction_id
        """)

        transaction_ids = pd.read_sql(
            """
            SELECT transaction_id
            FROM transactions
            ORDER BY transaction_id
            """,
            connection
        )

        if len(transaction_ids) != len(df):
            raise ValueError(
                "Transaction count does not match Parquet record count."
            )

        batch = []

        for index, row in df.iterrows():

            batch.append({
                "transaction_id": int(
                    transaction_ids.iloc[index]["transaction_id"]
                ),
                "record_hash": row["record_hash"]
            })

            if len(batch) >= 5000:
                connection.execute(update_sql, batch)
                batch.clear()

        if batch:
            connection.execute(update_sql, batch)

    print("Existing transaction hashes updated successfully.")


if __name__ == "__main__":
    backfill_hashes()