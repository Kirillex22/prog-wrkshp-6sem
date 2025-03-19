from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from routers.user_router import *
from routers.transaction_router import *
from routers.report_router import *
from common import *

app = FastAPI(
    title="gRPC Microsevices APP",
    description = "You can register, add transactions, get report by transactions by month."
)
app.include_router(user_router, prefix="/users", tags=["User Router"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transaction Router"])
app.include_router(report_router, prefix="/reports", tags=["Report Router"])

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    request = user_pb2.AuthRequest(login=form_data.username, password=form_data.password)
    try:
        response = await us_client.Auth(request)

    except grpc.RpcError as e:
        exception_handler(e)

    token = Token(access_token=response.token, token_type="Bearer")
    return token

