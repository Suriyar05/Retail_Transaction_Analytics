import pandas as pd


def generate_quality_report(df: pd.DataFrame) -> dict:
    """
    Generate a data-quality report for the retail dataset.
    """

    report = {}

    # Total records
    report["total_records"] = len(df)

    # Missing values
    report["missing_values"] = (
        df.isnull()
        .sum()
        .to_dict()
    )

    # Duplicate records
    report["duplicate_records"] = int(
        df.duplicated().sum()
    )

    # Negative quantity
    report["negative_quantity"] = int(
        (df["quantity"] < 0).sum()
    )

    # Zero quantity
    report["zero_quantity"] = int(
        (df["quantity"] == 0).sum()
    )

    # Negative price
    report["negative_price"] = int(
        (df["unit_price"] < 0).sum()
    )

    # Zero price
    report["zero_price"] = int(
        (df["unit_price"] == 0).sum()
    )

    # Invalid dates
    report["invalid_dates"] = int(
        df["invoice_date"].isna().sum()
    )

    return report


def print_quality_report(report: dict) -> None:
    """
    Display the data-quality report.
    """

    print("\n========== DATA QUALITY REPORT ==========")

    print(
        f"Total Records: "
        f"{report['total_records']}"
    )

    print(
        f"Duplicate Records: "
        f"{report['duplicate_records']}"
    )

    print(
        f"Negative Quantity: "
        f"{report['negative_quantity']}"
    )

    print(
        f"Zero Quantity: "
        f"{report['zero_quantity']}"
    )

    print(
        f"Negative Price: "
        f"{report['negative_price']}"
    )

    print(
        f"Zero Price: "
        f"{report['zero_price']}"
    )

    print(
        f"Invalid Dates: "
        f"{report['invalid_dates']}"
    )

    print("\nMissing Values:")

    for column, count in report["missing_values"].items():
        print(f"{column}: {count}")

    print("==========================================")