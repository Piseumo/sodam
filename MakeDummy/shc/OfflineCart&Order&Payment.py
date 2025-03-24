import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

# 외래키 제약 조건 비활성화
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Offline_Cart;")
cursor.execute("TRUNCATE TABLE Offline_Order;")
cursor.execute("TRUNCATE TABLE Offline_Payment;")
conn.commit()

print(" 기존 데이터 삭제 완료!")

# ---------- Offline_Cart 데이터 삽입 ----------
num_offline_cart = 500000
for _ in range(num_offline_cart):
    # c_id: 고객 ID (임의의 1~1000 사이 값)
    c_id = random.randint(1, 1000)
    # total_price: 1000원부터 100,000원 사이, 100원 단위
    total_price = random.randrange(1000, 100001, 100)
    
    sql = "INSERT INTO Offline_Cart (c_id, total_price) VALUES (%s, %s)"
    cursor.execute(sql, (c_id, total_price))

conn.commit()
print("✅ Offline_Cart 데이터 삽입 완료!")

# ---------- Offline_Order 데이터 삽입 ----------
# Offline_Cart 테이블에서 생성된 offline_cart_id 목록 가져오기
cursor.execute("SELECT offline_cart_id FROM Offline_Cart")
offline_cart_ids = [row[0] for row in cursor.fetchall()]

num_offline_order = 1000000  # 예시: 100개의 데이터
for _ in range(num_offline_order):
    offline_cart_id = random.choice(offline_cart_ids)
    # point_id: 임의의 1~1000 사이 값
    point_id = random.randint(1, 1000)
    pay_method = random.choice(["카드 결제", "현금 결제"])
    status = random.choice(["결제 대기", "결제 완료"])
    
    sql = "INSERT INTO Offline_Order (offline_cart_id, point_id, pay_method, status) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (offline_cart_id, point_id, pay_method, status))

conn.commit()
print("✅ Offline_Order 데이터 삽입 완료!")

# ---------- Offline_Payment 데이터 삽입 ----------
# Offline_Order 테이블에서 생성된 order_id 목록 가져오기
cursor.execute("SELECT order_id FROM Offline_Order")
offline_order_ids = [row[0] for row in cursor.fetchall()]

# Offline_Card 테이블에서 card_id 목록 가져오기 (없으면 임의의 값 1~100)
cursor.execute("SELECT card_id FROM Offline_Card")
card_ids = [row[0] for row in cursor.fetchall()]
if not card_ids:
    card_ids = list(range(1, 101))

# offline_cancels 테이블에서 cancels_id 목록 가져오기 (없으면 임의의 값 1~100)
cursor.execute("SELECT cancels_id FROM offline_cancels")
cancels_ids = [row[0] for row in cursor.fetchall()]
if not cancels_ids:
    cancels_ids = list(range(1, 101))

num_offline_payment = 100000
for _ in range(num_offline_payment):
    order_id = random.choice(offline_order_ids)
    card_id = random.choice(card_ids)
    cancels_id = random.choice(cancels_ids)
    
    result_code = random.choice(["0000", "1001", "2002", "3003"])
    result_message = fake.sentence(nb_words=6)
    tid = fake.uuid4()[:30]
    cancelled_tid = None  # 취소 거래 키가 없는 경우
    edi_date = fake.date_time_between(start_date="-1y", end_date="now")
    signature = fake.sha256()
    status_payment = random.choice(["paid", "ready", "failed", "cancelled", "partialCancelled", "expired"])
    paid_at = fake.date_time_between(start_date="-1y", end_date="now")
    failed_at = fake.date_time_between(start_date="-1y", end_date="now")
    cancelled_at = fake.date_time_between(start_date="-1y", end_date="now")
    pay_method_enum = random.choice(["card", "vbank", "naverpay", "kakaopay", "payco", "ssgpay", "samsungpay"])
    # amount: 1000원부터 300,000원 사이, 100원 단위
    amount = random.randrange(1000, 300001, 100)
    # balance_amt: 0원부터 amount까지 100원 단위
    balance_amt = random.randrange(0, amount+1, 100)
    goods_name = random.choice(["상품A", "상품B", "상품C", fake.catch_phrase()])
    mall_reserved = fake.text(max_nb_chars=50)
    use_escrow = random.choice([0, 1])
    currency = "KRW"
    channel = random.choice(["pc", "mobile"])
    approve_no = fake.bothify(text='??????')  # 6자리 임의 문자열
    buyer_name = fake.name()
    buyer_tel = fake.phone_number()
    buyer_email = fake.email()
    issued_cash_receipt = random.choice([0, 1])
    receipt_url = fake.url()
    
    sql = """
    INSERT INTO Offline_Payment (
        result_code, result_message, tid, cancelled_tid, order_id, card_id, cancels_id,
        edi_date, signature, status, paid_at, failed_at, cancelled_at, pay_method,
        amount, balance_amt, goods_name, mall_reserved, use_escrow, currency, channel,
        approve_no, buyer_name, buyer_tel, buyer_email, issued_cash_receipt, receipt_url
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    values = (
        result_code, result_message, tid, cancelled_tid, order_id, card_id, cancels_id,
        edi_date, signature, status_payment, paid_at, failed_at, cancelled_at, pay_method_enum,
        amount, balance_amt, goods_name, mall_reserved, use_escrow, currency, channel,
        approve_no, buyer_name, buyer_tel, buyer_email, issued_cash_receipt, receipt_url
    )
    cursor.execute(sql, values)

conn.commit()

cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # 외래키 제약 조건 재활성화

cursor.close()
conn.close()

print("✅ Offline_Payment 데이터 삽입 완료!")
