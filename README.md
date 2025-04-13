# prog-wrkshp-6sem

## lab2

### .env structure

JWT_SECRET_KEY=supersecretkey
ACCESS_TOKEN_TYPE=ACCESS
REFRESH_TOKEN_TYPE=REFRESH
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=7
USER_SERVICE_PORT=50051
TRANSACTION_SERVICE_PORT=50052
REPORT_SERVICE_PORT=50053
DEFAULT_ROLE=USER
ADMIN_ROLE=ADMIN  
 

### run: 
activate venv  
python UserService/server.py  
python TransactionService/server.py  
python ReportService/server.py  
uvicorn main:app --reload  
