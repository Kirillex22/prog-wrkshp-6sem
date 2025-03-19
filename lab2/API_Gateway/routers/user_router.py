import sys
sys.path.append('..')
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from typing import Annotated
from google.protobuf.json_format import MessageToDict
from UserService import user_pb2
from schemas import *
from grpc_clients import *
from common import *

user_router = APIRouter()

@user_router.post("/register")
async def register_user(rur: RegisterUserRequest):
    request = user_pb2.RegisterRequest(**rur.dict())
    try:
        response = await us_client.Register(request)
    except grpc.RpcError as e:
        exception_handler(e)

    return MessageToDict(response)


@user_router.get('/get')
async def get_user(token: Annotated[str, Depends(oauth2_scheme)]):
    request = user_pb2.GetUserRequest()
    try:
        print(token)
        response = await us_client.GetUser(request, metadata=make_metadata(token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)