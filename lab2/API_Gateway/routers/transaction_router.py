import sys
sys.path.append('..')
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Cookie
from google.protobuf.json_format import MessageToDict
from TransactionService import transaction_pb2
from schemas import *
from grpc_clients import *
from common import *


transaction_router = APIRouter()

@transaction_router.post("/")
async def add_transaction(
        transaction_request: TransactionRequest,
        access_token: str = Cookie(None)
) -> TransactionResponse:
    request = transaction_pb2.TransactionRequest(**transaction_request.dict())
    try:
        response = await ts_client.AddTransaction(request, metadata=make_metadata(access_token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)


@transaction_router.get("/monthly")
async def get_montly_transactions(
        access_token: str = Cookie(None),
        montly_transactions_req: GetMontlyTransactionsRequest = Depends()
) -> GetTransactionsResponse:
    request = transaction_pb2.TransactionSetRequest(**montly_transactions_req.dict())
    try:
        response = await ts_client.GetTransactionSet(request, metadata=make_metadata(access_token))
        return MessageToDict(response)
    except grpc.RpcError as e:
        exception_handler(e)


@transaction_router.get("/all")
async def get_all_transactions(
        access_token: str = Cookie(None)
) -> GetTransactionsResponse:
    request = transaction_pb2.AllTransactionSetRequest()
    try:
        response = await ts_client.GetAllTransactionSet(request, metadata=make_metadata(access_token))
        transactions = []
        for t in response.transactions:
            transactions.append(TransactionResponse(**MessageToDict(t)))
        return GetTransactionsResponse(transactions=transactions)
    except grpc.RpcError as e:
        exception_handler(e)
