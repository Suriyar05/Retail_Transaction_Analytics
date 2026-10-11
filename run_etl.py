from src.etl.pipeline import run_pipeline


FILE_PATH = "data/raw/Online_Retail_II.xlsx"
OUTPUT_PATH ="data/processed/cleaned_retail.parquet"

df = run_pipeline(FILE_PATH)

df.to_parquet(
    OUTPUT_PATH,
    index=False
)

print("\nProcessed dataset saved successfully.")
print(f"path :{OUTPUT_PATH}")

print("\nFinal shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head())