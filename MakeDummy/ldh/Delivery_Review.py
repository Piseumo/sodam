import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Faker 객체 생성
fake = Faker('ko_KR')

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

# 커서 생성
cursor = db.cursor()

# 데이터 삽입 쿼리
insert_query = """
    INSERT INTO Delivery_Review (point, content, insert_date, update_date, delete_date, delivery_id)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

# 포인트 비율 설정
point_weights = [0.01, 0.02, 0.07, 0.7, 0.2]  # 포인트 1, 2, 3, 4, 5의 비율 (각각 1%, 2%, 7%, 70%, 20%)

# 상태별 리뷰 내용
def generate_good_review():
    return f"배송이 빠르고 상태가 좋았습니다. {fake.sentence(nb_words=6)}"

def generate_neutral_review():
    return f"배송은 괜찮았지만, 제품에 조금 아쉬운 점이 있었습니다. {fake.sentence(nb_words=6)}"

def generate_bad_review():
    return f"배송이 지연되었고, 제품 상태가 매우 불량했습니다. {fake.sentence(nb_words=6)}"

# 포인트가 1일 때 부정적인 내용
def generate_bad_point_review():
    return f"배송은 예상보다 늦었고, 제품 상태는 최악이었습니다. {fake.sentence(nb_words=6)}"

# 포인트가 3일 때 중립적인 내용
def generate_neutral_point_review():
    return f"배송은 적당했지만, 제품 상태는 기대 이하였습니다. {fake.sentence(nb_words=6)}"

# 리뷰 작성 함수
def generate_review(delivery_id):
    # 이미 해당 delivery_id에 리뷰가 있는지 확인
    cursor.execute("SELECT COUNT(*) FROM Delivery_Review WHERE delivery_id = %s", (delivery_id,))
    result = cursor.fetchone()
    
    if result[0] > 0:
        print(f"Review already exists for delivery_id {delivery_id}. Skipping.")
        return  # 이미 리뷰가 있다면 추가하지 않음
    
    point = random.choices([1, 2, 3, 4, 5], weights=point_weights, k=1)[0]
    
    # 포인트에 따른 리뷰 내용 생성
    if point == 1:
        content = generate_bad_point_review()
    elif point == 2:
        content = generate_neutral_point_review()
    elif point == 3:
        content = generate_neutral_review()
    elif point == 4:
        content = generate_good_review()
    elif point == 5:
        content = generate_good_review()

    # 등록 날짜 (Delivery의 end_date로부터 1주일 이내 랜덤 날짜 생성)
    cursor.execute("SELECT end_date FROM Delivery WHERE delivery_id = %s", (delivery_id,))
    result = cursor.fetchone()
    if result:
        end_date = result[0]
        random_days = random.randint(0, 7)  # 1주일 이내로 날짜 랜덤 선택
        insert_date = end_date - timedelta(days=random_days)
        
        # 업데이트 날짜 및 삭제 날짜 (10% 확률로 업데이트 및 삭제 날짜 생성)
        update_date = None
        delete_date = None
        
        # 10% 확률로 delete_date 생성
        if random.random() < 0.1:  
            delete_date = insert_date + timedelta(days=random.randint(1, 7))  # insert_date보다 나중 날짜
        
        # delete_date가 존재하는 경우, update_date는 생성하지 않음
        if delete_date:
            update_date = None
        else:
            # 10% 확률로 update_date 생성 (delete_date가 없는 경우만)
            if random.random() < 0.1:  
                update_date = insert_date + timedelta(days=random.randint(1, 7))  # insert_date보다 나중 날짜

        # delete_date가 존재하면 update_date는 delete_date와 동일하거나 이전 날짜여야 한다.
        if update_date and delete_date and update_date > delete_date:
            update_date = delete_date  # update_date는 delete_date보다 크지 않아야 함

        # 데이터 삽입
        cursor.execute(insert_query, (point, content, insert_date, update_date, delete_date, delivery_id))
        db.commit()

# Delivery_Review 테이블에 15개의 더미 데이터 삽입
cursor.execute("SELECT delivery_id FROM Delivery WHERE status = '배송완료' LIMIT 15")  # '배송완료' 상태의 데이터만 추출
delivery_ids = cursor.fetchall()

for delivery_id in delivery_ids:
    generate_review(delivery_id[0])
    print(f"Review for delivery {delivery_id[0]} inserted!")

# 커서와 데이터베이스 연결 종료
cursor.close()
db.close()

print("✅ Delivery_Review 데이터 삽입 완료!")
