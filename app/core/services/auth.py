"""
Functions for password hashing and verification
"""
from fastapi_jwt_auth import AuthJWT

from passlib.context import CryptContext


# Typically you'd store the deny list on something like redis, but for this demo, a set is ok
denylist = set()

# Passlib context that we will hash/verify password with using bcrypt
passwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


# Function that checks if a token's identifier is in our deny list
@AuthJWT.token_in_denylist_loader
async def check_if_in_denylist(plaintext_token):
    jti = plaintext_token['jti']
    return jti in denylist


# Gets password from login request and returns hash
async def get_password_hash(password: str):
    return await passwd_context.hash(password)


# Compares password from login request to hash to see if password is correct
async def verify_password(plain_text: str, hashed_pw: str):
    return await passwd_context.verify(plain_text, hashed_pw)

