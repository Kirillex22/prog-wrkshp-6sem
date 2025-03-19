import grpc
import os
from UserService import user_pb2_grpc
from TransactionService import transaction_pb2_grpc
from ReportService import report_pb2_grpc
from dotenv import load_dotenv


load_dotenv()

user_service_channel = grpc.aio.insecure_channel(f'localhost:{os.getenv("USER_SERVICE_PORT")}')
transaction_service_channel = grpc.aio.insecure_channel(f'localhost:{os.getenv("TRANSACTION_SERVICE_PORT")}')
report_service_channel = grpc.aio.insecure_channel(f'localhost:{os.getenv("REPORT_SERVICE_PORT")}')

us_client = user_pb2_grpc.UserServiceStub(user_service_channel)
ts_client = transaction_pb2_grpc.TransactionServiceStub(transaction_service_channel)
rs_client = report_pb2_grpc.ReportServiceStub(report_service_channel)