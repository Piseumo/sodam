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
cursor.execute("SELECT customer_id FROM Customer")
customer_ids = [row[0] for row in cursor.fetchall()]

# ✅ 2. 고객 시나리오 설정 (각 그룹별 고객 ID 분류)
total_customers = len(customer_ids)
svip_customers = random.sample(customer_ids, int(total_customers * 0.1))  # 10% SVIP 고객
vvip_customers = random.sample(
    list(set(customer_ids) - set(svip_customers)), 
    int(total_customers * 0.2)
)  # 20% VVIP 고객
vip_customers = random.sample(
    list(set(customer_ids) - set(svip_customers) - set(vvip_customers)), 
    int(total_customers * 0.2)
)  # 20% VIP 고객
normal_customers = list(
    set(customer_ids) - set(svip_customers) - set(vvip_customers) - set(vip_customers)
)  # 나머지 50% Normal 고객

# ✅ 3. 등급 산정 기준 설정 함수
def get_grade_name(accumulated_amount):
    if accumulated_amount <= 50000:
        return "Normal"
    elif accumulated_amount <= 100000:
        return "VIP"
    elif accumulated_amount <= 300000:
        return "VVIP"
    else:
        return "SVIP"

# ✅ 4. Grade 더미 데이터 생성 (약 50만 건)
target_data_count = 300000

for _ in range(target_data_count):
    # ✅ 다양한 고객 그룹에서 고객 ID 선택
    random_choice = random.random()
    
    if random_choice < 0.1:  # 10% 확률로 SVIP 고객
        customer_id = random.choice(svip_customers)
        accumulated_amount = random.randint(300001, 1000000)
    elif random_choice < 0.3:  # 20% 확률로 VVIP 고객
        customer_id = random.choice(vvip_customers)
        accumulated_amount = random.randint(100001, 300000)
    elif random_choice < 0.5:  # 20% 확률로 VIP 고객
        customer_id = random.choice(vip_customers)
        accumulated_amount = random.randint(50001, 100000)
    else:  # 50% 확률로 Normal 고객
        customer_id = random.choice(normal_customers)
        accumulated_amount = random.randint(0, 50000)
    
    # ✅ 등급 및 업데이트 날짜 설정
    grade_name = get_grade_name(accumulated_amount)
    last_update = fake.date_time_between(start_date="-1y", end_date="now")

    # ✅ reason 설정 (자동 산정 or 없음)
    reason = "누적 결제액에 따른 자동 등급 산정" if grade_name != "Normal" else None

    # ✅ 데이터 삽입
    sql = """
    INSERT INTO Grade (customer_id, name, last_update, accumulated_amount, reason) 
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (customer_id, grade_name, last_update, accumulated_amount, reason)
    cursor.execute(sql, values)

    # ✅ 일정량마다 커밋 (메모리 사용 최적화)
    if _ % 10000 == 0:
        conn.commit()

# ✅ 최종 커밋
conn.commit()
print("✅ 다양한 시나리오의 Grade 데이터 약 150만 건이 삽입되었습니다!")

cursor.close()
conn.close()
