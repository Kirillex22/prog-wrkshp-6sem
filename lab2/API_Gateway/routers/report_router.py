import sys
sys.path.append("..")
import os
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.responses import FileResponse
from typing import Annotated
from google.protobuf.json_format import MessageToDict
from ReportService import report_pb2
from schemas import *
from grpc_clients import *
from common import *


report_router = APIRouter()

@report_router.get('/create')
async def get_monthly_report(
        token: Annotated[str, Depends(oauth2_scheme)],
        filter: ReportRequest = Depends()
) -> ReportResponse:
    request = report_pb2.ReportRequest(**filter.dict())
    try:
        response = await rs_client.GetMontlyReport(request, metadata=make_metadata(token))
        json = MessageToDict(response)
        report = ReportResponse(**json)
        return report

    except grpc.RpcError as e:
            exception_handler(e)


@report_router.get('/create/download')
async def get_montly_report_serialized(
        token: Annotated[str, Depends(oauth2_scheme)],
        filter: ExportReportRequest = Depends()
):
    request = report_pb2.ExportReportRequest(**filter.dict())
    file_type = filter.type
    try:
        response = await rs_client.GetMontlyReportFile(request, metadata=make_metadata(token))
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