import asyncio
import typer

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from app.core.config import settings
from app.database import init_models


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
    return await settings


# Register fastapi_jwt_auth exception handler
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"auth_error": exc.message}
    )


cli = typer.Typer()


@cli.command()
def db_init():
    asyncio.run(init_models())
    print("DB Populated")


# Pop DB on startup
if __name__ == "__main__":
    cli()
