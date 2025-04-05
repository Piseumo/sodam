import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# ✅ Faker 설정
fake = Faker("ko_KR")

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
cursor.execute("TRUNCATE TABLE warehouse_orders_log;")
cursor.execute("TRUNCATE TABLE warehouse_orders_details;")
cursor.execute("TRUNCATE TABLE warehouse_orders_requests;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ Step 1 완료: 기존 데이터 초기화\n")

# ✅ (2) 참조 데이터 로딩
print("▶️ Step 2: 참조 데이터 불러오는 중...")

# 창고 ID
cursor.execute("SELECT warehouse_id FROM warehouses LIMIT 1")
warehouse_id = cursor.fetchone()[0]

# 제품 ID
cursor.execute("SELECT product_id FROM product")
product_ids = [row[0] for row in cursor.fetchall()]

# 매장 발주 정보
cursor.execute("SELECT request_id, requested_by, approved_by FROM store_order_requests WHERE status != '취소'")
store_orders = cursor.fetchall()

# 온라인 주문 상세 정보
cursor.execute("""
    SELECT o.order_id, o.customer_id, od.inventory_id, od.product_name, od.quantity, od.price,
           od.status, od.refund_reason, od.exchange_inventory_id, od.created_at
    FROM online_order_detail od
    JOIN online_order o ON od.order_id = o.order_id
""")
online_details = cursor.fetchall()

# 물류센터 직원 정보
cursor.execute("""
    SELECT employee_id, role FROM employees WHERE location_type = '물류센터'
""")
warehouse_employees = cursor.fetchall()

# 역할 기반 직원 필터링
requested_online = [eid for eid, role in warehouse_employees if role == '온라인 주문 담당자']
requested_supply = [eid for eid, role in warehouse_employees if role == '입고 담당자']
approved_common = [eid for eid, role in warehouse_employees if role in ('출고 담당자', '재고 관리자')]
approved_null = None

print("✅ Step 2 완료: 참조 데이터 로딩 완료\n")

# ✅ (2) ENUM 및 설정
statuses = ['요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중']
types = ['입고', '출고']
sources = ['매장발주', '공급처발주', '온라인주문']
batch_size = 1000

# ✅ (3) 매장발주 기반 warehouse_orders 데이터 INSERT
print("▶️ Step 3: 매장발주 warehouse_orders_* INSERT 시작...")
for batch_start in range(0, len(store_orders), batch_size):
    batch = store_orders[batch_start:batch_start + batch_size]
    request_batch = []
    detail_batch = []
    log_batch = []

    for row in batch:
        store_request_id, req_by, app_by = row
        status_idx = random.randint(0, len(statuses) - 1)
        status = statuses[status_idx]
        created_at = fake.date_time_between(start_date='-6M', end_date='-1d')
        updated_at = created_at + timedelta(days=random.randint(1, 7))

        request_batch.append((
            warehouse_id, '출고', '매장발주', status,
            created_at, updated_at,
            store_request_id, req_by, app_by
        ))

    cursor.executemany("""
        INSERT INTO warehouse_orders_requests (
            warehouse_id, type, source, status, created_at, updated_at,
            store_request_id, requested_by, approved_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, request_batch)

    cursor.execute("SELECT LAST_INSERT_ID()")
    start_id = cursor.fetchone()[0]
    inserted_ids = list(range(start_id, start_id + len(batch)))

    for i, request_id in enumerate(inserted_ids):
        for _ in range(random.randint(1, 3)):
            detail_batch.append((request_id, random.choice(product_ids), random.randint(5, 50)))
        for j in range(status_idx + 1):
            log_batch.append((request_id, statuses[j], created_at + timedelta(minutes=10 * j)))

    cursor.executemany("""
        INSERT INTO warehouse_orders_details (request_id, product_id, quantity)
        VALUES (%s, %s, %s)
    """, detail_batch)

    cursor.executemany("""
        INSERT INTO warehouse_orders_log (request_id, status, changed_at)
        VALUES (%s, %s, %s)
    """, log_batch)

    conn.commit()
    print(f"✅ 매장발주 {batch_start + batch_size:,}건 완료")

# ✅ (4) 온라인주문 기반 warehouse_orders 데이터 INSERT
print("\n▶️ Step 4: 온라인주문 warehouse_orders_* INSERT 시작...")
for batch_start in range(0, len(online_details), batch_size):
    batch = online_details[batch_start:batch_start + batch_size]
    request_batch = []
    detail_batch = []
    log_batch = []

    for row in batch:
        order_id, customer_id, inventory_id, product_name, quantity, price, \
        od_status, refund_reason, exchange_id, created_at = row

        status_idx = random.randint(1, len(statuses) - 1)
        status = statuses[status_idx]
        updated_at = created_at + timedelta(days=random.randint(1, 5))
        req_by = random.choice(requested_online)
        app_by = random.choice(approved_common)

        request_batch.append((
            warehouse_id, '출고', '온라인주문', status,
            created_at, updated_at,
            None, req_by, app_by
        ))

    cursor.executemany("""
        INSERT INTO warehouse_orders_requests (
            warehouse_id, type, source, status, created_at, updated_at,
            store_request_id, requested_by, approved_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, request_batch)

    cursor.execute("SELECT LAST_INSERT_ID()")
    start_id = cursor.fetchone()[0]
    inserted_ids = list(range(start_id, start_id + len(batch)))

    for i, request_id in enumerate(inserted_ids):
        _, _, inventory_id, _, quantity, _, _, _, _, created_at = batch[i]
        detail_batch.append((request_id, inventory_id, quantity))
        for j in range(status_idx + 1):
            log_batch.append((request_id, statuses[j], created_at + timedelta(minutes=10 * j)))

    cursor.executemany("""
        INSERT INTO warehouse_orders_details (request_id, product_id, quantity)
        VALUES (%s, %s, %s)
    """, detail_batch)

    cursor.executemany("""
        INSERT INTO warehouse_orders_log (request_id, status, changed_at)
        VALUES (%s, %s, %s)
    """, log_batch)

    conn.commit()
    print(f"✅ 온라인주문 {batch_start + batch_size:,}건 완료")

# ✅ (5) 공급처발주 INSERT
print("\n▶️ Step 5: 공급처발주 warehouse_orders_requests INSERT 시작...")
supply_batch = []
for _ in range(50000):
    status_idx = random.randint(0, len(statuses) - 1)
    status = statuses[status_idx]
    created_at = fake.date_time_between(start_date='-6M', end_date='-1d')
    updated_at = created_at + timedelta(days=random.randint(1, 5))
    req_by = random.choice(requested_supply)

    supply_batch.append((
        warehouse_id, '입고', '공급처발주', status,
        created_at, updated_at, None, req_by, None
    ))

cursor.executemany("""
    INSERT INTO warehouse_orders_requests (
        warehouse_id, type, source, status, created_at, updated_at,
        store_request_id, requested_by, approved_by
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", supply_batch)
conn.commit()
print("✅ 공급처발주 50,000건 완료\n")

# ✅ 종료
cursor.close()
conn.close()
print("🎉 전체 warehouse_orders 데이터 삽입 완료!")
