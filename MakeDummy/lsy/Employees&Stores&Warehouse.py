import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)

cursor = conn.cursor()

# ✅ 직급 및 역할 데이터
roles = ['고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', 
         '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사']
daegu_districts = ["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"]

# ✅ (1) 더미 매니저 추가
sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
         VALUES (%s, %s, %s, NULL, NULL, %s, CURDATE(), %s, %s, TRUE)"""
values = ('Dummy Manager', '010-0000-0000', 'dummy@company.com', '매장 관리자', 0, '매장')

cursor.execute(sql, values)
dummy_manager_id = cursor.lastrowid  # ✅ 더미 매니저 ID 저장

conn.commit()

print(f"더미 매니저 ID: {dummy_manager_id} 생성 완료!")

# ✅ (2) 매장 데이터 10개 삽입
store_ids = []

for _ in range(10):
    name = fake.company() + " 매장"
    contact_number = "053-" + fake.numerify("###-####")
    open_time = "08:00:00"
    close_time = "22:00:00"
    address = f"대구광역시 {random.choice(daegu_districts)} {fake.street_address()}"
    status = '운영'
    manager_id = dummy_manager_id  # ✅ 초기에는 더미 매니저 사용
    registration_number = fake.numerify("###-##-#####")

    sql = """INSERT INTO Stores (name, contact_number, open_time, close_time, address, status, manager_id, registration_number, industry_type)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '소매업')"""
    values = (name, contact_number, open_time, close_time, address, status, manager_id, registration_number)

    cursor.execute(sql, values)
    store_ids.append(cursor.lastrowid)

conn.commit()

print("매장 데이터 삽입 완료!")

# ✅ (3) 물류센터 데이터 5개 삽입
warehouse_ids = []

for _ in range(5):
    name = fake.company() + " 물류센터"
    contact_number = "053-" + fake.numerify("###-####")
    address = f"대구광역시 {random.choice(daegu_districts)} {fake.street_address()}"
    manager_id = dummy_manager_id  # ✅ 초기에는 더미 매니저 사용
    registration_number = fake.numerify("###-##-#####")

    sql = """INSERT INTO Warehouses (name, contact_number, address, manager_id, registration_number, industry_type)
             VALUES (%s, %s, %s, %s, %s, '물류')"""
    values = (name, contact_number, address, manager_id, registration_number)

    cursor.execute(sql, values)
    warehouse_ids.append(cursor.lastrowid)

conn.commit()

print("물류센터 데이터 삽입 완료!")

# ✅ (4) 직원 데이터 100명 삽입 (역할별로 적절한 store_id, warehouse_id 자동 할당)
employee_ids = []

for _ in range(100):
    name = fake.name()
    phone = "010-" + fake.numerify("####-####")
    email = fake.email()
    role = random.choice(roles)
    salary = random.randint(3000000, 10000000)  # ✅ 급여 300만원 ~ 1000만원

    # ✅ role에 따라 store_id 또는 warehouse_id 할당
    if role in ['매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자']:
        store_id = random.choice(store_ids)
        warehouse_id = None
        location_type = '매장'
    elif role in ['고객 지원', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사']:
        store_id = None
        warehouse_id = random.choice(warehouse_ids)
        location_type = '물류센터'
    else:  # 고객지원은 랜덤 배정
        if random.choice([True, False]):
            store_id = random.choice(store_ids)
            warehouse_id = None
            location_type = '매장'
        else:
            store_id = None
            warehouse_id = random.choice(warehouse_ids)
            location_type = '물류센터'

    sql = """INSERT INTO Employees (name, phone, email, store_id, warehouse_id, role, hire_date, salary, location_type, insurance)
             VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s, %s, TRUE)"""
    values = (name, phone, email, store_id, warehouse_id, role, salary, location_type)

    cursor.execute(sql, values)
    employee_ids.append(cursor.lastrowid)

conn.commit()

print("직원 데이터가 MySQL에 삽입되었습니다!")

# ✅ (5) 더미 매니저 업데이트 (실제 매장 및 물류센터 관리자로 변경)
if store_ids:
    sql = """UPDATE Stores SET manager_id = %s WHERE manager_id = %s"""
    cursor.execute(sql, (random.choice(employee_ids), dummy_manager_id))

if warehouse_ids:
    sql = """UPDATE Warehouses SET manager_id = %s WHERE manager_id = %s"""
    cursor.execute(sql, (random.choice(employee_ids), dummy_manager_id))

conn.commit()

print("더미 매니저 업데이트 완료!")

# ✅ (6) 더미 매니저 삭제 (선택)
sql = "DELETE FROM Employees WHERE email = 'dummy@company.com'"
cursor.execute(sql)
conn.commit()

print("더미 매니저 삭제 완료!")

# ✅ 데이터베이스 연결 종료
cursor.close()
conn.close()

print("직원, 매장, 물류센터 데이터가 성공적으로 삽입되었습니다!")
