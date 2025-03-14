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
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

# 1. Product_Price 데이터 삽입

# Product 테이블에서 product_id 목록 가져오기
cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]

num_price_entries = 200000
for _ in range(num_price_entries):
    product_id = random.choice(product_ids)
    current_price = random.randrange(1000, 100001, 10)
    price_type = random.choice(["Increase", "Decrease"])
    delta = random.randrange(10, 5001, 10)
    reason = random_reason(nb_words=6)  # 한국어 단어 조합으로 reason 생성
    if price_type == "Increase":
        final_price = current_price + delta
    else:
        final_price = max(current_price - delta, 1000)
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

num_discount_entries = 100000
for _ in range(num_discount_entries):
    price_id = random.choice(price_ids)
    rate = random.randint(5, 50)
    reason = random_reason(nb_words=5)  # 할인 사유도 한국어 단어 조합
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
