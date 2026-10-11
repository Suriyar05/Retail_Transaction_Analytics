import pandas as pd


SHEETS = [
    "Year 2009-2010",
    "Year 2010-2011"
]


def read_retail_data(file_path: str) -> pd.DataFrame:
    """
    Read both yearly sheets from the Online Retail II Excel file
    and combine them into a single DataFrame.
    """

    frames = []

    for sheet in SHEETS:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet
        )

        df["SourceSheet"] = sheet
        frames.append(df)

    combined_df = pd.concat(
        frames,
        ignore_index=True
    )

    return combined_df