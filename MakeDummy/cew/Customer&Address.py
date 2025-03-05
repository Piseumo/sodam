import mysql.connector
from faker import Faker
import random
import re

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# MySQL 연결 설정
conn = mysql.connector.connect(
    #host="192.168.0.104",      
    host="localhost",      
    #user="my_user",           
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = conn.cursor()

login_type = ['Form', 'Kakao', 'Google']
daegu_districts = ["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"]


# ✅ 고객 ID 저장 리스트
customer_ids = []  

# ✅ 1. 고객 데이터 삽입
for _ in range(1000000):
    name = fake.name()
    email = fake.email()
    phone = "010-" + fake.numerify("####-####")  # ✅ 010으로 시작하는 한국 휴대폰 번호
    login_type_value = random.choice(login_type)
    password = fake.password() if login_type_value == "Form" else None

    sql = "INSERT INTO customer (name, email, phone, password, login_type) VALUES (%s, %s, %s, %s, %s)"
    values = (name, email, phone, password, login_type_value)
    
    cursor.execute(sql, values)

    # ✅ 방금 삽입된 고객 ID 저장 (매번 추가)
    customer_ids.append(cursor.lastrowid)

# 변경 사항 커밋
conn.commit()

print("✅ 고객 데이터가 MySQL에 삽입되었습니다!")

# ✅ 2. Delivery Address 테이블에 각 고객당 2개씩 배송지 정보 삽입
for customer_id in customer_ids:  # ✅ 고객 ID 리스트 순회
    for _ in range(3):  # ✅ 고객당 2개씩 주소 추가
        city = "대구광역시"
        district = random.choice(daegu_districts)

        full_address = fake.street_address()  # ex) "제주특별자치도 청주시 상당구 영동대가 196"

        # ✅ 띄어쓰기 기준으로 첫 두 단어 삭제 (예: "제주특별자치도 청주시 상당구 영동대가 196" → "상당구 영동대가 196")
        address_parts = full_address.split(" ")
        if len(address_parts) > 2:
            address = " ".join(address_parts[2:])  # ✅ 첫 두 단어 제거하고 나머지만 저장
        else:
            address = full_address  # ✅ 만약 2개 이하 단어면 원본 유지
        address2 = fake.address_detail()
        postal_code = fake.postcode()

        sql = """INSERT INTO delivery_address (customer_id, city, district, address, address2, postal_code, last_update)
                 VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""
        values = (customer_id, city, district, address, address2, postal_code)

        cursor.execute(sql, values)

# 변경 사항 커밋 & 연결 종료
conn.commit()
cursor.close()
conn.close()

print("✅ Delivery Address 데이터 삽입 완료!")
