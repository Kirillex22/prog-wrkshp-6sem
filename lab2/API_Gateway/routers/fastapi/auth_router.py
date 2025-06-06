import sys
sys.path.append('../..')
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from grpc_clients import us_client
from schemas import Token
from UserService import user_pb2
import grpc
from typing import Annotated
from common import *

auth_router = APIRouter()

@auth_router.post("/token")
async def login_for_access_token(
    login_response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    request = user_pb2.AuthRequest(login=form_data.username, password=form_data.password)
    try:
        response = await us_client.Auth(request)

    except grpc.RpcError as e:
        exception_handler(e)

    access_token = Token(token=response.access_token, token_type="Bearer")

    login_response.set_cookie(
        key="refresh_token",
        value=f'Bearer {response.refresh_token}',
        httponly=True,
        secure=True,
        samesite="strict"
    )

    login_response.set_cookie(
        key="access_token",
        value=f'Bearer {response.access_token}',
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return access_token


@auth_router.post("/refresh")
async def refresh_token(
        refresh_response: Response,
        request: Request
) -> Token:
    refresh_token = request.cookies.get("refresh_token")
    request = user_pb2.ReAuthRequest(refresh_token=refresh_token)
    try:
        response = await us_client.ReAuth(request)
        access_token = Token(token=response.access_token, token_type="Bearer")

        refresh_response.set_cookie(
            key="access_token",
            value=f'Bearer {response.access_token}',
            httponly=True,
            secure=True,
            samesite="strict"
        )

        return access_token

    except grpc.RpcError as e:
        exception_handler(e)