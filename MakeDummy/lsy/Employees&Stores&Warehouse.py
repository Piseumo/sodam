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
cursor.execute("TRUNCATE TABLE Employees;")
cursor.execute("TRUNCATE TABLE Stores;")
cursor.execute("TRUNCATE TABLE Warehouses;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("기존 데이터 삭제 완료!")

# ✅ (2) 역할 데이터 정의
valid_roles = [
    '고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당',
    '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사'
]
general_roles = [
    '고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당',
    '물류 직원', '물류 재고 담당', '배송 기사'
]

# ✅ (3) 더미 매니저 추가
sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
         VALUES (%s, %s, %s, NULL, NULL, %s, CURDATE(), %s, %s, TRUE)"""
values = ('Dummy Manager', '010-0000-0000', 'dummy@company.com', '매장 관리자', 0, '매장')

cursor.execute(sql, values)
dummy_manager_id = cursor.lastrowid  # ✅ 더미 매니저 ID 저장

conn.commit()

print(f"더미 매니저 ID: {dummy_manager_id} 생성 완료!")

# ✅ (4) 매장 정보 (소담소담 OOO구점)
store_locations = {
    "달서구": ("소담소담 달서구점", "대구광역시 달서구 성당로 187", "42669"),
    "북구": ("소담소담 북구점", "대구광역시 북구 옥산로 65", "41590"),
    "수성구": ("소담소담 수성구점", "대구광역시 수성구 유니버시아드로42길 127", "42250"),
    "동구": ("소담소담 동구점", "대구광역시 동구 동촌로 325", "41133"),
    "달성군": ("소담소담 달성군점", "대구광역시 달성군 현풍읍 현풍중앙로 27", "42972")
}

# ✅ (5) 매장 데이터 삽입 (더미 매니저 ID 사용)
store_ids = {}

for district, (name, address, postal_code) in store_locations.items():
    contact_number = "053-" + fake.numerify("###-####")

    today = datetime.today().strftime('%Y-%m-%d')  # 현재 날짜
    open_time = f"{today} 08:00:00"
    close_time = f"{today} 22:00:00"

    registration_number = fake.numerify("###-##-#####")

    sql = """INSERT INTO Stores (name, contact_number, open_time, close_time, address, status, manager_id, registration_number, industry_type)
             VALUES (%s, %s, %s, %s, %s, '운영', %s, %s, '소매업')"""
    values = (name, contact_number, open_time, close_time, address, dummy_manager_id, registration_number)

    cursor.execute(sql, values)
    store_ids[district] = cursor.lastrowid  # ✅ 해당 구의 store_id 저장

conn.commit()

print("매장 데이터 삽입 완료!")

# ✅ (6) 물류센터 데이터 삽입 (더미 매니저 ID 사용)
warehouse_id = 1  # ✅ 물류센터는 하나만 존재

sql = """INSERT INTO Warehouses (warehouse_id, name, contact_number, address, manager_id, registration_number, industry_type)
         VALUES (%s, %s, %s, %s, %s, %s, '물류')
         ON DUPLICATE KEY UPDATE warehouse_id=warehouse_id"""  # ✅ 이미 존재하면 무시
values = (warehouse_id, "중앙 물류센터", "053-111-2222", "대구광역시 북구 물류로 123", dummy_manager_id, fake.numerify("###-##-#####"))

cursor.execute(sql, values)

conn.commit()

print("물류센터 데이터 삽입 완료!")

# ✅ (7) 직원 데이터 삽입 (관리자 + 일반 직원)
employee_ids = []
store_managers = random.sample(list(store_ids.items()), 5)  # ✅ 5개 매장 관리자를 랜덤 선정
store_manager_ids = []
# ✅ 매장 관리자 5명 생성
for district, store_id in store_managers:
    name = fake.name()
    phone = "010-" + fake.numerify("####-####")
    email = fake.email()
    salary = random.randint(5000000, 10000000)

    sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
             VALUES (%s, %s, %s, %s, NULL, '매장 관리자', CURDATE(), %s, '매장', TRUE)"""
    values = (name, phone, email, store_id, salary)

    cursor.execute(sql, values)
    employee_ids.append(cursor.lastrowid)
    store_manager_ids.append(cursor.lastrowid)
print("매장 관리자 데이터 삽입 완료!")

# ✅ 물류 관리자 1명 생성
name = fake.name()
phone = "010-" + fake.numerify("####-####")
email = fake.email()
salary = random.randint(5000000, 10000000)

sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
         VALUES (%s, %s, %s, NULL, %s, '물류 관리자', CURDATE(), %s, '물류센터', TRUE)"""
values = (name, phone, email, warehouse_id, salary)

cursor.execute(sql, values)
warehouse_manager = cursor.lastrowid
employee_ids.append(warehouse_manager)
print("물류 관리자 데이터 삽입 완료!")

# ✅ 일반 직원 생성 (총 94명)
for _ in range(999994):
    name = fake.name()
    phone = "010-" + fake.numerify("####-####")
    email = fake.email()
    role = random.choice(general_roles)
    salary = random.randint(3000000, 5000000)

    store_id = random.choice(list(store_ids.values())) if role in ['매장 직원', '매장 캐셔', '매장 재고 담당'] else None
    warehouse_id = 1 if role in ['고객지원', '물류 직원', '물류 재고 담당', '배송 기사'] else None

    sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
             VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE)"""
    values = (name, phone, email, store_id, warehouse_id, role, salary, '매장' if store_id else '물류센터')

    cursor.execute(sql, values)

conn.commit()

print("직원 데이터 삽입 완료!")

# ✅ 기존 더미 매니저 ID를 실제 매장 및 물류 관리자 ID로 업데이트
for (district, store_id), manager_id in zip(store_ids.items(), store_manager_ids):
    sql = """UPDATE Stores SET manager_id = %s WHERE store_id = %s AND manager_id = %s"""
    cursor.execute(sql, (manager_id, store_id, dummy_manager_id))

sql = """UPDATE Warehouses SET manager_id = %s WHERE warehouse_id = 1 AND manager_id = %s"""
cursor.execute(sql, (warehouse_manager, dummy_manager_id))

conn.commit()

print("매장 및 물류센터 관리자 업데이트 완료!")

# ✅ 더미 매니저 삭제
sql = "DELETE FROM Employees WHERE employee_id = %s"
cursor.execute(sql, (dummy_manager_id,))
conn.commit()

print("더미 매니저 삭제 완료!")

# ✅ 데이터베이스 연결 종료
cursor.close()
conn.close()

print("직원, 매장, 물류센터 데이터가 성공적으로 삽입되었습니다!")
