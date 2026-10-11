import pandas as pd
import mysql.connector


PARQUET_PATH = "data/processed/cleaned_retail.parquet"


def load_parquet_to_mysql():
    print("Reading processed Parquet file...")

    df = pd.read_parquet(PARQUET_PATH)

    print(f"Records to load: {len(df)}")

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="retail_analytics"
    )

    cursor = connection.cursor()

    insert_query = """
        INSERT INTO transactions (
            invoice_no,
            stock_code,
            description,
            quantity,
            invoice_date,
            unit_price,
            customer_id,
            country,
            source_sheet,
            transaction_value,
            is_cancelled_invoice,
            is_negative_quantity
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """

    batch_size = 5000

    for start in range(0, len(df), batch_size):

        batch = df.iloc[start:start + batch_size]

        records = []

        for _, row in batch.iterrows():

            records.append((
                str(row["invoice_no"]),
                str(row["stock_code"]),
                None if pd.isna(row["description"])
                else str(row["description"]),

                int(row["quantity"]),

                row["invoice_date"].to_pydatetime(),

                float(row["unit_price"]),

                None if pd.isna(row["customer_id"])
                else int(row["customer_id"]),

                str(row["country"]),
                str(row["source_sheet"]),

                float(row["transaction_value"]),

                bool(row["is_cancelled_invoice"]),
                bool(row["is_negative_quantity"])
            ))

        cursor.executemany(insert_query, records)

        connection.commit()

        print(
            f"Loaded {min(start + batch_size, len(df))}"
            f"/{len(df)} records"
        )

    cursor.close()
    connection.close()

    print("\nData loading completed successfully.")


if __name__ == "__main__":
    load_parquet_to_mysql()