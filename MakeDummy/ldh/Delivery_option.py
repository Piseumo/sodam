import mysql.connector
import random
from datetime import datetime, timedelta

# MySQL 연결 설정
db = mysql.connector.connect(
    host="192.168.0.9",  
    port=3306,    
    user="root",   
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
        
        # Delivery_Option 테이블에 데이터 삽입
        query = """
        INSERT INTO Delivery_Option (price_id, request_datetime)
        VALUES (%s, %s)
        """
        cursor.execute(query, (price_id, request_datetime.strftime('%Y-%m-%d')))
    
    db.commit()

# Delivery_Option 테이블에 더미 데이터 삽입 (10개 레코드 삽입 예시)
insert_delivery_options(10)

# 연결 종료
cursor.close()
db.close()

print("✅ 더미 데이터가 Delivery_Option 테이블에 삽입되었습니다!")
