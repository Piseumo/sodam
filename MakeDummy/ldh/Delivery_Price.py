import mysql.connector
import random

# MySQL 연결 설정
db = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# Delivery_Price 테이블에 더미 데이터 삽입
def insert_delivery_price():
    # 배송 옵션을 '일반배송'으로 고정
    option_type = '일반배송'

    # Delivery 테이블에서 assignment_id 가져오기
    cursor.execute("SELECT assignment_id FROM delivery_assignment")
    assignment_ids = [row[0] for row in cursor.fetchall()]

    # Delivery_Price 테이블에 데이터 삽입
    if assignment_ids:
        for assignment_id in assignment_ids:
            # 가격은 고정 값
            price = 2500

            # 무게는 200g (0.2kg) ~ 15kg 사이 랜덤 생성
            weight = round(random.uniform(0.2, 15), 2)

            # Delivery_Price 테이블에 데이터 삽입
            query = """
            INSERT INTO delivery_price (assignment_id, price, option_type, weight)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (assignment_id, price, option_type, weight))

        db.commit()

# Delivery_Price 테이블에 더미 데이터 삽입
insert_delivery_price()

# 연결 종료
cursor.close()
db.close()

print("✅ 배송비 데이터 삽입 완료!")
