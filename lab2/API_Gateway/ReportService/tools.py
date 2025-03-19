import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_SERVICE_DIR = os.path.join(BASE_DIR, "Reports")

def make_report(response):
    withdraw_sum = 0.0
    topup_sum = 0.0
    userid = response[0].userid

    for t in response:
        if t.type == 'withdraw':
            withdraw_sum += t.count

        if t.type == 'topup':
            topup_sum += t.count

    profit_sum = topup_sum - withdraw_sum
    return {"userid": userid, "profit_sum": profit_sum, "topup_sum": topup_sum, "withdraw_sum": withdraw_sum}


def make_serialized(request, response):
    report = make_report(response)
    filename = f'{datetime.now().strftime("%Y-%m")}_{report["userid"]}_report.{request.type}'
    file_path = os.path.join(REPORT_SERVICE_DIR, filename)
    print(file_path)
    with open(file_path, 'w') as f:
        if request.type == 'json':
            f.write(json.dumps(report))
        if request.type == 'csv':
            f.write(",".join(report.keys()) + "\n")
            f.write(",".join(map(str, report.values())) + "\n")

    return str(os.path.join(REPORT_SERVICE_DIR, filename))