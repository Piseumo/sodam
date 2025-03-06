import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# 외래키 제약 조건 비활성화
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# 1. Offline_Cash 데이터 삽입

# Offline_Order 테이블에서 order_id 목록 가져오기
cursor.execute("SELECT order_id FROM Offline_Order")
order_ids = [row[0] for row in cursor.fetchall()]
if not order_ids:
    order_ids = list(range(1, 101))  # 임의 값: 1~100

num_offline_cash = 100  # 예시: 100개의 데이터
for _ in range(num_offline_cash):
    order_id = random.choice(order_ids)
    # amount: 1000원부터 300,000원 사이, 100원 단위
    amount = random.randrange(1000, 300001, 100)
    currency = "KRW"
    pay_date = fake.date_time_between(start_date="-1y", end_date="now")
    status = random.choice(["PENDING", "COMPLETE", "CANCELED"])
    # created_at는 기본값 사용 (또는 fake.date_time_between 등으로 생성)
    # cash_receipt_request_num와 cash_receipt_approval_num: 가끔 None, 가끔 임의 문자열
    cash_receipt_request_num = random.choice([None, fake.bothify(text="REQ-####")])
    cash_receipt_approval_num = random.choice([None, fake.bothify(text="APR-####")])
    
    sql = """
    INSERT INTO offline_cash 
    (order_id, amount, currency, pay_date, status, cash_receipt_request_num, cash_receipt_approval_num)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (order_id, amount, currency, pay_date, status, cash_receipt_request_num, cash_receipt_approval_num)
    cursor.execute(sql, values)

conn.commit()
print("✅ offline_cash 데이터 삽입 완료!")

# 2. Offline_Cart_Product 데이터 삽입

# Offline_Cart 테이블에서 offline_cart_id 목록 가져오기
cursor.execute("SELECT offline_cart_id FROM Offline_Cart")
offline_cart_ids = [row[0] for row in cursor.fetchall()]
if not offline_cart_ids:
    offline_cart_ids = list(range(1, 101))  # 임의 값: 1~100

# Store_Inventory 테이블에서 inventory_id 목록 가져오기
cursor.execute("SELECT inventory_id FROM Store_Inventory")
inventory_ids = [row[0] for row in cursor.fetchall()]
if not inventory_ids:
    inventory_ids = list(range(1, 101))  # 임의 값: 1~100

num_cart_products = 100  # 예시: 100개의 데이터
for _ in range(num_cart_products):
    offline_cart_id = random.choice(offline_cart_ids)
    inventory_id = random.choice(inventory_ids)
    quantity = random.randint(1, 10)  # 수량 1~10
    # price: 100원 단위, 100원 ~ 10,000원 사이
    price = random.randrange(100, 100001, 100)
    
    sql = """
    INSERT INTO Offline_Cart_Product 
    (offline_cart_id, inventory_id, quantity, price)
    VALUES (%s, %s, %s, %s)
    """
    values = (offline_cart_id, inventory_id, quantity, price)
    cursor.execute(sql, values)

conn.commit()

# 외래키 제약 조건 재활성화
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

cursor.close()
conn.close()

print("✅ Offline_Cart_Product 데이터 삽입 완료!")
