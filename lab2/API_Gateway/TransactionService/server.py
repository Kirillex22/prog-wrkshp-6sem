import json
import os
import atexit
import grpc
import jwt
from concurrent import futures
from itertools import chain
import sys
sys.path.append('.')
import transaction_pb2, transaction_pb2_grpc
from grpc import ServerInterceptor
from google.protobuf.json_format import MessageToDict
import datetime
from dotenv import load_dotenv

#------------------------------------------------------------------------
load_dotenv()
transactions = None
path = 'TransactionService/transactions.json'
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DEFAULT_ROLE = os.getenv("DEFAULT_ROLE")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")

with open(path, 'r') as f:
    serialized = f.read()
    transactions = {int(k): v for k, v in json.loads(serialized).items()}

def dump_transactions():
    with open(path, 'w') as f:
        serialized = json.dumps(transactions)
        f.write(serialized)

def add_transaction(userid, transaction):
    if not transactions.get(userid, None):
        transactions[userid] = []

    transaction_model = MessageToDict(transaction)
    transaction_model["timestamp"] = str(datetime.datetime.now().timestamp())
    transaction_model["userid"] = userid
    transactions[userid].append(transaction_model)
    return transaction_model


def get_transactions(userid, month=None):
    if month:
        user_ts = transactions.get(userid, None)
        if user_ts:
            return [t for t in user_ts
                    if datetime.datetime.fromtimestamp(float(t.get("timestamp"))).strftime('%Y-%m') == month
                    ]

    return transactions.get(userid, None)


def get_transactions_admin(month = None):
    ts = list(chain.from_iterable(transactions.values()))
    if month:
        return [t for t in ts if
                datetime.datetime.fromtimestamp(float(t.get("timestamp"))).strftime('%Y-%m') == month
                ]
    return ts


def get_data_from_token(token):
    decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
    userid = int(decoded_token["userid"])
    role = str(decoded_token["role"])
    return {'userid': userid, 'role': role}

#-------------------------------------------------------------------------------------

class AuthInterceptor(ServerInterceptor):

    def _unauth(self, message):
        def deny(request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, message)

        return grpc.unary_unary_rpc_method_handler(deny)

    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        metadata = dict(handler_call_details.invocation_metadata)

        print(f"[gRPC] Вызов метода: {method}")
        print(f"[gRPC] Метаданные: {metadata}")

        token = metadata.get('authorization')

        if not token:
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Missing token')
        try:
            jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return self._unauth("Token has expired")

        except jwt.InvalidTokenError:
            return self._unauth("Invalid token")

        return continuation(handler_call_details)


class TransactionService(transaction_pb2_grpc.TransactionServiceServicer):
    def AddTransaction(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        data = get_data_from_token(token)
        userid = data['userid']

        transaction_model = add_transaction(userid, request)
        return transaction_pb2.TransactionResponse(**transaction_model)


    def GetTransactionSet(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        data = get_data_from_token(token)
        userid, role = data['userid'], data['role']

        if role == DEFAULT_ROLE:
            user_transactions_by_month = get_transactions(userid, month = request.month)
            if user_transactions_by_month:
                return transaction_pb2.TransactionSetResponse(transactions = [transaction_pb2.TransactionResponse(**t) for t in user_transactions_by_month])

        if role == ADMIN_ROLE:
            transactions_by_month = get_transactions_admin(month=request.month)
            if transactions_by_month:
                return transaction_pb2.TransactionSetResponse(
                    transactions=[transaction_pb2.TransactionResponse(**t) for t in transactions_by_month])

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Not found')
        return transaction_pb2.TransactionSetResponse()


    def GetAllTransactionSet(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        data = get_data_from_token(token)
        role = data['role']

        if role == ADMIN_ROLE:
            all_transactions = get_transactions_admin(month=None)
            return transaction_pb2.TransactionSetResponse(
                transactions=[transaction_pb2.TransactionResponse(**t) for t in all_transactions])

        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details('User is not an admin')
        return transaction_pb2.TransactionSetResponse()


def save():
    dump_transactions()

def serve():
    port = os.getenv('TRANSACTION_SERVICE_PORT')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=[AuthInterceptor()])
    transaction_pb2_grpc.add_TransactionServiceServicer_to_server(TransactionService(), server)
    server.add_insecure_port(f"[::]:{port}")
    atexit.register(save)
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()
    dump_transactions()

if __name__ == "__main__":
    serve()