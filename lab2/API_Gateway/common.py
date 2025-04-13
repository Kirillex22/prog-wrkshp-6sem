from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

def exception_handler(e):
    details = e.details()
    raise HTTPException(status_code=500, detail=f"gRPC error: {details}")

make_metadata = lambda token: (('authorization', token),)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")