import mysql.connector
from faker import Faker
import random
from datetime import timedelta

# Faker 초기화
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

# ✅ 기존 데이터 삭제
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Employee_Store_Assignments;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("기존 데이터 삭제 완료!")

# ✅ Employees 테이블에서 employee_id, store_id, department 조회 (location_type이 매장인 직원만)
cursor.execute("""
    SELECT employee_id, store_id, department 
    FROM Employees 
    WHERE store_id IS NOT NULL
      AND location_type = '매장'
""")
employee_data = cursor.fetchall()

# ✅ 상태값 리스트
statuses = ['근무 중', '전출', '종료', '휴직', '파견']

# ✅ 더미 데이터 삽입
for row in employee_data:
    employee_id, store_id, department = row
    status = random.choice(statuses)
    assigned_at = fake.date_between(start_date='-2y', end_date='-30d')
    ended_at = None if status == '근무 중' else assigned_at + timedelta(days=random.randint(30, 300))
    notes = fake.sentence(nb_words=5)

    query = """
        INSERT INTO Employee_Store_Assignments 
            (employee_id, store_id, department, assigned_at, ended_at, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (employee_id, store_id, department, assigned_at, ended_at, status, notes))

# 저장 및 종료
conn.commit()
cursor.close()
conn.close()

print(f"{len(employee_data)}명의 매장 직원 배정 기록이 추가되었습니다.")
