import sys
sys.path.append("..")
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Cookie
from fastapi.responses import FileResponse
from google.protobuf.json_format import MessageToDict
from ReportService import report_pb2
from schemas import *
from grpc_clients import *
from common import *


report_router = APIRouter()

@report_router.get('/create')
async def get_monthly_report(
        access_token: str = Cookie(None),
        filter: ReportRequest = Depends()
) -> ReportResponse:
    request = report_pb2.ReportRequest(**filter.dict())
    try:
        response = await rs_client.GetMontlyReport(request, metadata=make_metadata(access_token))
        json = MessageToDict(response)
        report = ReportResponse(**json)
        return report

    except grpc.RpcError as e:
            exception_handler(e)


@report_router.get('/create/download')
async def get_montly_report_serialized(
        access_token: str = Cookie(None),
        filter: ExportReportRequest = Depends()
):
    request = report_pb2.ExportReportRequest(**filter.dict())
    file_type = filter.type
    try:
        response = await rs_client.GetMontlyReportFile(request, metadata=make_metadata(access_token))
        if response.download_url:
            file_url = response.download_url
            if os.path.exists(file_url):
                return FileResponse(
                    file_url,
                    media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={datetime.now().strftime('%Y-%m')}.{file_type}"}
                )
    except grpc.RpcError as e:
        exception_handler(e)