# GET /api/customers
# GET /api/customers/top
# GET /api/customers/{customer_id}

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.database import get_db


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"]
)


# GET /api/customers
@router.get("")
def get_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size

    count_query = text("""
        SELECT COUNT(*)
        FROM (
            SELECT customer_id
            FROM transactions
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        ) AS customers
    """)

    total_customers = db.execute(count_query).scalar()

    query = text("""
        SELECT
            customer_id,
            COUNT(DISTINCT invoice_no) AS total_orders,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue
        FROM transactions
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        ORDER BY total_revenue DESC
        LIMIT :page_size OFFSET :offset
    """)

    results = db.execute(
        query,
        {
            "page_size": page_size,
            "offset": offset
        }
    ).mappings().all()

    return {
        "page": page,
        "page_size": page_size,
        "total_customers": total_customers,
        "data": [
            {
                "customer_id": row["customer_id"],
                "total_orders": row["total_orders"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }


# GET /api/customers/top
@router.get("/top")
def get_top_customers(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            customer_id,
            COUNT(DISTINCT invoice_no) AS total_orders,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue
        FROM transactions
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        ORDER BY total_revenue DESC
        LIMIT :limit
    """)

    results = db.execute(
        query,
        {"limit": limit}
    ).mappings().all()

    return {
        "limit": limit,
        "data": [
            {
                "customer_id": row["customer_id"],
                "total_orders": row["total_orders"],
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }


# GET /api/customers/{customer_id}
@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            customer_id,
            COUNT(DISTINCT invoice_no) AS total_orders,
            SUM(quantity) AS total_quantity,
            SUM(transaction_value) AS total_revenue,
            MIN(invoice_date) AS first_purchase,
            MAX(invoice_date) AS last_purchase
        FROM transactions
        WHERE customer_id = :customer_id
        GROUP BY customer_id
    """)

    result = db.execute(
        query,
        {"customer_id": customer_id}
    ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found"
        )

    return {
        "customer_id": result["customer_id"],
        "total_orders": result["total_orders"],
        "total_quantity": result["total_quantity"],
        "total_revenue": float(result["total_revenue"]),
        "first_purchase": result["first_purchase"],
        "last_purchase": result["last_purchase"]
    }