import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

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

# ✅ (1) `customer_id` 목록 가져오기
cursor.execute("SELECT customer_id FROM Customer;")
customer_ids = [row[0] for row in cursor.fetchall()]  # ✅ 고객 ID 리스트

# ✅ (2) 상품 ID 범위 정의 (1 ~ 100000)
product_ids = list(range(1, 100001))  # ✅ 상품 ID 목록 (1부터 10만까지)

# ✅ (3) 랜덤 상품별 리뷰 개수 배정
total_reviews = 200000  # ✅ 전체 리뷰 개수
reviews_per_product = {}  # ✅ 각 상품별 리뷰 개수 저장

while total_reviews > 0:
    product_id = random.choice(product_ids)  # ✅ 랜덤 상품 선택
    review_count = random.randint(50, 1500)  # ✅ 50 ~ 1500개 사이의 랜덤 리뷰 개수 배정

    if total_reviews - review_count < 0:
        review_count = total_reviews  # ✅ 남은 개수보다 초과하면 조정

    if product_id in reviews_per_product:
        reviews_per_product[product_id] += review_count
    else:
        reviews_per_product[product_id] = review_count

    total_reviews -= review_count  # ✅ 남은 총 리뷰 개수 감소

# ✅ (4) 별점 & 리뷰 템플릿
star_ratings = [1, 2, 3, 4, 5]
review_templates = [
    "정말 만족스러워요! 재구매 의사 100%",
    "괜찮긴 한데 아쉬운 부분이 있네요.",
    "배송 빠르고 상품도 좋았어요!",
    "별로였어요. 다시는 안 살 것 같아요.",
    "가성비 최고! 추천합니다.",
    "상품 설명과 달라서 실망했어요.",
    "사용해보니 정말 만족스럽습니다.",
    "배송이 너무 오래 걸려요.",
    "포장이 꼼꼼하게 되어 있어서 좋았어요.",
    "이 가격에 이 퀄리티? 완전 득템입니다!"
]

# ✅ (5) 리뷰 데이터 생성 및 삽입 (배치 처리)
if customer_ids:
    batch_size = 10000  # ✅ 대량 삽입을 위한 배치 크기
    reviews_to_insert = []

    for product_id, count in reviews_per_product.items():
        for _ in range(count):
            customer_id = random.choice(customer_ids)  # ✅ 랜덤 고객 ID 선택
            star = random.choice(star_ratings)  # ✅ 랜덤 별점
            content = random.choice(review_templates)  # ✅ 랜덤 리뷰 내용

            created_at = fake.date_time_between(start_date="-1y", end_date="now")  # ✅ 최근 1년 내 작성된 리뷰
            updated_at = created_at + timedelta(days=random.randint(0, 30))  # ✅ 0~30일 후 랜덤 업데이트

            # ✅ 30% 확률로 이미지 포함
            image = f"review_{random.randint(1, 100)}.jpg" if random.random() < 0.3 else None

            reviews_to_insert.append((customer_id, product_id, star, content, created_at, updated_at, image))

            # ✅ 일정 개수마다 DB에 삽입 (배치 처리)
            if len(reviews_to_insert) >= batch_size:
                sql_review = """
                INSERT INTO Review (customer_id, product_id, star, content, created_at, updated_at, image)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.executemany(sql_review, reviews_to_insert)
                conn.commit()
                reviews_to_insert = []

    # ✅ 마지막 남은 데이터 삽입
    if reviews_to_insert:
        sql_review = """
        INSERT INTO Review (customer_id, product_id, star, content, created_at, updated_at, image)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(sql_review, reviews_to_insert)
        conn.commit()

    print(f"총 {sum(reviews_per_product.values())}개의 리뷰가 삽입되었습니다!")

# ✅ (6) 커서 및 연결 종료
cursor.close()
conn.close()

print("리뷰(Review) 데이터가 성공적으로 삽입되었습니다! 🚀")
