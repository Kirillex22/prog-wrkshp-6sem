from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator, confloat, conint, ConfigDict, AliasGenerator, Field


class RegisterUserRequest(BaseModel):
    login: str
    password: str
    full_name: str


class TransactionRequest(BaseModel):
    type: str
    count: confloat(ge=0)
    source: str

    @validator("type")
    def check_type(cls, value):
        if value not in ["withdraw", "topup"]:
            raise ValueError(f"Transaction {value} is not allowed")
        return value


class ReportRequest(BaseModel):
    month: str

    @validator("month")
    def check_month(cls, value):
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            raise ValueError(f"Date {value} is not valid")


class ReportResponse(BaseModel):
    profit_sum: Optional[float] = Field(None, alias="profitSum")
    withdraw_sum: Optional[float] = Field(None, alias="withdrawSum")
    topup_sum: Optional[float] = Field(None, alias="topupSum")
    userid: int



class ExportReportRequest(BaseModel):
    month: str
    type: str

    @validator("type")
    def check_type(cls, value):
        if value not in ["json", "csv"]:
            raise ValueError(f"Transaction {value} is not allowed")
        return value


class ExportReportResponse(BaseModel):
    download_url: str


class Token(BaseModel):
    token: str
    token_type: str


class UpdateUserRoleRequest(BaseModel):
    userid: int
    role: str

    @validator("role")
    def check_role(cls, value):
        if value not in ["ADMIN", "USER"]:
            raise ValueError(f"Role {value} is not provided")
        return value


class UpdateUserRoleResponse(BaseModel):
    userid: int
    role: str


class GetMontlyTransactionsRequest(BaseModel):
    month: str

    @validator("month")
    def check_month(cls, value):
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            raise ValueError(f"Date {value} is not valid")


class GetTransactionsResponse(BaseModel):
    transactions: list
