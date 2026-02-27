from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    bank_accounts_router,
    bank_transactions_router,
    businesses_router,
    coa_router,
    health_router,
    matches_router,
    pdf_uploads_router,
    reconciliation_router,
    register_router,
    reports_router,
    seed_router,
)
from app.settings import settings

app = FastAPI(title=settings.app_name)

allow_origins = [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]
if allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(businesses_router)
app.include_router(coa_router)
app.include_router(bank_accounts_router)
app.include_router(pdf_uploads_router)
app.include_router(bank_transactions_router)
app.include_router(register_router)
app.include_router(matches_router)
app.include_router(reconciliation_router)
app.include_router(reports_router)
app.include_router(seed_router)
