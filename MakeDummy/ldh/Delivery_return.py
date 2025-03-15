import mysql.connector
import random
import datetime

# MySQL 연결 설정
db = mysql.connector.connect(

    # host="localhost",  
    host="192.168.0.104",  
    # port=3306,    
    user="my_user",   
    password="1234", 
    database="sodam"
)

cursor = db.cursor()

def insert_delivery_return():
    # 상태 비율 설정 (균일하게)
    statuses = ['파손', '잘못배송', '수량부족', '상태불량']

    # 반품 유형 비율 설정 (균일하게)
    return_types = ['재배송', '환불', '교환']

    # 매장 직원 role인 직원만 선택
    cursor.execute("SELECT employee_id FROM Employees WHERE role = '매장 직원'")
    store_employee_ids = [row[0] for row in cursor.fetchall()]

    # 15건씩 반복 처리
    batch_size = 15
    offset = 0
    processed_ids = set()  # 이미 처리한 delivery_id를 추적

    while True:
        # Delivery 테이블에서 delivery_id와 end_date를 15건씩 가져오기
        cursor.execute(f"SELECT delivery_id, end_date FROM Delivery LIMIT {batch_size} OFFSET {offset}")
        delivery_data = cursor.fetchall()

        # 더 이상 가져올 데이터가 없으면 종료
        if not delivery_data:
            break

        # Delivery_Return 테이블에 데이터 삽입
        for delivery_id, end_date in delivery_data:
            if delivery_id in processed_ids:  # 이미 처리한 delivery_id라면 건너뜀
                continue

            if end_date is None:
                continue  # end_date가 없으면 건너뛰기

            # application_date는 end_date로부터 3일 뒤
            application_date = end_date + datetime.timedelta(days=random.randint(3, 7))

            # drop_date는 application_date의 1~3일 후
            drop_date = application_date + datetime.timedelta(days=random.randint(1, 3))

            # return_date는 drop_date의 1~2일 후
            return_date = drop_date + datetime.timedelta(days=random.randint(1, 2))

            # return_complete_date는 return_date의 1일 후
            return_complete_date = return_date + datetime.timedelta(days=1)

            # status_check는 모두 '검사완료'
            status_check = '검사완료'

            # employee_id는 매장 직원만 랜덤으로 선택
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

            # 처리한 delivery_id는 processed_ids에 추가
            processed_ids.add(delivery_id)

        db.commit()
        
        # offset을 증가시켜서 다음 배치로 이동
        offset += batch_size

# Delivery_Return 테이블에 더미 데이터 삽입
insert_delivery_return()

# 연결 종료
cursor.close()
db.close()

print("✅ 반송/반품 데이터 삽입 완료!")
