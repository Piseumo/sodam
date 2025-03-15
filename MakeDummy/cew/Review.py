import mysql.connector
from faker import Faker
import random

# ✅ Faker 설정 (한글 지원)
fake = Faker("ko_KR")

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# ✅ 온라인 주문에서 고객과 상품 ID 가져오기
cursor.execute("""
    SELECT oc.customer_id, ocp.cart_product_id
    FROM online_order oo
    JOIN Online_Cart oc ON oo.online_cart_id = oc.online_cart_id
    JOIN Online_Cart_Product ocp ON oc.online_cart_id = ocp.online_cart_id
""")
order_data = cursor.fetchall()  # [(customer_id, product_id), (customer_id, product_id), ...]

# ✅ 더미 리뷰 데이터 10,000개 생성
review_data = []
for _ in range(10000):
    customer_id, product_id = random.choice(order_data)  # 랜덤 주문 정보 선택
    star = random.randint(1, 5)  # 별점 1~5
    content = fake.text(max_nb_chars=200)  # 200자 내외의 리뷰 내용
    created_at = fake.date_time_this_year()  # 올해 작성된 날짜

    review_data.append((customer_id, product_id, star, content, created_at, created_at))

# ✅ 리뷰 데이터 삽입 SQL 실행
insert_query = """
    INSERT INTO Review (customer_id, product_id, star, content, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s)
"""
cursor.executemany(insert_query, review_data)

# ✅ 데이터 커밋 & 연결 종료
conn.commit()
cursor.close()
conn.close()

print("✅ 10,000개의 더미 리뷰 데이터 삽입 완료!")
