# prog-wrkshp-6sem

## lab2

### .env structure

JWT_SECRET_KEY=  
USER_SERVICE_PORT=  
TRANSACTION_SERVICE_PORT=  
REPORT_SERVICE_PORT=  
 

### run: 
activate venv  
python UserService/server.py  
python TransactionService/server.py  
python ReportService/server.py  
uvicorn main:app --reload  
