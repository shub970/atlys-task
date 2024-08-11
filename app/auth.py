from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-AUTH-TOKEN")

def get_user(auth_token_header: str = Security(api_key_header)):
    if validate_auth_token(auth_token_header):
        pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key"
    )

def validate_auth_token(token: str):
    pass