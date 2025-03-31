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

print("✅ 기존 데이터 삭제 완료!")

# ✅ (2) 역할 및 부서 설정
role_department_location = {
    # 매장팀
    '매장 총괄 관리자': ('매장팀', '매장'),
    '매장 운영 관리자': ('매장팀', '매장'),
    '매장 재고 관리자': ('매장팀', '매장'),
    '매장 주문 담당자': ('매장팀', '매장'),
    '매장 캐셔': ('매장팀', '매장'),
    '매장 CS 담당자': ('매장팀', '매장'),
    # 물류팀
    '물류센터장': ('물류팀', '물류센터'),
    '물류 입고 담당자': ('물류팀', '물류센터'),
    '물류 출고 담당자': ('물류팀', '물류센터'),
    '물류 재고 관리자': ('물류팀', '물류센터'),
    '온라인 주문 출고자': ('물류팀', '물류센터'),
    '검수 담당자': ('물류팀', '물류센터'),
    # 배송팀
    '배송 기사': ('배송팀', '물류센터'),
    # 고객지원팀
    '고객 문의 담당자': ('고객지원팀', '고객센터'),
    '반품 처리 담당자': ('고객지원팀', '고객센터'),
}

roles = list(role_department_location.keys())

# ✅ (3) 매장 정보 설정
store_locations = {
    "달서구": ("소담소담 달서구점", "대구광역시 달서구 성당로 187", "42669"),
    "북구": ("소담소담 북구점", "대구광역시 북구 옥산로 65", "41590"),
    "수성구": ("소담소담 수성구점", "대구광역시 수성구 유니버시아드로42길 127", "42250"),
    "동구": ("소담소담 동구점", "대구광역시 동구 동촌로 325", "41133"),
    "달성군": ("소담소담 달성군점", "대구광역시 달성군 현풍읍 현풍중앙로 27", "42972")
}

# ✅ (4) 더미 매니저 생성
sql = """INSERT INTO Employees (name, phone, email, role, department, hire_date, salary, location_type, insurance)
         VALUES (%s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE)"""
values = ('Dummy Manager', '010-0000-0000', 'dummy@company.com', '매장 총괄 관리자', '매장팀', 0, '매장')
cursor.execute(sql, values)
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
    sql = """INSERT INTO Stores (name, contact_number, open_time, close_time, address, status, manager_id, registration_number, industry_type)
             VALUES (%s, %s, %s, %s, %s, '운영', %s, %s, '소매업')"""
    values = (name, contact_number, open_time, close_time, address, dummy_manager_id, registration_number)
    cursor.execute(sql, values)
    store_ids[district] = cursor.lastrowid
conn.commit()

# ✅ (6) 물류센터 등록
warehouse_id = 1
sql = """INSERT INTO Warehouses (warehouse_id, name, contact_number, address, manager_id, registration_number, industry_type)
         VALUES (%s, %s, %s, %s, %s, %s, '물류')
         ON DUPLICATE KEY UPDATE warehouse_id=warehouse_id"""
values = (warehouse_id, "중앙 물류센터", "053-111-2222", "대구광역시 북구 물류로 123", dummy_manager_id, fake.numerify("###-##-#####"))
cursor.execute(sql, values)
conn.commit()

# ✅ (7) 300,000명 직원 삽입
num_employees = 300_000
batch_size = 10_000
inserted = 0
while inserted < num_employees:
    for _ in range(min(batch_size, num_employees - inserted)):
        name = fake.name()
        phone = "010-" + fake.numerify("####-####")
        email = fake.email()
        role = random.choice(roles)
        department, location_type = role_department_location[role]
        salary = random.randint(3000000, 7000000)
        store_id = random.choice(list(store_ids.values())) if location_type == "매장" else None
        w_id = warehouse_id if location_type in ["물류센터", "고객센터"] else None
        sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, department, hire_date, salary, location_type, insurance)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE)"""
        cursor.execute(sql, (name, phone, email, store_id, w_id, role, department, salary, location_type))
    conn.commit()
    inserted += batch_size
    print(f"{inserted}명 직원 삽입 완료...")

# ✅ 매장/물류 관리자 교체
for store_id in store_ids.values():
    sql = """SELECT employee_id FROM Employees WHERE store_id = %s AND role = '매장 총괄 관리자' LIMIT 1"""
    cursor.execute(sql, (store_id,))
    manager_id = cursor.fetchone()
    if manager_id:
        cursor.execute("UPDATE Stores SET manager_id = %s WHERE store_id = %s", (manager_id[0], store_id))

cursor.execute("SELECT employee_id FROM Employees WHERE warehouse_id = 1 AND role = '물류센터장' LIMIT 1")
manager_id = cursor.fetchone()
if manager_id:
    cursor.execute("UPDATE Warehouses SET manager_id = %s WHERE warehouse_id = 1", (manager_id[0],))

conn.commit()

# ✅ 더미 매니저 삭제
cursor.execute("DELETE FROM Employees WHERE employee_id = %s", (dummy_manager_id,))
conn.commit()

cursor.close()
conn.close()
print("✅ 30만명 직원 및 관리자 구성 완료!")
