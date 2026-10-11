
import time

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import get_current_user
from src.api.routes.auth import router as auth_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.products import router as products_router
from src.api.routes.customers import router as customers_router
from src.utils.logger import get_logger


logger = get_logger("retail_api")


app = FastAPI(
    title="Retail Transaction Analytics API",
    description="REST API for retail transaction analytics",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ============================================================
# ROUTE REGISTRATION
# ============================================================

# Login and current-user endpoints remain publicly accessible
# as appropriate to their own endpoint dependencies.
app.include_router(auth_router)

# All analytics endpoints require authentication.
app.include_router(
    analytics_router,
    dependencies=[Depends(get_current_user)],
)

# All customer endpoints require authentication.
app.include_router(
    customers_router,
    dependencies=[Depends(get_current_user)],
)

# Product routes enforce authentication in products.py.
# Product mutations additionally require the admin role.
app.include_router(products_router)


# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            "%s %s -> %s (%.4f seconds)",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response

    except Exception as error:
        process_time = time.time() - start_time

        logger.exception(
            "%s %s -> ERROR (%.4f seconds): %s",
            request.method,
            request.url.path,
            process_time,
            error,
        )

        raise


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Retail Transaction Analytics API is running"
    }


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred.",
        },
    )
