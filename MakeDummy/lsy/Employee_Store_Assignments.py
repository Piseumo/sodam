import mysql.connector
from faker import Faker
import random
from datetime import timedelta

# Faker 초기화
fake = Faker('ko_KR')

# ✅ MySQL 연결 (지정한 host, port, user, pw 사용)
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port=50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

# ✅ 실제 존재하는 employee_id 조회
cursor.execute("SELECT employee_id FROM Employees")
employee_ids = [row[0] for row in cursor.fetchall()]

# ✅ 실제 존재하는 store_id 조회
cursor.execute("SELECT store_id FROM Stores")
store_ids = [row[0] for row in cursor.fetchall()]

# 설정값
roles = ['매장 관리자', '매장 직원', '매장 재고 담당', '매장 캐셔', '고객지원']
statuses = ['근무 중', '이동', '퇴사', '휴직']
num_rows = 30  # 생성할 더미 데이터 수

# ✅ 더미 데이터 삽입
for _ in range(num_rows):
    employee_id = random.choice(employee_ids)
    store_id = random.choice(store_ids)
    role = random.choice(roles)
    status = random.choice(statuses)
    start_date = fake.date_between(start_date='-2y', end_date='-30d')
    end_date = None if status == '근무 중' else start_date + timedelta(days=random.randint(30, 300))
    note = fake.sentence(nb_words=5)

    query = """
        INSERT INTO Employee_Store_Assignments 
            (employee_id, store_id, role, start_date, end_date, status, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (employee_id, store_id, role, start_date, end_date, status, note))

# 저장 및 종료
conn.commit()
cursor.close()
conn.close()

print(f"{num_rows}건의 직원-매장 배치 이력이 성공적으로 추가되었습니다.")
