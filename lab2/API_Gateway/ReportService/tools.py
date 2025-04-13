import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_SERVICE_DIR = os.path.join(BASE_DIR, "Reports")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DEFAULT_ROLE = os.getenv("DEFAULT_ROLE")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")

def make_report(transactions, userid = 1):
    withdraw_sum = 0.0
    topup_sum = 0.0

    for t in transactions:
        if t.type == 'withdraw':
            withdraw_sum += t.count

        if t.type == 'topup':
            topup_sum += t.count

    profit_sum = topup_sum - withdraw_sum
    return {"userid": userid, "profit_sum": profit_sum, "topup_sum": topup_sum, "withdraw_sum": withdraw_sum}


def make_serialized(report_type, transactions, userid = 1):
    report = make_report(transactions, userid)
    filename = f'{datetime.now().strftime("%Y-%m")}_{report["userid"]}_report.{report_type}'
    file_path = os.path.join(REPORT_SERVICE_DIR, filename)
    print(file_path)
    with open(file_path, 'w') as f:
        if report_type == 'json':
            f.write(json.dumps(report))
        if report_type == 'csv':
            f.write(",".join(report.keys()) + "\n")
            f.write(",".join(map(str, report.values())) + "\n")

    return str(os.path.join(REPORT_SERVICE_DIR, filename))