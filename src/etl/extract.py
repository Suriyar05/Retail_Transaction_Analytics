from src.ingestion.reader import read_retail_data


def extract_data(file_path: str):
    """
    Extract raw retail transaction data from the Excel workbook.
    """
    return read_retail_data(file_path)