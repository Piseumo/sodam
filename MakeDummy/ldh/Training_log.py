import mysql.connector
from faker import Faker
import random

db = mysql.connector.connect(
    host="localhost",   
    # host="192.168.0.9",   
    # port=3306,  
    user="root",    
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# Faker 객체 생성
fake = Faker('ko_KR')  # 한국어로 더미 데이터 생성

# Training_Log 테이블에 더미 데이터 삽입
def insert_training_logs(batch_size=100):
    offset = 0

    while True:
        # 배치 크기만큼 driver_id를 가져오기
        cursor.execute(f"SELECT driver_id FROM Delivery_Driver LIMIT {batch_size} OFFSET {offset}")
        driver_ids = [row[0] for row in cursor.fetchall()]

        # driver_ids가 없으면 더 이상 가져올 데이터가 없다는 의미
        if not driver_ids:
            break

        # 훈련 로그 데이터 삽입
        for driver_id in driver_ids:
            # 이미 훈련 기록이 있는지 확인
            cursor.execute("SELECT COUNT(*) FROM Training_Log WHERE driver_id = %s", (driver_id,))
            existing_records = cursor.fetchone()[0]

            # 훈련 기록이 없다면 훈련 로그 삽입
            if existing_records == 0:
                # complete_date를 현재 날짜보다 1년 이내의 랜덤 날짜로 생성
                complete_date = fake.date_between(start_date="-1y", end_date="today")

                query = """
                INSERT INTO Training_Log (driver_id, complete_date)
                VALUES (%s, %s)
                """
                cursor.execute(query, (driver_id, complete_date))

        db.commit()  # 배치 후 한번에 커밋
        offset += batch_size  # 다음 배치를 위해 offset 증가

# Delivery_Driver 테이블에 있는 모든 배송기사의 id에 대해 훈련 로그 삽입
insert_training_logs()

# 연결 종료
cursor.close()
db.close()

print("✅ 트레이닝 로그 데이터 삽입 완료!")