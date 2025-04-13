import grpc
from concurrent import futures
import sys
import os
import jwt
sys.path.append('.')
from TransactionService.client import TransactionServiceClient
from tools import *
import report_pb2, report_pb2_grpc
from dotenv import load_dotenv
from grpc import ServerInterceptor

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DEFAULT_ROLE = os.getenv("DEFAULT_ROLE")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")

def get_data_from_token(token):
    decoded_token = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
    userid = int(decoded_token["userid"])
    role = str(decoded_token["role"])
    return {'userid': userid, 'role': role}


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


class ReportService(report_pb2_grpc.ReportServiceServicer):
    def __init__(self):
        self.client = TransactionServiceClient()

    def GetMontlyReport(self, request, context):
        try:
            sub_request = self.client.getMontlyReportRequest(month = request.month)
            metadata = dict(context.invocation_metadata())
            token = metadata.get('authorization')
            data = get_data_from_token(token)

            metadata = [('authorization', token)]
            response = self.client.stub.GetTransactionSet(sub_request, metadata=metadata)


            if data['role'] == ADMIN_ROLE:
                report = make_report(response.transactions)
                return report_pb2.ReportResponse(**report)

            report = make_report(response.transactions, userid=data['userid'])
            return report_pb2.ReportResponse(**report)


        except grpc.RpcError as rpc_error:
            context.set_details(rpc_error.details())
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return report_pb2.ReportResponse()

    def GetMontlyReportFile(self, request, context):
        try:
            sub_request = self.client.getMontlyReportRequest(month=request.month)
            metadata = dict(context.invocation_metadata())
            token = metadata.get('authorization')
            data = get_data_from_token(token)

            metadata = [('authorization', token)]
            response = self.client.stub.GetTransactionSet(sub_request, metadata=metadata)


            if data['role'] == ADMIN_ROLE:
                path = make_serialized(request.type, response.transactions)
                return report_pb2.ExportReportResponse(download_url=path)

            path = make_serialized(request.type, response.transactions, userid=data['userid'])
            return report_pb2.ExportReportResponse(download_url=path)

        except grpc.RpcError as rpc_error:
            context.set_details(rpc_error.details())
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return report_pb2.ExportReportResponse()


def serve():
    port = os.getenv("REPORT_SERVICE_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors = [AuthInterceptor()])
    report_pb2_grpc.add_ReportServiceServicer_to_server(ReportService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()