import sys
sys.path.append('../..')
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Cookie
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
async def get_user(access_token: str = Cookie(None)):
    request = user_pb2.GetUserRequest()
    try:
        response = await us_client.GetUser(request, metadata=make_metadata(access_token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)


@user_router.patch('/update_role')
async def update_role(update_role_req: UpdateUserRoleRequest, access_token: str = Cookie(None)):
    request = user_pb2.SetRoleRequest(**update_role_req.dict())
    try:
        response = await us_client.SetRole(request, metadata=make_metadata(access_token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)



@user_router.get('/all')
async def get_all_users(access_token: str = Cookie(None)):
    request = user_pb2.GetUsersListRequest()
    try:
        response = await us_client.GetUsersList(request, metadata=make_metadata(access_token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)