from src.etl.extract import extract_data
from src.etl.validate import validate_data
from src.etl.transform import transform_data
from src.etl.data_quality import (generate_quality_report,print_quality_report)
from src.etl.clean import clean_data

def run_pipeline(file_path: str):

    print("Starting ETL pipeline...")

    # Extract
    df = extract_data(file_path)
    print(f"Extracted records: {len(df)}")

    # Validate
    validate_data(df)
    print("Validation completed.")

    # Transform
    df = transform_data(df)
    print("Transformation completed.")

    # data Quality
    quality_report=generate_quality_report(df)
    print_quality_report(quality_report)

    # clean 
    df=clean_data(df)
    print(f"\nRecords after cleaning")
    return df