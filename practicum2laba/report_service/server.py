import grpc
from concurrent import futures
from report_service import report_pb2
from report_service import report_pb2_grpc
from report_service import db
import csv
import json
import os
from datetime import datetime
import msgpack

def get_month_date_range(year, month):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year+1, 1, 1)
    else:
        end = datetime(year, month+1, 1)
    return start.date(), (end.date())

class ReportServiceServicer(report_pb2_grpc.ReportServiceServicer):
    def _generate_report_data(self, user_id, year, month):
        """Общий метод для генерации данных отчета"""
        conn = db.get_conn()
        cur = conn.cursor()
        start_date, end_date = get_month_date_range(year, month)
        try:
            cur.execute("""
                SELECT category, tx_type as type, SUM(amount) as total
                FROM transactions
                WHERE user_id=%s AND date >= %s AND date < %s
                GROUP BY category, tx_type
            """, (user_id, start_date, end_date))
            rows = cur.fetchall()
            
            categories = {}
            total_income = 0.0
            total_expense = 0.0
            
            for row in rows:
                cat = row['category']
                if cat not in categories:
                    categories[cat] = {'income': 0.0, 'expense': 0.0}
                if row['type'] == 'income':
                    categories[cat]['income'] += row['total']
                    total_income += row['total']
                else:
                    categories[cat]['expense'] += row['total']
                    total_expense += row['total']
            
            return {
                'categories': categories,
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': total_income - total_expense
            }
        finally:
            cur.close()
            conn.close()

    def GenerateMonthlyReport(self, request, context):
        """Генерация отчета в protobuf формате"""
        try:
            report_data = self._generate_report_data(request.user_id, request.year, request.month)
            
            cat_summaries = [
                report_pb2.CategorySummary(category=cat, income=val['income'], expense=val['expense'])
                for cat, val in report_data['categories'].items()
            ]
            
            report = report_pb2.MonthlyReport(
                user_id=request.user_id,
                year=request.year,
                month=request.month,
                total_income=report_data['total_income'],
                total_expense=report_data['total_expense'],
                balance=report_data['balance'],
                categories=cat_summaries
            )
            return report_pb2.GenerateMonthlyReportResponse(report=report)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error generating report: {str(e)}")
            return report_pb2.GenerateMonthlyReportResponse()

    def ExportReport(self, request, context):
        """Экспорт отчета в файл (json/csv/msgpack)"""
        try:
            report_data = self._generate_report_data(request.user_id, request.year, request.month)
            
            # Подготовка данных для экспорта
            cat_summaries = [
                {'category': cat, 'income': val['income'], 'expense': val['expense']}
                for cat, val in report_data['categories'].items()
            ]
            
            export_data = {
                'user_id': request.user_id,
                'year': request.year,
                'month': request.month,
                'total_income': report_data['total_income'],
                'total_expense': report_data['total_expense'],
                'balance': report_data['balance'],
                'categories': cat_summaries
            }
            
            # Создание директории для экспорта
            file_dir = os.path.join(os.getcwd(), 'report_service', 'exports')
            os.makedirs(file_dir, exist_ok=True)
            filename = f"report_{request.user_id}_{request.year}_{request.month}.{request.format}"
            file_path = os.path.join(file_dir, filename)
            
            # Экспорт в нужный формат
            if request.format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            elif request.format == 'csv':
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['category', 'income', 'expense'])
                    writer.writeheader()
                    writer.writerows(cat_summaries)
            elif request.format == 'msgpack':
                with open(file_path, 'wb') as f:
                    msgpack.dump(export_data, f)
            else:
                return report_pb2.ExportReportResponse(file_url="", status="unsupported format")
            
            return report_pb2.ExportReportResponse(file_url=file_path, status="exported")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Export error: {str(e)}")
            return report_pb2.ExportReportResponse(file_url="", status=f"error: {str(e)}")

    def GetMonthlyReportMsgPack(self, request, context):
        """Получение отчета в бинарном msgpack формате"""
        try:
            report_data = self._generate_report_data(request.user_id, request.year, request.month)
            
            # Добавляем метаданные
            full_data = {
                'user_id': request.user_id,
                'year': request.year,
                'month': request.month,
                **report_data
            }
            
            # Сериализуем в MessagePack
            msgpack_data = msgpack.packb(full_data)
            
            return report_pb2.MsgPackReportResponse(msgpack_data=msgpack_data)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"MsgPack error: {str(e)}")
            return report_pb2.MsgPackReportResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    report_pb2_grpc.add_ReportServiceServicer_to_server(ReportServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    print("gRPC сервер ReportService запущен на порту 50053")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()