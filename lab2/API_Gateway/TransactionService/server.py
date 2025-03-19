import json
import os
import atexit
import grpc
from concurrent import futures
import sys
sys.path.append('.')
from UserService.client import UserServiceClient
import transaction_pb2, transaction_pb2_grpc
from google.protobuf.json_format import MessageToDict
import datetime
from dotenv import load_dotenv


load_dotenv()
transactions = None
path = 'TransactionService/transactions.json'

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
            return [t for t in user_ts if datetime.datetime.fromtimestamp(float(t.get("timestamp"))).strftime('%Y-%m') == month]

    return transactions.get(userid, None)


class TransactionService(transaction_pb2_grpc.TransactionServiceServicer):
    def __init__(self):
        self.client = UserServiceClient()

    def authorized(self, context):
        request = self.client.createGetUserRequest()
        try:
            metadata = dict(context.invocation_metadata())
            token = metadata.get('authorization')
            response = self.client.stub.GetUser(request, metadata=(('authorization', token),))
            return response
        except grpc.RpcError as e:
            raise e

    def AddTransaction(self, request, context):
        try:
            response = self.authorized(context)
        except grpc.RpcError as e:
            print(f"Auth error: {e.code()} - {e.details()}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Auth error')
            return transaction_pb2.TransactionResponse()

        userid= response.userid
        transaction_model = add_transaction(userid, request)
        return transaction_pb2.TransactionResponse(**transaction_model)


    def GetTransactionSet(self, request, context):
        try:
            response = self.authorized(context)
        except grpc.RpcError as e:
            print(f"Auth error: {e.code()} - {e.details()}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Auth error')
            return transaction_pb2.TransactionResponse()

        userid = response.userid
        user_transactions_by_month = get_transactions(userid, month = request.month)
        if user_transactions_by_month:
            return transaction_pb2.TransactionSetResponse(transactions = [transaction_pb2.TransactionResponse(**t) for t in user_transactions_by_month])

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Not found')
        return transaction_pb2.TransactionSetResponse()

def save():
    dump_transactions()

def serve():
    port = os.getenv('TRANSACTION_SERVICE_PORT')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transaction_pb2_grpc.add_TransactionServiceServicer_to_server(TransactionService(), server)
    server.add_insecure_port(f"[::]:{port}")
    atexit.register(save)
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()
    dump_transactions()

if __name__ == "__main__":
    serve()