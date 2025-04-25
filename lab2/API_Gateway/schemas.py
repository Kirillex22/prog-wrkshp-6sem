from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator, confloat, conint, ConfigDict, AliasGenerator, Field
import os


USER_ROLE = str(os.getenv('USER_ROLE'))
ADMIN_ROLE = str(os.getenv('ADMIN_ROLE'))

ROLES = [USER_ROLE, ADMIN_ROLE]
TRANSACTIONS_TYPES = ['withdraw', 'topup']
FILE_TYPES = ['json', 'csv']


class RegisterUserRequest(BaseModel):
    login: str
    password: str
    full_name: str


class TransactionRequest(BaseModel):
    type: str = Field( ..., description='Тип транзакции. Снятие: withdraw, Пополнение: topup')
    count: confloat(ge=0)
    source: str = Field( ..., description='Источник транзакции.')

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
    month: str = Field( ..., description='Месяц, за который нужен отчет. В формате ГГГГ-ММ')

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
    month: str = Field( ..., description='Месяц, за который нужен отчет. В формате ГГГГ-ММ')
    type: str = Field( ..., description='Тип создаваемого файла. Допустимо: json, csv.')

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
    userid: int = Field( ..., description='ID пользователя.')
    role: str = Field( ..., description='Целевая роль. Допустимо: ADMIN, USER.')

    @validator("role")
    def check_role(cls, value):
        if value not in [ADMIN_ROLE, USER_ROLE]:
            raise ValueError(f"Role {value} is not provided")
        return value


class UpdateUserRoleResponse(BaseModel):
    userid: int
    role: str


class GetMontlyTransactionsRequest(BaseModel):
    month: str = Field( ..., description='Месяц, за который нужен отчет. В формате ГГГГ-ММ')

    @validator("month")
    def check_month(cls, value):
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            raise ValueError(f"Date {value} is not valid")


class GetTransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]
