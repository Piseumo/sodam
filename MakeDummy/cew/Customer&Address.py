import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

conn = mysql.connector.connect(
    host="112.222.157.156",      
    port=50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = conn.cursor()

login_type = ['Form', 'Kakao', 'Google']
daegu_districts = ["중구", "동구", "서구", "남구", "북구", "수성구", "달서구", "달성군"]
postal_code_prefix = {
    "중구": "40",
    "동구": "41",
    "서구": "42",
    "남구": "43",
    "북구": "44",
    "수성구": "45",
    "달서구": "46",
    "달성군": "47"
}

customer_ids = []

# 고객 데이터 10,000개 삽입
for _ in range(10000):
    name = fake.name()
    email = fake.email()
    phone = "010-" + fake.numerify("####-####")
    login_type_value = random.choice(login_type)
    password = fake.password() if login_type_value == "Form" else None

    cursor.execute(
        "INSERT INTO Customer (name, email, phone, password, login_type) VALUES (%s, %s, %s, %s, %s)",
        (name, email, phone, password, login_type_value)
    )

    customer_ids.append(cursor.lastrowid)

conn.commit()
print("고객 데이터 10,000건 삽입 완료!")

# 각 고객당 배송지 4개 삽입 (기본 1개, 추가 3개)
for customer_id in customer_ids:
    for address_count in range(4):
        city = "대구광역시"
        district = random.choice(daegu_districts)

        full_address = fake.street_address()
        address_parts = full_address.split(" ")
        address = " ".join(address_parts[2:]) if len(address_parts) > 2 else full_address

        address2 = fake.address_detail()

        postal_prefix = postal_code_prefix[district]
        postal_code = postal_prefix + fake.numerify("###")

        addr_type = "기본" if address_count == 0 else "추가"

        cursor.execute(
            """INSERT INTO Delivery_Address
            (customer_id, city, district, address, address2, postal_code, type, last_update)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
            (customer_id, city, district, address, address2, postal_code, addr_type)
        )

conn.commit()
cursor.close()
conn.close()

print("배송지 데이터 삽입 완료!")
