import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Faker 객체 생성
fake = Faker('ko_KR')

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
    # host="192.168.0.104",  
    host="192.168.0.9",  
    port=3306,   
    user="root",    
    password="1234", 
    database="sodam"
    # database=""
)

# 커서 생성
cursor = db.cursor()

# 데이터 삽입 쿼리
insert_query = """
    INSERT INTO Delivery_Car (number, status, insert_date, last_activity_date, insurance)
    VALUES (%s, %s, %s, %s, %s)
"""

# 상태별 비율 설정 (배열의 가중치를 설정)
status_list = ['배송가능', '수리중', '배송중', '고장']
weights = [0.5, 0.2, 0.2, 0.1]  # 각각 '배송가능' 50%, '수리중' 20%, '배송중' 20%, '고장' 10%

# 보험 여부 비율 설정 (80% 확률로 True, 20% 확률로 False)
insurance_weights = [0.8, 0.2]  # 80% True, 20% False

# 한글 차량 번호판 생성 함수
def generate_korean_license_plate():
    # 지역 코드 목록
    # cities = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']
    cities = [ '대구']
    
    # 번호판의 첫 번째와 두 번째 자리에 올 수 있는 한글 자음
    korean_characters = ['가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하']
    
    # 지역 코드 (예: 서울, 부산 등)
    city = random.choice(cities)
    
    # 차량 번호 (3자리 숫자)
    num = random.randint(100, 999)
    
    # 한글 자음 (예: 가, 나, 다 등)
    korean_char = random.choice(korean_characters)
    
    # 차량 등록 번호 (4자리 숫자)
    reg_num = random.randint(1000, 9999)
    
    # 최종 번호판 형식: 지역 + 번호 + 자음 + 등록번호
    license_plate = f"{city} {num} {korean_char} {reg_num}"
    
    return license_plate

# 랜덤 날짜와 시간 생성 함수 (특정 범위 내에서)
def generate_random_datetime(start_year=2024):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()  # 현재 날짜로 설정
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)  # 현재 날짜를 넘지 않도록 설정
    random_date = start_date + timedelta(days=random_days)
    
    # 랜덤 시간 (시, 분, 초)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    
    # 생성된 날짜에 시간, 분, 초 추가
    random_datetime = random_date.replace(hour=random_hour, minute=random_minute, second=random_second)
    
    return random_datetime

for i in range(15):
    # 가짜 차량 번호 생성
    number = generate_korean_license_plate()
    
    # 비율에 따라 상태 선택
    status = random.choices(status_list, weights=weights, k=1)[0]
    
    # insert_date는 랜덤 날짜와 시간으로 생성 (2024년 1월 1일부터 현재 날짜까지)
    insert_date = generate_random_datetime()

    # 처음 삽입될 때 last_activity_date는 NULL로 설정
    last_activity_date = None
    
    # 비율에 따라 보험 여부 선택 (80% True, 20% False)
    # insurance = random.choices([True, False], weights=insurance_weights, k=1)[0]

    insurance = 1

    # 데이터 삽입
    cursor.execute(insert_query, (number, status, insert_date, last_activity_date, insurance))
    db.commit()  # 데이터베이스에 커밋 (변경사항 저장)

    # 출력 (옵션)
    print(f"Inserted car {i+1}: {number}, {status}, {insert_date}, {last_activity_date}, {insurance}")

# 커서와 데이터베이스 연결 종료
cursor.close()
db.close()

print("✅ 배송차량량 데이터 삽입 완료!")
