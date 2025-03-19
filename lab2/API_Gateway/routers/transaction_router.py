import sys
sys.path.append('..')
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from typing import Annotated
from google.protobuf.json_format import MessageToDict
from TransactionService import transaction_pb2
from schemas import *
from grpc_clients import *
from common import *


transaction_router = APIRouter()

@transaction_router.post("/")
async def add_transaction(
        TransactionRequest: TransactionRequest,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> TransactionResponse:
    request = transaction_pb2.TransactionRequest(**TransactionRequest.dict())
    try:
        response = await ts_client.AddTransaction(request, metadata=make_metadata(token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)