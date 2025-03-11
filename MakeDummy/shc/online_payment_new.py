import mysql.connector
from faker import Faker
import random
import string
from datetime import timedelta

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)

cursor = conn.cursor()

# 간편결제 제공사 목록
payment_providers = [
    "TOSSPAY", "NAVERPAY", "SAMSUNGPAY", "APPLEPAY", "LPAY",
    "KAKAOPAY", "PINPAY", "PAYCO", "SSG"
]

# 실패 코드 목록
failure_codes_messages = {
    'PAY_PROCESS_CANCELED': '결제 처리가 취소 되었습니다.',
    'PAY_PROCESS_ABORTED': '결제 처리가 중단 되었습니다.',
    'REJECT_CARD_COMPANY': '카드사에서 결제를 거부했습니다.',
    'NOT_FOUND_PAYMENT_SESSION': '결제 세션을 찾을 수 없습니다.',
    'FORBIDDEN_REQUEST': '이 요청은 금지되었습니다.',
    'UNAUTHORIZED_KEY': '인증되지 않은 키입니다.',
}

# 랜덤한 유니크한 키 생성 함수
def generate_unique_key(min_length=20, max_length=200):
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(characters, k=length))

# 카드 번호 마스킹 처리
def mask_card_number(card_number):
    return card_number[:8] + "****" + card_number[-4:-1] + "*"

# 🟢 더미 데이터 삽입 함수
def insert_fake_data():
    print("🟢 insert_fake_data() 실행됨")  # ✅ 실행 확인

    try:
        # 1. 주문 정보 가져오기
        print("🔎 주문 정보 가져오는 중...")
        cursor.execute("SELECT order_id, online_cart_id FROM online_order ORDER BY RAND() LIMIT 1")
        order_info = cursor.fetchone()
        
        if not order_info:
            print("❌ 주문 정보가 없습니다.")
            return

        order_id, online_cart_id = order_info
        print(f"✅ 주문 ID: {order_id}, 장바구니 ID: {online_cart_id}")  

        # 2. 총 금액 가져오기
        print(f"🔎 총 금액 조회: online_cart_id={online_cart_id}")
        cursor.execute("SELECT total_price FROM Online_Cart WHERE online_cart_id = %s", (online_cart_id,))
        cart_info = cursor.fetchone()
        
        if not cart_info:
            print("❌ 장바구니 정보가 없습니다.")
            return

        total_amount = cart_info[0]
        print(f"✅ 총 금액: {total_amount}원")  

        # 결제 관련 데이터 생성
        mid = 'tosspayments'
        payment_key = generate_unique_key()
        order_name = f"{fake.word()} 외 {random.randint(1, 5)}개"
        method = random.choice(['카드', '간편 결제'])
        requested_at = fake.date_time_this_year()
        approved_at = requested_at + timedelta(minutes=random.randint(1, 60)) if random.random() > 0.5 else None
        balance_amount = total_amount

        card_id = None
        easy_pay_id = None
        cancels_id = None

        # 3. 카드 결제 방식
        if method == '카드':
            print("💳 카드 결제 정보 생성 중...")
            card_number = ''.join(random.choices(string.digits, k=16))
            card_number_masked = mask_card_number(card_number)
            installment_plan_months = random.randint(0, 18)
            approve_no = ''.join(random.choices(string.digits, k=8))

            cursor.execute(""" 
                INSERT INTO `online_card` (
                    `amount`, `issuer_code`, `acquirer_code`, `number`, `installment_plan_months`, 
                    `approve_no`, `use_card_point`, `card_type`, `owner_type`, `acquire_status`, `is_interested_free`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (total_amount, "123", "456", card_number_masked, installment_plan_months, approve_no, 0, '신용카드', '개인', 'COMPLETED', 0))
            cursor.execute("SELECT LAST_INSERT_ID()")
            card_id = cursor.fetchone()[0]
            print(f"✅ 카드 결제 ID: {card_id}")

        # 4. 간편 결제 방식
        if method == '간편 결제':
            print("📱 간편 결제 정보 생성 중...")
            provider = random.choice(payment_providers)
            discount_amount = random.randint(0, total_amount // 2)  
            easy_pay_amount = total_amount - discount_amount

            cursor.execute(""" 
                INSERT INTO `Online_Easy_Pay` (`provider`, `amount`, `discount_amount`)
                VALUES (%s, %s, %s)
            """, (provider, easy_pay_amount, discount_amount))
            cursor.execute("SELECT LAST_INSERT_ID()")
            easy_pay_id = cursor.fetchone()[0]
            print(f"✅ 간편 결제 ID: {easy_pay_id}")

        # 5. 결제 정보 삽입
        print("📝 결제 정보 삽입 중...")
        cursor.execute("""
            INSERT INTO `online_payment` (
                `mid`, `payment_key`, `order_id`, `order_name`, `requested_at`, `approved_at`, 
                `currency`, `total_amount`, `balance_amount`, `method`, `card_id`, `easy_pay_id`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (mid, payment_key, order_id, order_name, requested_at, approved_at, 'KRW', total_amount, balance_amount, method, card_id, easy_pay_id))
        
        conn.commit()
        print("🎉 더미 데이터 삽입 완료!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()

# 🟢 더미 데이터 생성 실행
insert_fake_data()

# 🟢 연결 종료
cursor.close()
conn.close()
