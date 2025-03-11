import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE offline_card;")
cursor.execute("TRUNCATE TABLE offline_cancels;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print(" 기존 데이터 삭제 완료!")

# ---------- Offline_Card 더미 데이터 삽입 ----------
num_offline_card = 500000
card_codes = ["BC1", "SH2", "KM3", "WR4", "LG5"]  # 3자리 코드 예시
card_names = ["비씨", "신한", "국민", "우리", "하나"]
acqu_card_codes = ["AC1", "AC2", "AC3", "AC4", "AC5"]
acqu_card_names = ["신한카드", "국민카드", "우리카드", "하나카드", "비씨카드"]

for _ in range(num_offline_card):
    card_code = random.choice(card_codes)
    card_name = random.choice(card_names)
    # 카드번호: 앞 6자리, 가운데 ******, 마지막 4자리
    prefix = "".join([str(random.randint(0, 9)) for _ in range(6)])
    suffix = "".join([str(random.randint(0, 9)) for _ in range(4)])
    card_num = f"{prefix}******{suffix}"
    card_quota = random.choice(["0", "2", "3", "6", "12"])
    is_interest_free = random.choice([0, 1])
    card_type = random.choice(["credit", "check"])
    can_part_cancel = random.choice([0, 1])
    acqu_card_code = random.choice(acqu_card_codes)
    acqu_card_name = random.choice(acqu_card_names)
    
    sql = """
    INSERT INTO Offline_Card 
    (card_code, card_name, card_num, card_quota, is_interest_free, card_type, can_part_cancel, acqu_card_code, acqu_card_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (card_code, card_name, card_num, card_quota, is_interest_free, card_type, can_part_cancel, acqu_card_code, acqu_card_name)
    cursor.execute(sql, values)

conn.commit()
print("✅ Offline_Card 데이터 삽입 완료!")

# ---------- offline_cancels 더미 데이터 삽입 ----------
num_offline_cancels = 100000
cancel_reasons = ["고객 요청", "상품 품절", "시스템 오류", "취소 요청", "기타"]

for _ in range(num_offline_cancels):
    # tid: UUID 문자열을 30자 이내로 사용
    tid = fake.uuid4()[:30]
    # amount: 1000원부터 100,000원 사이의 100원 단위
    amount = random.randrange(1000, 100001, 100)
    cancelled_at = fake.date_time_between(start_date="-1y", end_date="now")
    reason = random.choice(cancel_reasons)
    receipt_url = fake.url()
    # coupon_amt: None 또는 0원부터 5000원 사이의 100원 단위
    coupon_amt = random.choice([None, random.randrange(0, 5001, 100)])
    
    sql = """
    INSERT INTO offline_cancels
    (tid, amount, cancelled_at, reason, receipt_url, coupon_amt)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (tid, amount, cancelled_at, reason, receipt_url, coupon_amt)
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ offline_cancels 데이터 삽입 완료!")
