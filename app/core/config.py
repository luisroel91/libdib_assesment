# Settings for our App
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """
    Our App configuration class. All fields are typed.
    """
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Validator for our CORS origins setting
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        # Type check and check if input is list
        if isinstance(v, str) and not v.startswith("["):
            # If not, make input a list and return it
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            # Otherwise, just return it
            return v
        raise ValueError(v)

    DATABASE_URI: Optional[str] = "postgresql+asyncpg://postgres:postgres@database:5432/postgres"

    # JWT Secret Key
    authjwt_secret_key: str
    # Store/get tokens from cookies
    authjwt_token_location: set = {"cookies"}
    # Enable token revoke list
    authjwt_denylist_enabled: bool = True
    # Decide what kinds of tokens to check for in denylist
    authjwt_denylist_token_checks: set = {"access", "refresh"}

    # Be defining a Config subclass, we can load our .env
    # and automatically configure our App
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
