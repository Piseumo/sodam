import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# ✅ (1) 기존 데이터 삭제
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Employees;")
cursor.execute("TRUNCATE TABLE Stores;")
cursor.execute("TRUNCATE TABLE Warehouses;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

# ✅ (2) 역할별 메타정보 설정 (새로운 role + department 구조 적용)
role_meta = {
    # 매장
    '점장': ('매장운영팀', '매장', '점장', True),
    '운영 담당자': ('매장운영팀', '매장', '운영 관리자', True),
    '재고 담당자': ('재고팀', '매장', '파트장', True),
    '발주 담당자': ('발주팀', '매장', '일반 직원', False),
    '캐셔': ('매장영업팀', '매장', '일반 직원', False),
    '고객응대 담당자': ('고객응대팀', '매장', '일반 직원', False),

    # 물류
    '센터장': ('물류운영팀', '물류센터', '센터장', True),
    '입고 담당자': ('물류운영팀', '물류센터', '파트장', True),
    '출고 담당자': ('물류운영팀', '물류센터', '파트장', True),
    '재고 관리자': ('재고팀', '물류센터', '파트장', True),
    '온라인 주문 담당자': ('온라인팀', '물류센터', '일반 직원', False),
    '검수 담당자': ('품질관리팀', '물류센터', '일반 직원', False),

    # 배송
    '배송 기사': ('배송팀', '물류센터', '일반 직원', False),

    # 고객지원
    'QnA 담당자': ('고객지원팀', '고객센터', '일반 직원', False),
    '반품 담당자': ('반품처리팀', '고객센터', '일반 직원', False),
}
roles = list(role_meta.keys())

# ✅ (3) 매장 정보 설정
store_locations = {
    "달서구": ("소담소담 달서구점", "대구광역시 달서구 성당로 187", "42669"),
    "북구": ("소담소담 북구점", "대구광역시 북구 옥산로 65", "41590"),
    "수성구": ("소담소담 수성구점", "대구광역시 수성구 유니버시아드로42길 127", "42250"),
    "동구": ("소담소담 동구점", "대구광역시 동구 동촌로 325", "41133"),
    "달성군": ("소담소담 달성군점", "대구광역시 달성군 현풍읍 현풍중앙로 27", "42972")
}

# ✅ (4) 더미 매니저 생성
cursor.execute("""
    INSERT INTO Employees (name, phone, email, role, department, hire_date, salary, location_type, insurance, birth_date, position, is_supervisor)
    VALUES (%s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE, %s, %s, %s)
""", (
    'Dummy Manager', '010-0000-0000', 'dummy@company.com', '점장', '매장운영팀', 0, '매장', fake.date_of_birth(minimum_age=40, maximum_age=60), '점장', True
))
dummy_manager_id = cursor.lastrowid
conn.commit()

# ✅ (5) 매장 등록
store_ids = {}
for district, (name, address, postal_code) in store_locations.items():
    contact_number = "053-" + fake.numerify("###-####")
    today = datetime.today().strftime('%Y-%m-%d')
    open_time = f"{today} 08:00:00"
    close_time = f"{today} 22:00:00"
    registration_number = fake.numerify("###-##-#####")
    cursor.execute("""
        INSERT INTO Stores (name, contact_number, open_time, close_time, address, status, manager_id, registration_number, industry_type)
        VALUES (%s, %s, %s, %s, %s, '운영', %s, %s, '소매업')
    """, (name, contact_number, open_time, close_time, address, dummy_manager_id, registration_number))
    store_ids[district] = cursor.lastrowid
conn.commit()

# ✅ (6) 물류센터 등록
warehouse_id = 1
cursor.execute("""
    INSERT INTO Warehouses (warehouse_id, name, contact_number, address, manager_id, registration_number, industry_type)
    VALUES (%s, %s, %s, %s, %s, %s, '물류')
    ON DUPLICATE KEY UPDATE warehouse_id=warehouse_id
""", (warehouse_id, "중앙 물류센터", "053-111-2222", "대구광역시 북구 물류로 123", dummy_manager_id, fake.numerify("###-##-#####")))
conn.commit()

# ✅ (7) 점장 5명 + 센터장 1명
for store_id in store_ids.values():
    birth = fake.date_of_birth(minimum_age=35, maximum_age=60)
    cursor.execute("""
        INSERT INTO Employees (name, phone, email, store_id, role, department, hire_date, salary, location_type, insurance, birth_date, position, is_supervisor)
        VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE, %s, %s, %s)
    """, (
        fake.name(), fake.phone_number(), fake.email(), store_id,
        '점장', '매장운영팀', random.randint(5000000, 7000000), '매장', birth, '점장', True
    ))

cursor.execute("""
    INSERT INTO Employees (name, phone, email, warehouse_id, role, department, hire_date, salary, location_type, insurance, birth_date, position, is_supervisor)
    VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE, %s, %s, %s)
""", (
    fake.name(), fake.phone_number(), fake.email(), warehouse_id,
    '센터장', '물류운영팀', random.randint(6000000, 8000000), '물류센터', fake.date_of_birth(minimum_age=40, maximum_age=65), '센터장', True
))
conn.commit()

# ✅ (8) 나머지 직원 299,994명 삽입
excluded_roles = {'점장', '센터장'}
num_employees = 300_000 - 6
batch_size = 10000
inserted = 0

while inserted < num_employees:
    for _ in range(min(batch_size, num_employees - inserted)):
        role = random.choice([r for r in roles if r not in excluded_roles])
        department, location_type, position, is_supervisor = role_meta[role]
        store_id = random.choice(list(store_ids.values())) if location_type == '매장' else None
        warehouse = warehouse_id if location_type in ['물류센터', '고객센터'] else None
        birth = fake.date_of_birth(minimum_age=20, maximum_age=55)
        cursor.execute("""
            INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, department, hire_date, salary, location_type, insurance, birth_date, position, is_supervisor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE, %s, %s, %s)
        """, (
            fake.name(), fake.phone_number(), fake.email(), store_id, warehouse,
            role, department, random.randint(3000000, 6000000), location_type, birth, position, is_supervisor
        ))
    conn.commit()
    inserted += batch_size
    print(f"{inserted}명 직원 삽입 완료...")

# ✅ 점장 및 센터장으로 매장 관리자 업데이트
for store_id in store_ids.values():
    cursor.execute("SELECT employee_id FROM Employees WHERE store_id = %s AND role = '점장' LIMIT 1", (store_id,))
    manager_id = cursor.fetchone()
    if manager_id:
        cursor.execute("UPDATE Stores SET manager_id = %s WHERE store_id = %s", (manager_id[0], store_id))

cursor.execute("SELECT employee_id FROM Employees WHERE warehouse_id = 1 AND role = '센터장' LIMIT 1")
manager_id = cursor.fetchone()
if manager_id:
    cursor.execute("UPDATE Warehouses SET manager_id = %s WHERE warehouse_id = 1", (manager_id[0],))

# ✅ 더미 매니저 삭제
cursor.execute("DELETE FROM Employees WHERE employee_id = %s", (dummy_manager_id,))
conn.commit()

cursor.close()
conn.close()

print("✅ 30만명 직원 및 관리자 구성 완료!")
