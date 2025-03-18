import mysql.connector
import random
from faker import Faker  # ✅ Faker 가져오기

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

# ✅ 온라인 주문에서 고객 ID 가져오기 (수정됨)
cursor.execute("""
    SELECT DISTINCT oc.customer_id
    FROM online_order oo
    JOIN Online_Cart oc ON oo.online_cart_id = oc.online_cart_id
""")
customer_data = [row[0] for row in cursor.fetchall()]  # ✅ 고객 ID 리스트

# ✅ ⭐ 리뷰 스타일 데이터
positive_reviews = [
    "상품이 너무 좋아요! 기대 이상이에요 😊",
    "배송이 빠르고, 품질도 만족스럽네요!",
    "생각보다 훨씬 고퀄리티예요. 다음에도 구매할게요!",
    "포장이 꼼꼼하게 되어 있어서 상태가 정말 좋았어요!",
    "가성비 최고! 이런 가격에 이런 품질이라니, 강추합니다!"
]

neutral_reviews = [
    "그냥 무난해요. 가격 대비 괜찮은 것 같아요.",
    "딱 예상했던 정도의 품질입니다.",
    "배송은 빠르지만 상품이 특별히 좋은지는 모르겠어요.",
    "가격대비 나쁘지 않아요. 특별히 좋은 점은 모르겠어요.",
    "그냥 그런 무난한 상품입니다."
]

negative_reviews = [
    "기대했는데 조금 실망이에요. 품질이 생각보다 별로네요.",
    "포장이 허술했어요. 개선이 필요할 듯합니다.",
    "배송이 너무 느려서 불편했어요.",
    "사진과 실물이 많이 달라요. 다시 구매할지는 고민해봐야겠네요.",
    "상품이 불량이 왔어요. 교환 신청해야 할 것 같아요."
]

# ✅ 더미 리뷰 데이터 15,000개 생성
review_data = []

for _ in range(15000):
    customer_id = random.choice(customer_data)  # 랜덤 고객 선택
    star = random.randint(1, 5)  # 별점 1~5
    
    # ⭐ 별점에 따라 리뷰 내용 선택
    if star >= 4:
        content = random.choice(positive_reviews)
    elif star == 3:
        content = random.choice(neutral_reviews)
    else:
        content = random.choice(negative_reviews)

    created_at = fake.date_time_this_year()  # ✅ 올해 작성된 날짜
    review_data.append((customer_id, 8460, star, content, created_at, created_at))

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

print(f"✅ 15,000개의 자연스러운 더미 리뷰 데이터 삽입 완료! (모든 리뷰가 product_id = 8460)")
