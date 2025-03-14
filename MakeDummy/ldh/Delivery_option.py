import mysql.connector
import random
from datetime import datetime, timedelta

# MySQL 연결 설정
db = mysql.connector.connect(

    host="192.168.0.104",  
    user="my_user",   
    password="1234", 
    database="sodam"
)

cursor = db.cursor()

# Delivery_Option 테이블에 더미 데이터 삽입 (Delivery_Price 외래키 참조)
def insert_delivery_options(num_records):
    # Delivery_Price에서 '새벽배송' 또는 '예약배송' 옵션을 가진 price_id를 가져옵니다.
    cursor.execute("""
        SELECT price_id
        FROM Delivery_Price 
        WHERE option_type IN ('새벽배송', '예약배송')
        LIMIT %s
    """, (num_records,))  # num_records 만큼의 price_id를 가져옵니다.
    
    results = cursor.fetchall()
    
    for result in results:
        price_id = result[0]

        # 현재 날짜에서 1년 이내의 랜덤 날짜 생성
        current_date = datetime.now()
        random_days = random.randint(0, 365)  # 현재 날짜부터 최대 1년 이내로 랜덤 날짜
        request_datetime = current_date - timedelta(days=random_days)

        # price_id가 이미 Delivery_Option 테이블에 존재하는지 체크
        cursor.execute("""
            SELECT COUNT(*) FROM Delivery_Option WHERE price_id = %s
        """, (price_id,))
        count = cursor.fetchone()[0]
        
        # 이미 존재하지 않으면 삽입
        if count == 0:
            query = """
            INSERT INTO Delivery_Option (price_id, request_datetime)
            VALUES (%s, %s)
            """
            cursor.execute(query, (price_id, request_datetime.strftime('%Y-%m-%d')))
        else:
            print(f"price_id {price_id}는 이미 Delivery_Option 테이블에 존재합니다. 중복 삽입을 방지합니다.")
    
    db.commit()

# Delivery_Option 테이블에 더미 데이터 삽입 (1000개 레코드 삽입 예시)
insert_delivery_options(1000)

# 연결 종료
cursor.close()
db.close()

print("더미 데이터 Delivery_Option 테이블에 삽입되었습니다!")
