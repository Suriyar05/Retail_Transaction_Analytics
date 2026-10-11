import pandas as pd
from sqlalchemy import text

from src.etl.pipeline_logger import (
    start_pipeline_run,
    complete_pipeline_run,
    fail_pipeline_run
)
from src.etl.extract import extract_data
from src.etl.validate import validate_data
from src.etl.transform import transform_data
from src.etl.data_quality import generate_quality_report
from src.etl.clean import clean_data
from src.etl.incremental import add_record_hash
from src.api.database import engine


INSERT_COLUMNS = [
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
    "is_negative_quantity",
    "record_hash",
]


def get_existing_hashes():
    query = text("""
        SELECT record_hash
        FROM transactions
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    return {
        row[0]
        for row in rows
    }


def insert_new_records(df: pd.DataFrame) -> int:

    if df.empty:
        return 0

    insert_sql = text("""
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
            is_negative_quantity,
            record_hash
        )
        VALUES (
            :invoice_no,
            :stock_code,
            :description,
            :quantity,
            :invoice_date,
            :unit_price,
            :customer_id,
            :country,
            :source_sheet,
            :transaction_value,
            :is_cancelled_invoice,
            :is_negative_quantity,
            :record_hash
        )
    """)

    records = df[INSERT_COLUMNS].to_dict(
        orient="records"
    )

    with engine.begin() as connection:
        connection.execute(insert_sql, records)

    return len(records)

def run_incremental_etl(file_path: str):

    print("\n========== INCREMENTAL ETL ==========")

    run_id = start_pipeline_run(
        "incremental_retail_etl"
    )

    try:

        # 1. Extract
        df = extract_data(file_path)

        records_read = len(df)

        print(
            f"Extracted records: {records_read}"
        )

        # 2. Validate
        validate_data(df)

        print("Validation completed.")

        # 3. Transform
        df = transform_data(df)

        print("Transformation completed.")

        # 4. Quality report
        quality_report = generate_quality_report(df)

        print(
            f"Duplicate records in input: "
            f"{quality_report['duplicate_records']}"
        )

        # 5. Clean
        df = clean_data(df)

        print(
            f"Records after cleaning: {len(df)}"
        )

        # 6. Generate hashes
        df = add_record_hash(df)

        # 7. Remove duplicates inside incoming file
        df = df.drop_duplicates(
            subset=["record_hash"]
        ).reset_index(drop=True)

        print(
            f"Unique records in incoming file: "
            f"{len(df)}"
        )

        # 8. Get existing database hashes
        existing_hashes = get_existing_hashes()

        print(
            f"Existing database records: "
            f"{len(existing_hashes)}"
        )

        # 9. Keep only new records
        new_records = df[
            ~df["record_hash"].isin(existing_hashes)
        ].copy()

        print(
            f"New records to insert: "
            f"{len(new_records)}"
        )

        # 10. Insert new records
        inserted_count = insert_new_records(
            new_records
        )

        print(
            f"Inserted records: {inserted_count}"
        )

        # 11. Log successful pipeline
        complete_pipeline_run(
            run_id=run_id,
            records_read=records_read,
            records_inserted=inserted_count,
            records_rejected=0
        )

        print(
            f"Pipeline run {run_id} completed successfully."
        )

        print(
            "Incremental ETL completed."
        )

        return inserted_count

    except Exception as error:

        # Log failed pipeline
        fail_pipeline_run(
            run_id=run_id,
            error_message=str(error)
        )

        print(
            f"Pipeline run {run_id} failed."
        )

        raise
    
if __name__ == "__main__":

    FILE_PATH = "data/raw/Online_Retail_II.xlsx"

    run_incremental_etl(FILE_PATH)