import mysql.connector
from faker import Faker
import random

db = mysql.connector.connect(
    host="192.168.0.9",   
    port=3306,  
    user="root",    
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# Faker 객체 생성
fake = Faker('ko_KR')  # 한국어로 더미 데이터 생성

# Training_Log 테이블에 더미 데이터 삽입
def insert_training_logs(num_records, batch_size=100):
    # 배치 크기만큼 driver_id를 가져와서 한 번에 처리
    offset = 0

    while offset < num_records:
        # 배치 크기만큼 driver_id를 가져오기
        cursor.execute(f"SELECT driver_id FROM Delivery_Driver LIMIT {batch_size} OFFSET {offset}")
        driver_ids = [row[0] for row in cursor.fetchall()]

        # driver_ids가 없으면 더 이상 가져올 데이터가 없다는 의미
        if not driver_ids:
            break

        # 훈련 로그 데이터 삽입
        for _ in range(min(batch_size, num_records - offset)):
            driver_id = random.choice(driver_ids)  # 배치에서 랜덤으로 driver_id 선택
            # complete_date를 현재 날짜보다 1년 이내의 랜덤 날짜로 생성
            complete_date = fake.date_between(start_date="-1y", end_date="today")  # 1년 이내의 날짜로 설정

            query = """
            INSERT INTO Training_Log (driver_id, complete_date)
            VALUES (%s, %s)
            """
            cursor.execute(query, (driver_id, complete_date))
        
        db.commit()  # 배치 후 한번에 커밋
        offset += batch_size  # 다음 배치를 위해 offset 증가

# 100개의 훈련 로그 더미 데이터 생성
insert_training_logs(100)

# 연결 종료
cursor.close()
db.close()
