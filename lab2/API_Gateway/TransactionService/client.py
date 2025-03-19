import grpc
from TransactionService import transaction_pb2
from TransactionService import transaction_pb2_grpc

class TransactionServiceClient:
    def __init__(self, address='localhost:50052'):
        self.channel = grpc.insecure_channel(address)
        self.stub = transaction_pb2_grpc.TransactionServiceStub(self.channel)


    def getMontlyReportRequest(self, month):
        return transaction_pb2.TransactionSetRequest(month=month)
