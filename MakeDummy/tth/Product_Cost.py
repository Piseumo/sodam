import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

def random_reason(nb_words=6):
    korean_words = [
        "공급가", "단가", "조정", "가격", "협상", "계약", 
        "수급", "증가", "감소", "변경", "이벤트", "할인", 
        "환율", "인상", "인하", "시세"
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

# Product 테이블에서 product_id 목록 가져오기
cursor.execute("SELECT product_id FROM Product")
product_ids = [row[0] for row in cursor.fetchall()]

# Product_Cost 더미 데이터 삽입
num_cost_entries = 100000
for _ in range(num_cost_entries):
    product_id = random.choice(product_ids)
    base_cost = random.randint(500, 70000)  # 기본 원가
    cost_type = random.choice(["Increase", "Decrease"])
    delta = random.randint(10, 3000)
    reason = random_reason(nb_words=6)
    
    if cost_type == "Increase":
        final_cost = base_cost + delta
    else:
        final_cost = max(base_cost - delta, 100)  # 최소 원가 100원 보장

    date_time = fake.date_time_between(start_date="-1y", end_date="now")

    sql = """
    INSERT INTO Product_Cost 
    (product_id, base_cost, type, delta, reason, final_cost, date_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (product_id, base_cost, cost_type, delta, reason, final_cost, date_time)
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ Product_Cost 더미 데이터 삽입 완료!")
