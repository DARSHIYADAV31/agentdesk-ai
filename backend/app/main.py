import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import (admin_tickets, approvals, assign, audit, auth, notes, profile, register,
                     resolve, tickets, webhook)
from app.db import models  # noqa: F401  (registers tables)
from app.db.base import Base
from app.db.session import engine
from app.logging_setup import log_event, setup_logging

logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Base.metadata.create_all(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AgentDesk AI", lifespan=lifespan)
    for module in (auth, register, profile, tickets, admin_tickets, assign, notes, resolve,
                   webhook, approvals, audit):
        app.include_router(module.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        log_event(logger, logging.ERROR, "unhandled_error", path=request.url.path,
                  error=type(exc).__name__)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    return app


app = create_app()
