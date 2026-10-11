from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date
from fastapi import Query
from fastapi import Depends, HTTPException
from sqlalchemy import text
from src.api.database import get_db


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


# ============================================================
# 1. Overall KPI Summary
# ============================================================
@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):

    query = text("""
        SELECT
            COUNT(*) AS transaction_records,
            COUNT(DISTINCT invoice_no) AS unique_invoices,
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(DISTINCT stock_code) AS unique_products,
            COUNT(DISTINCT country) AS unique_countries,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue,
            ROUND(
                SUM(transaction_value)
                / NULLIF(COUNT(DISTINCT invoice_no), 0),
                2
            ) AS average_order_value
        FROM transactions
    """)

    result = db.execute(query).mappings().one()

    return {
        "transaction_records": result["transaction_records"],
        "unique_invoices": result["unique_invoices"],
        "unique_customers": result["unique_customers"],
        "unique_products": result["unique_products"],
        "unique_countries": result["unique_countries"],
        "total_quantity": result["total_quantity"],
        "total_revenue": float(result["total_revenue"] or 0),
        "average_order_value": float(
            result["average_order_value"] or 0
        )
    }
# ============================================================
# 2. Monthly Sales
# ============================================================

@router.get("/monthly-sales")
def get_monthly_sales(db: Session = Depends(get_db)):

    query = text("""
        SELECT
            DATE_FORMAT(invoice_date, '%Y-%m') AS month,
            COUNT(DISTINCT invoice_no) AS unique_invoices,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue
        FROM transactions
        GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
        ORDER BY month
    """)

    results = db.execute(query).mappings().all()

    return {
        "data": [
            {
                "month": row["month"],
                "unique_invoices": row["unique_invoices"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }


# ============================================================
# 3. Country Sales
# ============================================================

@router.get("/country-sales")
def get_country_sales(db: Session = Depends(get_db)):

    query = text("""
        SELECT
            country,
            COUNT(DISTINCT invoice_no) AS unique_invoices,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue
        FROM transactions
        GROUP BY country
        ORDER BY total_revenue DESC
    """)

    results = db.execute(query).mappings().all()

    return {
        "data": [
            {
                "country": row["country"],
                "unique_invoices": row["unique_invoices"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }


# ============================================================
# 4. Top Products
# ============================================================

@router.get("/top-products")
def get_top_products(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            t.stock_code,
            COALESCE(p.description, t.description) AS description,
            t.total_quantity,
            t.total_revenue
        FROM (
            SELECT
                stock_code,
                MAX(description) AS description,
                SUM(quantity) AS total_quantity,
                SUM(transaction_value) AS total_revenue
            FROM transactions
            GROUP BY stock_code
        ) t
        LEFT JOIN products p
            ON p.stock_code = t.stock_code
        ORDER BY t.total_revenue DESC, t.stock_code ASC
        LIMIT :limit
    """)

    results = db.execute(
        query,
        {"limit": limit}
    ).mappings().all()

    return {
        "data": [
            {
                "stock_code": row["stock_code"],
                "description": row["description"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"] or 0)
            }
            for row in results
        ]
    }

@router.get("/date-range")
def get_date_range_sales(
    start_date: date = Query(
        ...,
        description="Start date in YYYY-MM-DD format"
    ),
    end_date: date = Query(
        ...,
        description="End date in YYYY-MM-DD format"
    ),
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        return {
            "error": "start_date must be earlier than or equal to end_date"
        }

    query = text("""
        SELECT
            COUNT(*) AS transaction_records,
            COUNT(DISTINCT invoice_no) AS unique_invoices,
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(DISTINCT stock_code) AS unique_products,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue,
            ROUND(
                SUM(transaction_value)
                / NULLIF(COUNT(DISTINCT invoice_no), 0),
                2
            ) AS average_order_value
        FROM transactions
        WHERE invoice_date >= :start_date
          AND invoice_date < DATE_ADD(:end_date, INTERVAL 1 DAY)
    """)

    result = db.execute(
        query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().one()

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "transaction_records": result["transaction_records"],
        "unique_invoices": result["unique_invoices"],
        "unique_customers": result["unique_customers"],
        "unique_products": result["unique_products"],
        "total_quantity": result["total_quantity"],
        "total_revenue": float(result["total_revenue"] or 0),
        "average_order_value": float(
            result["average_order_value"] or 0
        )
    }