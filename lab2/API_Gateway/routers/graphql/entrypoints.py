import asyncio
from ariadne import QueryType, MutationType, SubscriptionType, make_executable_schema
from ariadne.asgi import GraphQL
from google.protobuf.json_format import MessageToDict

from ReportService import report_pb2
from TransactionService import transaction_pb2
from UserService import user_pb2
from routers.graphql.graphql_schema import schema_str
from starlette.middleware.cors import CORSMiddleware
from ariadne.asgi.handlers import GraphQLTransportWSHandler, GraphQLWSHandler
from grpc_clients import us_client, ts_client, rs_client
from common import make_metadata
import re


def camel_to_snake(name: str) -> str:
    """Преобразует camelCase или PascalCase в snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def convert_keys(obj):
    """Рекурсивно преобразует ключи словаря в snake_case"""
    if isinstance(obj, dict):
        return {camel_to_snake(k): convert_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys(item) for item in obj]
    else:
        return obj


query = QueryType()
mutation = MutationType()
subscription = SubscriptionType()

transaction_added_queue = asyncio.Queue()


@query.field("getUser")
async def resolve_get_user(_, info):
    token = info.context["request"].headers.get("token")
    request = user_pb2.GetUserRequest()
    response = await us_client.GetUser(request, metadata=make_metadata(token))

    return MessageToDict(response)


@query.field("getAllUsers")
async def resolve_get_all_users(_, info):
    token = info.context["request"].headers.get("token")
    request = user_pb2.GetUsersListRequest()
    response = await us_client.GetUsersList(request,  metadata=make_metadata(token))
    return [MessageToDict(response_item) for response_item in response.users]


@query.field("refreshToken")
async def resolve_refresh_token(_, info, refreshToken):
    request = user_pb2.ReAuthRequest(refresh_token=refreshToken)
    response = await us_client.ReAuth(request)
    return response.access_token


@query.field("getTransactions")
async def resolve_get_transactions(_, info, month):
    token = info.context["request"].headers.get("token")
    request = transaction_pb2.TransactionSetRequest(month=month)
    response = await ts_client.GetTransactionSet(request, metadata=make_metadata(token))
    return [MessageToDict(response_item) for response_item in response.transactions]


@query.field("generateAndDownloadReport")
async def resolve_generate_and_download_report(_, info, month, type):
    token = info.context["request"].headers.get("token")
    request = report_pb2.ExportReportRequest(month=month, type=type)
    response = await rs_client.GetMontlyReportFile(request, metadata=make_metadata(token))
    return response.download_url


@mutation.field("registerUser")
async def resolve_register_user(_, info, login, password, full_name):
    request = user_pb2.RegisterRequest(login=login, password=password, full_name=full_name)
    response = await us_client.Register(request)
    return MessageToDict(response)


@mutation.field("loginUser")
async def resolve_login_user(_, info, login, password):
    request = user_pb2.AuthRequest(login=login, password=password)
    response = await us_client.Auth(request)
    return convert_keys(MessageToDict(response))


@mutation.field("addTransaction")
async def resolve_add_transaction(_, info, type, count, source):
    token = info.context["request"].headers.get("token")
    request = transaction_pb2.TransactionRequest(type=type, count=count, source=source)
    response = await ts_client.AddTransaction(request, metadata=make_metadata(token))
    transaction = convert_keys(MessageToDict(response))
    await transaction_added_queue.put(transaction)
    return transaction


@subscription.source("transactionAdded")
async def source_transaction_added(_, info):
    while True:
        transaction = await transaction_added_queue.get()
        yield transaction


@subscription.field("transactionAdded")
def transaction_added_resolver(transaction, info):
    return transaction


schema = make_executable_schema(schema_str, [query, mutation, subscription])

app = CORSMiddleware(
    GraphQL(schema, debug=True, websocket_handler=GraphQLTransportWSHandler()),
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)