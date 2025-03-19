from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, validator, confloat, conint, ConfigDict, AliasGenerator, Field


def to_snake_case(string: str) -> str:
    # Преобразует camelCase в snake_case
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', string).lower()


class RegisterUserRequest(BaseModel):
    login: str
    password: str
    full_name: str


class RegisterUserResponse(BaseModel):
    userid: int

    class Config:
        alias_generator = to_snake_case

class GetUserResponse(BaseModel):
    login: str
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


class TransactionResponse(BaseModel):
    type: str
    count: float
    source: str
    timestamp: datetime


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

    class Config:
        alias_generator = to_snake_case


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
    access_token: str
    token_type: str

