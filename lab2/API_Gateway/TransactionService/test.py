import grpc
import sys
sys.path.append('.')
from UserService import user_pb2, user_pb2_grpc
import transaction_pb2
import transaction_pb2_grpc


class TransactionClient:
    def __init__(self, transaction_service_address='localhost:50052', user_service_address='localhost:50051'):
        self.transaction_channel = grpc.insecure_channel(transaction_service_address)
        self.transaction_stub = transaction_pb2_grpc.TransactionServiceStub(self.transaction_channel)
        self.user_channel = grpc.insecure_channel(user_service_address)
        self.user_stub = user_pb2_grpc.UserServiceStub(self.user_channel)

    def authenticate(self, login, password):
        auth_request = user_pb2.AuthRequest(login=login, password=password)
        try:
            auth_response = self.user_stub.Auth(auth_request)
            if auth_response.token:
                print(f"TOKEN: {auth_response.token}")
                return auth_response.token
            else:
                print("Authentication failed")
                return None
        except grpc.RpcError as e:
            print(f"Authentication error: {e.code()} - {e.details()}")
            return None

    def add_transaction(self, token, type, amount, source):
        if not token:
            print("Authentication required.")
            return None

        metadata = [('authorization', f'Bearer {token}')]
        transaction_request = transaction_pb2.TransactionRequest(
            type=type,
            count=amount,
            source=source
        )
        try:
            response = self.transaction_stub.AddTransaction(transaction_request, metadata=metadata)
            print(f"Transaction added: {response}")
            return response
        except grpc.RpcError as e:
            print(f"Failed to add transaction: {e.code()} - {e.details()}")
            return None

    def get_transactions(self, token, month=None):
        if not token:
            print("Authentication required.")
            return None

        metadata = [('authorization', f'Bearer {token}')]
        request = transaction_pb2.TransactionSetRequest(month=month)
        try:
            response = self.transaction_stub.GetTransactionSet(request, metadata=metadata)
            if response.transactions:
                print("Transactions retrieved:")
                for transaction in response.transactions:
                    print(transaction)
                return response.transactions
            else:
                print("No transactions found.")
                return []
        except grpc.RpcError as e:
            print(f"Failed to get transactions: {e.code()} - {e.details()}")
            return None


if __name__ == "__main__":
    # Create a client instance
    client = TransactionClient()
    reg_req = user_pb2.RegisterRequest(login="admin", password="admin", full_name="admin")
    try:
        client.user_stub.Register(reg_req)
    except:
        pass
    # Authenticate the user with login and password
    token = client.authenticate(login="admin", password="admin")

    # Add a transaction
    if token:
        transaction = client.add_transaction(token, type='topup', amount=200, source='makaka')
        transaction = client.add_transaction(token, type='withdraw', amount=1000, source='makaka')
        transaction = client.add_transaction(token, type='topup', amount=500, source='makaka')

    # Retrieve transactions for the current month
    if token:
        client.get_transactions(token, month='2025-03')