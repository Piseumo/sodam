import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# ✅ (1) 기존 데이터 삭제 (TRUNCATE TABLE → AUTO_INCREMENT 초기화)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Warehouse_Orders_Requests;")
cursor.execute("TRUNCATE TABLE Store_Order_Requests;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("기존 데이터 삭제 완료!")

# ✅ warehouse_id 고정값 설정
warehouse_id = 1
store_ids = [2, 3, 4, 5, 6]

# ✅ 요청 유형 및 상태 ENUM 값
request_types = ['입고', '출고']
sources = ['매장발주', '공급처발주', '온라인주문']
warehouse_statuses = ['요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소']
store_statuses = ['요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소']

# ✅ 더미 데이터 개수 설정
num_records = 1000000  # ✅ 적절한 데이터 개수로 조정

# ✅ Warehouse_Orders_Requests 데이터 생성 및 삽입
for _ in range(num_records):
    request_type = random.choice(request_types)
    source = random.choice(sources)
    status = random.choice(warehouse_statuses)
    created_at = fake.date_time_between(start_date="-1y", end_date="now")
    updated_at = created_at if random.random() > 0.5 else fake.date_time_between(start_date=created_at, end_date="now")
    
    sql = """
    INSERT INTO Warehouse_Orders_Requests (warehouse_id, type, source, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    values = (warehouse_id, request_type, source, status, created_at, updated_at)

    cursor.execute(sql, values)

conn.commit()
print("Warehouse_Orders_Requests 데이터 삽입 완료!")

# ✅ Store_Order_Requests 데이터 생성 및 삽입
for _ in range(num_records):
    store_id = random.choice(store_ids)
    quantity = random.randint(1, 100)
    status = random.choice(store_statuses)
    created_at = fake.date_time_between(start_date="-1y", end_date="now")
    updated_at = created_at if random.random() > 0.5 else fake.date_time_between(start_date=created_at, end_date="now")
    
    sql = """
    INSERT INTO Store_Order_Requests (store_id, quantity, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s);
    """
    values = (store_id, quantity, status, created_at, updated_at)

    cursor.execute(sql, values)

conn.commit()
print("Store_Order_Requests 데이터 삽입 완료!")

# ✅ 커서 및 연결 종료
cursor.close()
conn.close()

print("더미 데이터 삽입이 완료되었습니다.")
