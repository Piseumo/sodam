import mysql.connector
from faker import Faker
import random
from datetime import datetime

# ✅ Faker 설정
fake = Faker('ko_KR')

# ✅ MySQL 연결
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# ✅ (1) 기존 데이터 삭제 (참조 무결성 off → truncate → on)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE store_order_logs;")
cursor.execute("TRUNCATE TABLE store_order_details;")
cursor.execute("TRUNCATE TABLE store_order_requests;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ 기존 데이터 초기화 완료")

# ✅ (2) 필요한 참조 테이블에서 값 불러오기
cursor.execute("SELECT store_id FROM Stores")
store_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT employee_id FROM Employees WHERE location_type = '매장'")
employee_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]

# ✅ (3) ENUM 값 정의
statuses = ['요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소']
reasons = ['정기 발주', '이벤트 준비', '재고 보충', '긴급 요청', '주말 대비']

# ✅ (4) 발주 요청 + 상세 + 로그 생성
num_requests = 100000
request_ids = []

for _ in range(num_requests):
    store_id = random.choice(store_ids)
    status = random.choice(statuses)
    reason = random.choice(reasons)
    requested_by = random.choice(employee_ids)
    approved_by = requested_by if status != '요청' else None
    created_at = fake.date_time_between(start_date='-6M', end_date='now')
    updated_at = created_at if random.random() < 0.8 else fake.date_time_between(start_date=created_at, end_date='now')

    # ✅ store_order_requests insert
    cursor.execute("""
        INSERT INTO store_order_requests (store_id, status, reason, requested_by, approved_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (store_id, status, reason, requested_by, approved_by, created_at, updated_at))
    request_id = cursor.lastrowid
    request_ids.append((request_id, status, store_id))

    # ✅ store_order_details insert (1~3개 상품)
    for _ in range(random.randint(1, 3)):
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 20)
        cursor.execute("""
            INSERT INTO store_order_details (request_id, product_id, quantity, created_at)
            VALUES (%s, %s, %s, %s)
        """, (request_id, product_id, quantity, created_at))

    # ✅ store_order_logs insert (상태 히스토리: 요청 → (승인) → (출고 중) 등)
    log_chain = ['요청']
    if status in statuses[1:]:
        log_chain.append('승인')
    if status in statuses[2:]:
        log_chain.append('출고 중')
    if status in statuses[3:]:
        log_chain.append('출고 완료')
    if status in statuses[4:]:
        log_chain.append('배송 중')
    if status in statuses[5:]:
        log_chain.append('입고 완료')
    if status == '취소':
        log_chain.append('취소')

    for i, st in enumerate(log_chain):
        log_time = created_at if i == 0 else fake.date_time_between(start_date=created_at, end_date=updated_at)
        cursor.execute("""
            INSERT INTO store_order_logs (request_id, status, changed_at)
            VALUES (%s, %s, %s)
        """, (request_id, st, log_time))

# ✅ 커밋 및 종료
conn.commit()
cursor.close()
conn.close()