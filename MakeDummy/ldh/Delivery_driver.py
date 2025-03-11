import mysql.connector
import random

# MySQL 연결 설정
db = mysql.connector.connect(
     host="localhost", 
    # host="192.168.0.9",  
    # port=3306,    
    user="root",   
    password="1234", 
    database="sodam"
)

cursor = db.cursor()

# Delivery_Driver 테이블에 더미 데이터 삽입
def insert_delivery_drivers():
    # statuses = ['근무가능', '병가', '휴가', '배송중사고']
    statuses = ['근무가능']
    status_weights = [1.0]
    # status_weights = [0.92, 0.02, 0.04, 0.02]  # 각 상태에 대한 확률(92%, 2%, 4%, 2%)
    zones = ['서구', '동구', '남구', '달서구', '북구', '수성구', '중구']  # 근무 지역

    # '배송 기사' role을 가진 employee_id만 가져오기
    cursor.execute("SELECT employee_id FROM Employees WHERE role = '배송 기사'")
    delivery_drivers = [row[0] for row in cursor.fetchall()]

    # '배송 기사'인 직원들이 있을 경우, Delivery_Driver에 데이터 삽입
    if delivery_drivers:
        for employee_id in delivery_drivers:
            if employee_id == 1:
                continue  # employee_id가 1인 경우는 건너뛰기

            status = random.choices(statuses, weights=status_weights, k=1)[0]  # 확률에 따라 status 선택
            training_check = True  # 트레이닝 체크는 항상 True
            insurance = True
            # insurance = random.choice([True, False])  # 보험은 True 또는 False로 랜덤
            zone = random.choice(zones)  # 근무 지역은 균등 확률로 랜덤

            query = """
            INSERT INTO Delivery_Driver (employee_id, status, training_check, insurance, zone)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (employee_id, status, training_check, insurance, zone))

        db.commit()

# Delivery_Driver 테이블에 '배송 기사' role을 가진 직원들만 삽입
insert_delivery_drivers()

# 연결 종료
cursor.close()
db.close()

print("✅ 배송기사 데이터 삽입 완료!")