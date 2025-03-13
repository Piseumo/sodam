import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = conn.cursor()

# ✅ 1. Customer ID 가져오기 (FK 제약 조건을 위해 기존 데이터 사용)
cursor.execute("SELECT customer_id FROM customer")
customer_ids = [row[0] for row in cursor.fetchall()]

# ✅ 고객 ID가 비어있을 때 예외 처리
if not customer_ids:
    print("❌ Error: No customer data found in the customer table.")
    exit()

# ✅ 2. Earned 포인트 데이터 삽입
earned_points = []  # Used/Expired 처리를 위한 저장소
for _ in range(500000):  # 50만 개의 Earned 포인트 생성
    customer_id = random.choice(customer_ids)
    total_amount = random.randint(1000, 1000000)  # ✅ 결제 금액 (1,000원 ~ 1,000,000원)
    delta = random.randint(10, 5000)  # ✅ Earned 포인트 (양수)

    # ✅ 현재 고객의 current_points 조회
    cursor.execute("SELECT COALESCE(MAX(current_points), 0) FROM Point WHERE customer_id = %s", (customer_id,))
    current_points = cursor.fetchone()[0]

    # ✅ Earned 포인트 적립 날짜 (현재 날짜 기준 2년 전까지 랜덤 설정)
    earned_date = fake.date_time_between(start_date="-2y", end_date="now")

    # ✅ total_points 업데이트 (current_points + delta)
    total_points = current_points + delta

    # ✅ Earned 포인트 삽입
    sql = """
        INSERT INTO Point 
        (customer_id, total_amount, type, delta, total_points, current_points, date_time) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (customer_id, total_amount, 'Earned', delta, total_points, current_points, earned_date)
    cursor.execute(sql, values)

    # ✅ Used/Expired 처리를 위해 저장
    earned_points.append((customer_id, delta, earned_date, total_points))

# ✅ 3. Used 포인트 데이터 삽입 (Earned 포인트에서 일부 사용)
for customer_id, earned_delta, earned_date, earned_total_points in earned_points:
    if random.random() < 0.6:  # ✅ 60% 확률로 사용 (Used 데이터 삽입)
        used_amount = random.randint(1, earned_delta)  # ✅ Earned 포인트 중 일부 사용
        used_date = earned_date + timedelta(days=random.randint(30, 330))  # Earned 후 1~11개월 사이 사용

        # ✅ current_points는 Earned 시점의 total_points 사용
        current_points = earned_total_points

        # ✅ total_points 업데이트 (current_points - used_amount)
        total_points = max(0, current_points - used_amount)

        # ✅ Used 포인트 삽입 (음수 값)
        sql = """
            INSERT INTO Point 
            (customer_id, total_amount, type, delta, total_points, current_points, date_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (customer_id, 0, 'Used', -used_amount, total_points, current_points, used_date)  
        cursor.execute(sql, values)

        remaining_delta = earned_delta - used_amount
    else:
        remaining_delta = earned_delta  # Used 없이 Expired 진행

    # ✅ 4. Expired 포인트 데이터 삽입 (Earned 후 1년 경과한 포인트 소멸)
    expired_date = earned_date + timedelta(days=365)  # Earned한 지 1년 후

    if expired_date < datetime.now() and remaining_delta > 0:
        # ✅ current_points는 Earned 시점의 total_points 사용
        current_points = earned_total_points

        # ✅ total_points 업데이트 (current_points - remaining_delta)
        total_points = max(0, current_points - remaining_delta)

        sql = """
            INSERT INTO Point 
            (customer_id, total_amount, type, delta, total_points, current_points, date_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (customer_id, 0, 'Expired', -remaining_delta, total_points, current_points, expired_date)  
        cursor.execute(sql, values)

# 변경 사항 커밋
conn.commit()
cursor.close()
conn.close()

print("✅ Earned, Used 및 Expired 포인트 데이터가 MySQL에 삽입되었습니다!")
