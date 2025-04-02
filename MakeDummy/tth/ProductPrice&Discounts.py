import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

def random_reason(nb_words=6):
    korean_words = [
        "가격", "변동", "할인", "특가", "신상품", "인기", 
        "세일", "이벤트", "재고", "변경", "수정", "프로모션", 
        "업데이트", "상승", "하락", "조정"
    ]
    return " ".join(random.choices(korean_words, k=nb_words))

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port=50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

# 🔁 테이블 초기화
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Discounts;")
cursor.execute("TRUNCATE TABLE Product_Price;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ 기존 Product_Price, Discounts 데이터 삭제 완료!")

# 1. Product_Price 데이터 삽입

cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]

num_price_entries = 200000
for _ in range(num_price_entries):
    product_id = random.choice(product_ids)
    current_price = random.randrange(500, 10001, 100)  # ✅ 100원 단위
    price_type = random.choice(["Increase", "Decrease"])
    delta = random.randrange(100, 1001, 100)  # ✅ 100원 단위
    reason = random_reason(nb_words=6)

    if price_type == "Increase":
        final_price = current_price + delta
    else:
        final_price = max(current_price - delta, 500)

    date_time = fake.date_time_between(start_date="-1y", end_date="now")

    sql = """
    INSERT INTO Product_Price 
    (product_id, current_price, type, delta, reason, final_price, date_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (product_id, current_price, price_type, delta, reason, final_price, date_time)
    cursor.execute(sql, values)

conn.commit()
print("✅ Product_Price 데이터 삽입 완료!")

# 2. Discounts 데이터 삽입

cursor.execute("SELECT price_id FROM Product_Price")
price_ids = [row[0] for row in cursor.fetchall()]

num_discount_entries = 10000
for _ in range(num_discount_entries):
    price_id = random.choice(price_ids)
    rate = random.randint(5, 50)
    reason = random_reason(nb_words=5)
    start = fake.date_time_between(start_date="-30d", end_date="now")
    end = fake.date_time_between(start_date="now", end_date="+30d")

    sql = """
    INSERT INTO Discounts
    (rate, reason, start, end, price_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (rate, reason, start, end, price_id)
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ Discounts 데이터 삽입 완료!")
