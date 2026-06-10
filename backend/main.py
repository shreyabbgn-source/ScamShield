from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.scan import router as scan_router
from .routes.feedback import router as feedback_router
from .routes.retrain import router as retrain_router
from .routes.stats import router as stats_router

app = FastAPI(title="ScamShield AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(retrain_router, prefix="/api")
app.include_router(stats_router)
