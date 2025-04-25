from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response, Request
from fastapi.responses import RedirectResponse
from routers.user_router import *
from routers.transaction_router import *
from routers.report_router import *
from routers.auth_router import *

app = FastAPI(
    title="gRPC Microsevices APP",
    description = "You can register, add transactions, get report by transactions."
)
app.include_router(user_router, prefix="/users", tags=["User Router"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transaction Router"])
app.include_router(report_router, prefix="/reports", tags=["Report Router"])
app.include_router(auth_router, prefix="/auth", tags=["Auth Router"])
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")
