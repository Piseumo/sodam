import mysql.connector
import random
import datetime

# MySQL 연결 설정
db = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# Delivery_Return 테이블에 더미 데이터 삽입
def insert_delivery_return():
    # 상태 비율 설정 (균일하게)
    statuses = ['파손', '잘못배송', '수량부족', '상태불량']

    # 반품 유형 비율 설정 (균일하게)
    return_types = ['재배송', '환불', '교환']

    # Delivery 테이블에서 delivery_id와 end_date 가져오기
    cursor.execute("SELECT delivery_id, end_date FROM Delivery")
    delivery_data = cursor.fetchall()

    # 매장 직원 role인 직원만 선택
    cursor.execute("SELECT employee_id FROM Employees WHERE role = '고객지원'")
    store_employee_ids = [row[0] for row in cursor.fetchall()]

    # Delivery_Return 테이블에 데이터 삽입
    if delivery_data and store_employee_ids:
        for delivery_id, end_date in delivery_data:
            # application_date는 end_date로부터 3일 뒤
            if end_date is None:
                continue  # end_date가 없으면 건너뛰기
            application_date = end_date + datetime.timedelta(days=random.randint(3, 7))  # 3일에서 7일 사이

            # drop_date는 application_date의 1~3일 후
            drop_date = application_date + datetime.timedelta(days=random.randint(1, 3))

            # return_date는 drop_date의 1~2일 후
            return_date = drop_date + datetime.timedelta(days=random.randint(1, 2))

            # return_complete_date는 return_date의 1일 후
            return_complete_date = return_date + datetime.timedelta(days=1)

            # status_check는 모두 '검사완료'
            status_check = '검사완료'

            # employee_id는 매장 직원만 원투매니로 받기
            employee_id = random.choice(store_employee_ids)

            # return_types는 균일하게
            return_type = random.choice(return_types)

            # status는 균일하게
            status = random.choice(statuses)

            # Delivery_Return 테이블에 데이터 삽입
            query = """
            INSERT INTO Delivery_Return (status, application_date, drop_date, return_date, return_complete_date, 
                                         status_check, employee_id, return_types, delivery_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (status, application_date, drop_date, return_date, return_complete_date, 
                                   status_check, employee_id, return_type, delivery_id))

        db.commit()

# Delivery_Return 테이블에 더미 데이터 삽입
insert_delivery_return()

# 연결 종료
cursor.close()
db.close()

print("✅ 반송/반품 데이터 삽입 완료!")