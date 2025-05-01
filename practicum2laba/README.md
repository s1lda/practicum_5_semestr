## Запуск
1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Сгенерируйте gRPC-код из proto-файлов:
   ```
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service/user.proto
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. transaction_service/transaction.proto
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. report_service/report.proto
   ```
3.  Запустите все микросервисы (каждый в отдельном окне/терминале):

**User Service (порт 50051):**
```bash
python -m user_service.server
```

**Transaction Service (порт 50052):**
```bash
python -m transaction_service.server
```

**Report Service (порт 50053):**
```bash
python -m report_service.server
```

4. Запустите автотесты:
```bash
pytest client/test_client.py -s
```

