from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.agents import router as agents_router
from app.api.v1.objectives import router as objectives_router
from app.api.v1.contracts import router as contracts_router
from app.api.v1.payments import router as payments_router
from app.api.v1.deliverables import router as deliverables_router
from app.api.v1.ledger import router as ledger_router
from app.api.v1.ws import router as ws_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(agents_router)
api_router.include_router(objectives_router)
api_router.include_router(contracts_router)
api_router.include_router(payments_router)
api_router.include_router(deliverables_router)
api_router.include_router(ledger_router)
api_router.include_router(ws_router)
