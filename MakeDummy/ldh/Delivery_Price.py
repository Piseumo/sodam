import mysql.connector
import random
import numpy as np

# MySQL 연결 설정
db = mysql.connector.connect(
<<<<<<< HEAD
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
=======
    # host="localhost",  
    host="192.168.0.104",  
    # port=3306,    
    user="my_user",   
    password="1234", 
>>>>>>> LDH
    database="sodam"
)

cursor = db.cursor()

# Delivery_Price 테이블에 더미 데이터 삽입
def insert_delivery_price():
    # 배송 옵션 비율 설정
    option_types = ['일반배송', '새벽배송', '예약배송']
    option_weights = [0.8, 0.1, 0.1]  # 80%, 10%, 10%

    # Delivery 테이블에서 delivery_id 가져오기
    cursor.execute("SELECT delivery_id FROM Delivery")
    delivery_ids = [row[0] for row in cursor.fetchall()]

    # Delivery_Price 테이블에 데이터 삽입
    if delivery_ids:
        for delivery_id in delivery_ids:
            # 가격은 고정 값
            price = 2500

            # 배송 옵션 선택 (확률에 따라)
            option_type = random.choices(option_types, weights=option_weights, k=1)[0]

            # 무게는 200g (0.2kg) ~ 15kg 사이 랜덤 생성
            weight = round(random.uniform(0.2, 15), 2)

            # Delivery_Price 테이블에 데이터 삽입
            query = """
            INSERT INTO Delivery_Price (delivery_id, price, option_type, weight)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (delivery_id, price, option_type, weight))

        db.commit()

# Delivery_Price 테이블에 더미 데이터 삽입
insert_delivery_price()

# 연결 종료
cursor.close()
db.close()

print("✅ 배송비 데이터 삽입 완료!")