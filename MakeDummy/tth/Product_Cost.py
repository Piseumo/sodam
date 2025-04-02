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

# 🔁 테이블 초기화
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Product_Cost;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ 기존 Product_Cost 데이터 삭제 완료!")

# 🔍 Product_Price 테이블에서 product_id별 최신 current_price 가져오기
cursor.execute("""
    SELECT pp.product_id, pp.current_price
    FROM Product_Price pp
    JOIN (
        SELECT product_id, MAX(date_time) AS max_date
        FROM Product_Price
        GROUP BY product_id
    ) latest
    ON pp.product_id = latest.product_id AND pp.date_time = latest.max_date
""")

# 딕셔너리로 매핑: {product_id: current_price}
product_price_map = {row[0]: row[1] for row in cursor.fetchall()}
print(f"📦 가격 참조 가능한 상품 수: {len(product_price_map)}개")

# ✅ Product_Cost 더미 데이터 삽입
num_cost_entries = 100000
insert_count = 0

for _ in range(num_cost_entries):
    product_id = random.choice(list(product_price_map.keys()))
    max_price = product_price_map[product_id]

    # base_cost는 판매가의 60~85% 사이
    base_cost = int(max_price * random.uniform(0.6, 0.85))

    # delta는 base_cost의 최대 30%까지 (100원 단위)
    delta = random.randrange(100, max(200, int(base_cost * 0.3)), 100)

    cost_type = random.choice(["Increase", "Decrease"])
    reason = random_reason(nb_words=6)

    # 가격 타입에 따라 최종 원가 계산
    if cost_type == "Increase":
        final_cost = base_cost + delta
    else:
        final_cost = max(base_cost - delta, 100)

    # 🔒 final_cost가 판매가보다 크면 건너뜀
    if final_cost >= max_price:
        continue

    date_time = fake.date_time_between(start_date="-1y", end_date="now")

    sql = """
        INSERT INTO Product_Cost 
        (product_id, base_cost, type, delta, reason, final_cost, date_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (product_id, base_cost, cost_type, delta, reason, final_cost, date_time)
    cursor.execute(sql, values)
    insert_count += 1

conn.commit()
cursor.close()
conn.close()

print(f"✅ Product_Cost 더미 데이터 {insert_count:,}건 삽입 완료!")
