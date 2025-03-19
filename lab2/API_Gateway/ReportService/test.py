import grpc
import report_pb2, report_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50053')
    stub = report_pb2_grpc.ReportServiceStub(channel)
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjEsImV4cCI6MTc0MjMxOTczMH0.XMXpxpait8Bj85JsRNzZgIYyX8PGzF2wxT7ZEZNibGo'
    metadata = [('authorization', f'Bearer {token}')]
    req = report_pb2.ReportRequest(month='2025-03')
    try:
        response = stub.GetMontlyReport(req, metadata=metadata)
        print("Report Response:", response)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

    export_request = report_pb2.ExportReportRequest(month='2025-03', type="сsv")
    try:
        export_response = stub.GetMontlyReportFile(export_request, metadata=metadata)
        print("Download URL:", export_response.download_url)
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")


if __name__ == "__main__":
    run()