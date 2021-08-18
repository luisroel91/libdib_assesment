import time

import pandas as pd

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from app.core.config import settings
from app.database import init_models, get_session
from .models.record import CensusRecord

from sqlalchemy.ext.asyncio import AsyncSession

# Import our routers
from app.routers import auth, record, user


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


# Load env vars for fastapi_jwt_auth
@AuthJWT.load_config
def get_config():
    return settings


# Register fastapi_jwt_auth exception handler
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"auth_error": exc.message}
    )


# Pop DB on startup
@app.on_event("startup")
async def db_init():
    await init_models()


# Define root route so that it redirs to /docs
@app.get("/")
async def redir_to_docs():
    response = RedirectResponse(url="/docs")
    return response


# Link routers to main app
app.include_router(auth.router)
app.include_router(record.router)
app.include_router(user.router)
