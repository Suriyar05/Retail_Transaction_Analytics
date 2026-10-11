from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.auth import get_current_user, require_admin
from src.api.auth import get_current_user, require_admin

router = APIRouter(
    prefix="/api/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
)


# ============================================================
# GET /api/products
# ============================================================

@router.get("")
def get_products(
    search: Optional[str] = Query(
        default=None,
        description="Search by stock code or product description"
    ),
    sort_by: str = Query(
        default="revenue",
        pattern="^(revenue|quantity)$"
    ),
    order: str = Query(
        default="desc",
        pattern="^(asc|desc)$"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size

    order_column = (
        "total_revenue"
        if sort_by == "revenue"
        else "total_quantity"
    )

    order_direction = "DESC" if order == "desc" else "ASC"

    count_query = text("""
        SELECT COUNT(*)
        FROM products p
        WHERE
            :search IS NULL
            OR p.stock_code LIKE CONCAT('%', :search, '%')
            OR p.description LIKE CONCAT('%', :search, '%')
    """)

    total = db.execute(
        count_query,
        {"search": search}
    ).scalar()

    query = text(f"""
        SELECT
            p.stock_code,
            p.description,
            p.is_active,
            COALESCE(SUM(t.quantity), 0) AS total_quantity,
            COALESCE(SUM(t.transaction_value), 0) AS total_revenue
        FROM products p
        LEFT JOIN transactions t
            ON p.stock_code = t.stock_code
        WHERE
            :search IS NULL
            OR p.stock_code LIKE CONCAT('%', :search, '%')
            OR p.description LIKE CONCAT('%', :search, '%')
        GROUP BY
            p.stock_code,
            p.description,
            p.is_active
        ORDER BY {order_column} {order_direction}
        LIMIT :page_size OFFSET :offset
    """)

    results = db.execute(
        query,
        {
            "search": search,
            "page_size": page_size,
            "offset": offset
        }
    ).mappings().all()

    return {
        "page": page,
        "page_size": page_size,
        "total_products": total,
        "data": [
            {
                "stock_code": row["stock_code"],
                "description": row["description"],
                "is_active": bool(row["is_active"]),
                "total_quantity": row["total_quantity"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }


# ============================================================
# GET /api/products/{stock_code}
# ============================================================

@router.get("/{stock_code}")
def get_product(
    stock_code: str,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            p.stock_code,
            p.description,
            p.is_active,
            COALESCE(SUM(t.quantity), 0) AS total_quantity,
            COALESCE(SUM(t.transaction_value), 0) AS total_revenue,
            COUNT(DISTINCT t.invoice_no) AS total_orders
        FROM products p
        LEFT JOIN transactions t
            ON p.stock_code = t.stock_code
        WHERE p.stock_code = :stock_code
        GROUP BY
            p.stock_code,
            p.description,
            p.is_active
    """)

    result = db.execute(
        query,
        {"stock_code": stock_code}
    ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product {stock_code} not found"
        )

    return {
        "stock_code": result["stock_code"],
        "description": result["description"],
        "is_active": bool(result["is_active"]),
        "total_quantity": result["total_quantity"],
        "total_revenue": float(result["total_revenue"]),
        "total_orders": result["total_orders"]
    }


# ============================================================
# POST /api/products
# ============================================================

@router.post("")
def create_product(
    stock_code: str,
    description: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    stock_code = stock_code.strip()

    if not stock_code:
        raise HTTPException(
            status_code=400,
            detail="stock_code cannot be empty"
        )

    existing = db.execute(
        text("""
            SELECT stock_code
            FROM products
            WHERE stock_code = :stock_code
        """),
        {"stock_code": stock_code}
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Product {stock_code} already exists"
        )

    db.execute(
        text("""
            INSERT INTO products (
                stock_code,
                description
            )
            VALUES (
                :stock_code,
                :description
            )
        """),
        {
            "stock_code": stock_code,
            "description": description
        }
    )

    db.commit()

    return {
        "message": "Product created successfully",
        "stock_code": stock_code,
        "description": description
    }


# ============================================================
# PUT /api/products/{stock_code}
# ============================================================

@router.put("/{stock_code}")
def update_product(
    stock_code: str,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.execute(
        text("""
            SELECT stock_code
            FROM products
            WHERE stock_code = :stock_code
        """),
        {"stock_code": stock_code}
    ).first()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product {stock_code} not found"
        )

    db.execute(
        text("""
            UPDATE products
            SET
                description = COALESCE(:description, description),
                is_active = COALESCE(:is_active, is_active)
            WHERE stock_code = :stock_code
        """),
        {
            "stock_code": stock_code,
            "description": description,
            "is_active": is_active
        }
    )

    db.commit()

    return {
        "message": "Product updated successfully",
        "stock_code": stock_code
    }


# ============================================================
# DELETE /api/products/{stock_code}
# ============================================================

@router.delete("/{stock_code}")
def delete_product(
    stock_code: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.execute(
        text("""
            SELECT stock_code
            FROM products
            WHERE stock_code = :stock_code
        """),
        {"stock_code": stock_code}
    ).first()

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product {stock_code} not found"
        )

    db.execute(
        text("""
            DELETE FROM products
            WHERE stock_code = :stock_code
        """),
        {"stock_code": stock_code}
    )

    db.commit()

    return {
        "message": "Product deleted successfully",
        "stock_code": stock_code
    }