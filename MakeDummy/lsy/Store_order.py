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

# ✅ (1) 기존 데이터 삭제
print("▶️ Step 1: 기존 데이터 초기화 중...")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE store_order_logs;")
cursor.execute("TRUNCATE TABLE store_order_details;")
cursor.execute("TRUNCATE TABLE store_order_requests;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ Step 1 완료: 기존 데이터 초기화\n")

# ✅ (2) 참조 데이터 불러오기
print("▶️ Step 2: 참조 데이터 로딩 중...")
cursor.execute("SELECT store_id FROM Stores")
store_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT employee_id FROM Employees WHERE location_type = '매장' AND role = '발주 담당자'")
requested_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("""
    SELECT employee_id FROM Employees 
    WHERE location_type = '물류센터' 
      AND role IN ('출고 담당자', '센터장')
""")
approved_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]
print("✅ Step 2 완료: 참조 데이터 로딩 완료\n")

# ✅ (3) ENUM 및 설정
statuses = ['요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소']
reasons = ['정기 발주', '이벤트 준비', '재고 보충', '긴급 요청', '주말 대비']
batch_size = 10000
total_requests = 1000000

# ✅ (4) 데이터 생성
print(f"▶️ Step 3: 총 {total_requests:,}건 배치로 삽입 시작...\n")

for batch_start in range(0, total_requests, batch_size):
    request_batch = []
    detail_batch = []
    log_batch = []

    for _ in range(batch_size):
        store_id = random.choice(store_ids)
        status = random.choice(statuses)
        reason = random.choice(reasons)
        requested_by = random.choice(requested_ids)
        approved_by = random.choice(approved_ids) if status != '요청' else None
        created_at = fake.date_time_between(start_date='-6M', end_date='now')
        updated_at = created_at if random.random() < 0.8 else fake.date_time_between(start_date=created_at, end_date='now')

        request_batch.append((store_id, status, reason, requested_by, approved_by, created_at, updated_at))

    # ✅ 요청 데이터 배치 INSERT
    cursor.executemany("""
        INSERT INTO store_order_requests (store_id, status, reason, requested_by, approved_by, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, request_batch)

    # ✅ INSERT 후 ID 조회
    cursor.execute("SELECT LAST_INSERT_ID()")
    start_id = cursor.fetchone()[0]
    inserted_ids = list(range(start_id, start_id + batch_size))

    # ✅ 세부 정보 및 로그 구성
    for i, request_id in enumerate(inserted_ids):
        status = request_batch[i][1]
        created_at = request_batch[i][5]
        updated_at = request_batch[i][6]

        # 세부 상품 (1~3개)
        for _ in range(random.randint(1, 3)):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 20)
            detail_batch.append((request_id, product_id, quantity, created_at))

        # 로그 히스토리
        log_chain = ['요청']
        if status in statuses[1:]: log_chain.append('승인')
        if status in statuses[2:]: log_chain.append('출고 중')
        if status in statuses[3:]: log_chain.append('출고 완료')
        if status in statuses[4:]: log_chain.append('배송 중')
        if status in statuses[5:]: log_chain.append('입고 완료')
        if status == '취소': log_chain.append('취소')

        for idx, st in enumerate(log_chain):
            log_time = created_at if idx == 0 else fake.date_time_between(start_date=created_at, end_date=updated_at)
            log_batch.append((request_id, st, log_time))

    # ✅ 세부 상품 및 로그 삽입
    cursor.executemany("""
        INSERT INTO store_order_details (request_id, product_id, quantity, created_at)
        VALUES (%s, %s, %s, %s)
    """, detail_batch)

    cursor.executemany("""
        INSERT INTO store_order_logs (request_id, status, changed_at)
        VALUES (%s, %s, %s)
    """, log_batch)

    conn.commit()
    print(f"✅ {batch_start + batch_size:,}건 삽입 완료!")

# ✅ 종료
cursor.close()
conn.close()
print("\n🎉 전체 배치 데이터 삽입 완료!")
