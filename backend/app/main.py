from fastapi import FastAPI

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


app = FastAPI(
    title="FinSight API",
    version="1.0.0",
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