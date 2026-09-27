from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.stores import router as stores_router
from backend.app.routes.sales import router as sales_router
from backend.app.routes.products import router as products_router
from backend.app.routes.customers import router as customers_router
from backend.app.routes.inventory import router as inventory_router
from backend.app.routes.anomalies import router as anomalies_router

from backend.app.routes.daily_store_metrics import router as daily_store_metrics_router
from backend.app.routes.product_performance import router as product_performance_router
from backend.app.routes.customer_metrics import router as customer_metrics_router
from backend.app.routes.inventory_metrics import router as inventory_metrics_router

from backend.app.routes.finance import router as finance_router
from backend.app.routes.finance_analytics import router as finance_analytics_router
from backend.app.routes.auth import router as auth_router
from backend.app.routes.ai import router as ai_router


app = FastAPI(
    title="FinSight API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "FinSight API",
    }


app.include_router(stores_router)
app.include_router(sales_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(inventory_router)
app.include_router(anomalies_router)

app.include_router(daily_store_metrics_router)
app.include_router(product_performance_router)
app.include_router(customer_metrics_router)
app.include_router(inventory_metrics_router)

app.include_router(finance_router)
app.include_router(finance_analytics_router)
app.include_router(auth_router)
app.include_router(ai_router)

import os
from fastapi.staticfiles import StaticFiles

frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")