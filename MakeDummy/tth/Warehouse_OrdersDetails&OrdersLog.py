import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # 외래키 제약 조건 비활성화

# 1. Warehouse_Orders_Details 데이터 삽입

# Warehouse_Orders_Requests 테이블에서 request_id 목록 가져오기
cursor.execute("SELECT request_id FROM Warehouse_Orders_Requests")
request_ids = [row[0] for row in cursor.fetchall()]
if not request_ids:
    # 만약 Warehouse_Orders_Requests 테이블에 데이터가 없다면, 임의의 request_id 목록 생성 (예: 1~10000)
    request_ids = list(range(1, 10001))

# Product 테이블에서 product_id 목록 가져오기
cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]
if not product_ids:
    # 만약 Product 테이블에 데이터가 없다면, 임의의 product_id 목록 생성 (예: 1~100000)
    product_ids = list(range(1, 100001))

num_details = 100000
for _ in range(num_details):
    req_id = random.choice(request_ids)
    prod_id = random.choice(product_ids)
    quantity = random.randint(1, 100)
    created_at = fake.date_time_between(start_date="-1y", end_date="now")
    
    sql = """
    INSERT INTO Warehouse_Orders_Details (request_id, product_id, quantity, created_at)
    VALUES (%s, %s, %s, %s)
    """
    values = (req_id, prod_id, quantity, created_at)
    cursor.execute(sql, values)

conn.commit()
print("✅ Warehouse_Orders_Details 데이터 삽입 완료!")

# 2. Warehouse_Orders_Log 데이터 삽입

statuses = ['요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소']
num_logs = 500000
for _ in range(num_logs):
    req_id = random.choice(request_ids)
    status = random.choice(statuses)
    changed_at = fake.date_time_between(start_date="-1y", end_date="now")
    
    sql = """
    INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
    VALUES (%s, %s, %s)
    """
    values = (req_id, status, changed_at)
    cursor.execute(sql, values)

conn.commit()

cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # 외래키 제약 조건 재활성화

cursor.close()
conn.close()

print("✅ Warehouse_Orders_Log 데이터 삽입 완료!")
