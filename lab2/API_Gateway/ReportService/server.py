import grpc
from concurrent import futures
import sys
import os
sys.path.append('.')
from TransactionService.client import TransactionServiceClient
from tools import *
import report_pb2, report_pb2_grpc
from dotenv import load_dotenv


load_dotenv()

class ReportService(report_pb2_grpc.ReportServiceServicer):
    def __init__(self):
        self.client = TransactionServiceClient()

    def GetMontlyReport(self, request, context):
        try:
            sub_request = self.client.getMontlyReportRequest(month = request.month)
            metadata = dict(context.invocation_metadata())
            metadata = [('authorization', metadata.get('authorization'))]
            response = self.client.stub.GetTransactionSet(sub_request, metadata=metadata)
            report = make_report(response.transactions)
            return report_pb2.ReportResponse(**report)


        except grpc.RpcError as rpc_error:
            context.set_details(rpc_error.details())
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return report_pb2.ReportResponse()

    def GetMontlyReportFile(self, request, context):
        try:
            sub_request = self.client.getMontlyReportRequest(month=request.month)
            metadata = dict(context.invocation_metadata())
            metadata = [('authorization', metadata.get('authorization'))]
            response = self.client.stub.GetTransactionSet(sub_request, metadata=metadata)
            path = make_serialized(request, response.transactions)
            return report_pb2.ExportReportResponse(download_url=path)

        except grpc.RpcError as rpc_error:
            context.set_details(rpc_error.details())
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return report_pb2.ExportReportResponse()


def serve():
    port = os.getenv("REPORT_SERVICE_PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    report_pb2_grpc.add_ReportServiceServicer_to_server(ReportService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server is running on port {port}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()