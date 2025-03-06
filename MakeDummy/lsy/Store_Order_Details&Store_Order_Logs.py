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
cursor.execute("TRUNCATE TABLE Store_Order_Logs;")
cursor.execute("TRUNCATE TABLE Store_Order_Details;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("기존 데이터 삭제 완료!")

# ✅ (2) `Store_Order_Requests` 테이블에서 `request_id` 및 `status` 가져오기
cursor.execute("SELECT request_id, status FROM Store_Order_Requests;")
store_order_requests = cursor.fetchall()  # ✅ 매장 주문 요청 목록 (request_id, status)

# ✅ (3) `product_id` 목록 가져오기 (Product 테이블)
cursor.execute("SELECT product_id FROM Product;")
product_ids = [row[0] for row in cursor.fetchall()]  # ✅ 상품 ID 리스트

# ✅ (4) Store_Order_Logs & Store_Order_Details 데이터 생성 및 삽입
if store_order_requests and product_ids:
    batch_size = 10000  # ✅ 대량 삽입을 위한 배치 크기
    num_records = min(1000000, len(store_order_requests))  # ✅ 최대 100만 개 생성

    logs_to_insert = []
    details_to_insert = []

    for request_id, status in random.sample(store_order_requests, num_records):
        changed_at = fake.date_time_between(start_date="-1y", end_date="now")  # ✅ 최근 1년 내 변경 날짜
        
        # ✅ Store_Order_Logs 데이터 추가 (status는 Store_Order_Requests에서 가져온 값 유지)
        logs_to_insert.append((request_id, status, changed_at))

        # ✅ Store_Order_Details (각 주문 요청에 대해 랜덤한 상품 1~3개 배정)
        num_products_per_order = random.randint(1, 3)  # ✅ 각 주문마다 1~3개의 상품 포함
        selected_products = random.sample(product_ids, num_products_per_order)  # ✅ 중복 방지

        for product_id in selected_products:
            quantity = random.randint(1, 300)  # ✅ 상품 수량 (1~300)
            created_at = fake.date_time_between(start_date="-1y", end_date=changed_at)  # ✅ 변경 날짜 이전으로 설정

            details_to_insert.append((request_id, product_id, quantity, created_at))  # ✅ Store_Order_Details 데이터 추가

        # ✅ 일정 개수마다 DB에 삽입 (배치 처리)
        if len(logs_to_insert) >= batch_size:
            sql_logs = """
            INSERT INTO Store_Order_Logs (request_id, status, changed_at)
            VALUES (%s, %s, %s);
            """
            cursor.executemany(sql_logs, logs_to_insert)
            conn.commit()
            logs_to_insert = []

        if len(details_to_insert) >= batch_size:
            sql_details = """
            INSERT INTO Store_Order_Details (request_id, product_id, quantity, created_at)
            VALUES (%s, %s, %s, %s);
            """
            cursor.executemany(sql_details, details_to_insert)
            conn.commit()
            details_to_insert = []

    # ✅ 마지막 남은 데이터 삽입
    if logs_to_insert:
        sql_logs = """
        INSERT INTO Store_Order_Logs (request_id, status, changed_at)
        VALUES (%s, %s, %s);
        """
        cursor.executemany(sql_logs, logs_to_insert)
        conn.commit()

    if details_to_insert:
        sql_details = """
        INSERT INTO Store_Order_Details (request_id, product_id, quantity, created_at)
        VALUES (%s, %s, %s, %s);
        """
        cursor.executemany(sql_details, details_to_insert)
        conn.commit()

    print("Store_Order_Logs & Store_Order_Details 데이터 삽입 완료!")

# ✅ (5) 커서 및 연결 종료
cursor.close()
conn.close()

print("매장 주문 로그 & 상세 데이터가 성공적으로 삽입되었습니다! 🚀")
