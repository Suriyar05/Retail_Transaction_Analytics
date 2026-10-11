from sqlalchemy import text

from src.api.database import engine


try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT COUNT(*) FROM transactions")
        )

        count = result.scalar()

        print("Database connection successful.")
        print(f"Transactions in database: {count}")

except Exception as error:
    print("Database connection failed.")
    print(error) 