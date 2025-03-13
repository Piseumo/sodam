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

# 카드사 데이터 (issuer_code, acquirer_code로 사용할 값)
card_companies = [
    ("기업 BC", "3K"), ("광주은행", "46"), ("롯데카드", "71"), ("한국산업은행", "30"),
    ("BC카드", "31"), ("삼성카드", "51"), ("새마을금고", "38"), ("신한카드", "41"),
    ("신협", "62"), ("씨티카드", "36"), ("우리BC카드(BC 매입)", "33"), ("우리카드(우리 매입)", "W1"),
    ("우체국예금보험", "37"), ("저축은행중앙회", "39"), ("전북은행", "35"), ("제주은행", "42"),
    ("카카오뱅크", "15"), ("케이뱅크", "3A"), ("토스뱅크", "24"), ("하나카드", "21"),
    ("현대카드", "61"), ("KB국민카드", "11"), ("NH농협카드", "91"), ("Sh수협은행", "34"),
]

# 간편결제 제공사 목록
payment_providers = [
    "TOSSPAY", "NAVERPAY", "SAMSUNGPAY", "APPLEPAY", "LPAY",
    "KAKAOPAY", "PINPAY", "PAYCO", "SSG"
]

# failure_code 목록
failure_codes_messages = {
    'PAY_PROCESS_CANCELED': '결제 처리가 취소 되었습니다.',
    'PAY_PROCESS_ABORTED': '결제 처리가 중단 되었습니다.',
    'REJECT_CARD_COMPANY': '카드사에서 결제를 거부했습니다.',
    'NOT_FOUND_PAYMENT_SESSION': '결제 세션을 찾을 수 없습니다.',
    'FORBIDDEN_REQUEST': '이 요청은 금지되었습니다.',
    'UNAUTHORIZED_KEY': '인증되지 않은 키입니다.',
}

# 랜덤한 유니크한 payment_key 생성
def generate_unique_payment_key(min_length=20, max_length=200):
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(characters, k=length))

# 고유한 last_transaction_key 생성 함수 (32 ~ 64자, 대소문자 + 숫자)
def generate_unique_transaction_key(min_length=32, max_length=64):
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(characters, k=length))

# 랜덤한 유니크한 secret 생성
def generate_unique_secret(min_length=20, max_length=50):
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    return ''.join(random.choices(characters, k=length))

# 카드 번호 마스킹 처리
def mask_card_number(card_number):
    card_number = card_number[:8] + "****" + card_number[-4:-1] + "*"
    return card_number

# 더미 데이터 삽입 함수
def insert_fake_data():
    try:
        # 1. 모든 주문의 order_id 조회
        cursor.execute("SELECT order_id, online_cart_id FROM online_order")
        orders = cursor.fetchall()
        
        # 주문이 없으면 종료
        if not orders:
            print("주문 정보가 없습니다.")
            return

        for order_id, online_cart_id in orders:
            print(f"Order ID: {order_id}, Online Cart ID: {online_cart_id}")

            # 2. 주문에 결제가 이미 존재하는지 확인
            cursor.execute("SELECT COUNT(*) FROM online_payment WHERE order_id = %s", (order_id,))
            payment_exists = cursor.fetchone()[0]
            if payment_exists > 0:
                print("이미 결제가 존재하는 주문입니다.")
                return  # 결제 정보를 다시 추가하지 않음

            # 2. 총 금액 (total_amount) 가져오기
            cursor.execute("SELECT total_price FROM Online_Cart WHERE online_cart_id = %s", (online_cart_id,))
            cart_info = cursor.fetchone()
            if not cart_info:
                print("장바구니 정보가 없습니다.")
                return

            total_amount = cart_info[0]
            print(f"Total Amount: {total_amount}")

            # 나머지 데이터 삽입 처리
            mid = 'tosspayments'
            last_transaction_key = generate_unique_transaction_key()  # UUID로 고유값 생성
            payment_key = generate_unique_payment_key()
            order_name = f"{fake.word()} 외 {random.randint(1, 5)}개"
            tax_exemption_amount = 0
            use_escrow = 0
            culture_expense = 0
            secret = generate_unique_secret()
            payment_type = 'NORMAL'
            country = 'KR'
            failure_code = None
            failure_message = None
            is_partial_cancelable = random.choice([0, 1])
            reciept_url = fake.url()
            check_out_url = fake.url()
            currency = 'KRW'
            supplied_amount = 0
            tax_free_amount = 0
            method = random.choice(['카드', '간편 결제'])
            version = '2022-11-16'
            card_id = None
            easy_pay_id = None
            cancels_id = None
            balance_amount = total_amount  # 기본적으로 total_amount로 설정

            # 상태 값 설정 추가
            status = random.choice(['COMPLETED', 'CANCELED', 'PARTIAL_CANCELED', 'PROCESSING'])  # 결제 상태 중 하나를 선택

            requested_at = fake.date_time_this_year()
            approved_at = requested_at + timedelta(minutes=random.randint(1, 60)) if random.random() > 0.5 else None

            print(f"Payment Method: {method}")
            print(f"Status: {status}")
            print(f"Payment Key: {payment_key}")
            print(f"Order Name: {order_name}")
            print(f"Total Amount: {total_amount}")
            print(f"Requested At: {requested_at}")
            print(f"Approved At: {approved_at}")
            print(f"Tax Exemption Amount: {tax_exemption_amount}")
            print(f"Use Escrow: {use_escrow}")
            print(f"Culture Expense: {culture_expense}")
            print(f"Secret: {secret}")
            print(f"Payment Type: {payment_type}")
            print(f"Country: {country}")
            print(f"Failure Code: {failure_code}")
            print(f"Failure Message: {failure_message}")
            print(f"Is Partial Cancelable: {is_partial_cancelable}")
            print(f"Receipt URL: {reciept_url}")
            print(f"Check Out URL: {check_out_url}")
            print(f"Currency: {currency}")
            print(f"Balance Amount: {balance_amount}")

            # 카드 테이블에 더미 데이터 삽입
            if method == '카드':
                amount = total_amount
                issuer_code, acquirer_code = random.choice(card_companies)[1], random.choice(card_companies)[1]
                card_number = ''.join(random.choices(string.digits, k=16))
                card_number_masked = mask_card_number(card_number)
                installment_plan_months = random.randint(0, 18)
                approve_no = ''.join(random.choices(string.digits, k=8))  # 8자리 숫자 승인 번호
                card_type = random.choice(['신용카드', '체크카드', '기프트카드'])  # 카드 종류 랜덤
                owner_type = random.choice(['개인', '법인'])  # 카드 소유자 종류 랜덤
                acquire_status = 'COMPLETED'  # 고정값
                is_interested_free = 0  # 고정값
                print(f"Card ID will be generated. Issuer Code: {issuer_code}, Acquirer Code: {acquirer_code}, Card Number: {card_number_masked}")
                cursor.execute(""" 
                    INSERT INTO `online_card` (
                        `amount`, `issuer_code`, `acquirer_code`, `number`, `installment_plan_months`, 
                        `approve_no`, `use_card_point`, `card_type`, `owner_type`, `acquire_status`, `is_interested_free`
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (amount, issuer_code, acquirer_code, card_number_masked, installment_plan_months, approve_no, 0, card_type, owner_type, acquire_status, is_interested_free))
                cursor.execute("SELECT LAST_INSERT_ID()")
                card_id = cursor.fetchone()[0]
                print(f"Card ID: {card_id}")

            # 간편 결제에 관련된 더미 데이터 삽입
            if method == '간편 결제':
                # 간편결제 금액 계산
                discount_amount = random.randint(0, total_amount // 2)  # 최대 할인 금액은 total_amount의 절반
                easy_pay_amount = total_amount - discount_amount
                provider = random.choice(payment_providers)
                print(f"Easy Pay provider: {provider}, Easy Pay Amount: {easy_pay_amount}, Discount Amount: {discount_amount}")
                cursor.execute(""" 
                    INSERT INTO `Online_Easy_Pay` (
                        `provider`, `amount`, `discount_amount`
                    ) VALUES (%s, %s, %s)
                """, (provider, easy_pay_amount, discount_amount))
                cursor.execute("SELECT LAST_INSERT_ID()")
                easy_pay_id = cursor.fetchone()[0]
                print(f"Easy Pay ID: {easy_pay_id}")

            # `online_payment`에 데이터 삽입
            query = """
            INSERT INTO `online_payment` (
                `mid`, `last_transaction_key`, `payment_key`, `order_id`, `order_name`, `tax_exemption_amount`, `status`, 
                `requested_at`, `approved_at`, `use_escrow`, `culture_expense`, `secret`, `type`, `country`, `failure_code`, 
                `failure_message`, `is_partial_cancelable`, `reciept_url`, `check_out_url`, `currency`, `total_amount`, 
                `balance_amount`, `supplied_amount`, `vat`, `tax_free_amount`, `method`, `version`, `card_id`, `easy_pay_id`, `cancels_id`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # vat 계산 (부가세 공식 적용)
            vat = round((total_amount - tax_free_amount) / 11)

            values = (
                mid, last_transaction_key, payment_key, order_id, order_name, tax_exemption_amount, status, requested_at,
                approved_at, use_escrow, culture_expense, secret, payment_type, country, failure_code,
                failure_message, is_partial_cancelable, reciept_url, check_out_url, currency, total_amount, balance_amount,
                supplied_amount, vat, tax_free_amount, method, version, card_id, easy_pay_id, cancels_id
            )

            print(f"Executing query: {query}")
            print(f"With values: {values}")
            cursor.execute(query, values)

            # 결제 취소가 발생했을 경우, 취소 데이터를 'online_cancels' 테이블에 삽입
            if status in ['CANCELED', 'PARTIAL_CANCELED']:
                cancel_reason = random.choice(["고객 요청으로 취소", "상품 품절", "기타"])
                cancel_status = "DONE"  # 취소 완료 상태
                transaction_key = generate_unique_transaction_key()  # 트랜잭션 키 생성
                # cancel_amount = random.randint(1, total_amount - 1)  # 환불 금액
                # refundable_amount = total_amount - cancel_amount  # 환불 후 환불 가능 금액
                canceled_at = fake.date_time_this_year()  # 취소 시간

                if total_amount > 0:
                    cancel_amount = random.randint(1, total_amount - 1)  # 환불 금액
                    refundable_amount = total_amount - cancel_amount  # 환불 후 환불 가능 금액
                else:
                    cancel_amount = 0
                    refundable_amount = 0

                print(f"Cancel Reason: {cancel_reason}, Transaction Key: {transaction_key}, Canceled Amount: {refundable_amount}")
                cursor.execute(""" 
                    INSERT INTO `online_cancels` (
                        `transaction_key`, `cancel_reason`, `tax_exemption_amount`, `canceled_at`,
                        `transfer_discount_amount`, `easyPay_discount_amount`, `cancel_amount`, 
                        `tax_free_amount`, `refundable_amount`, `cancel_status`, `cancel_request_id`
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (transaction_key, cancel_reason, 0, canceled_at, 0, 0, cancel_amount, 0, refundable_amount, cancel_status, None))

                # 삽입된 'online_cancels' 테이블에서 'cancels_id' 가져오기
                cancels_id = cursor.lastrowid

                # `online_payment` 테이블에서 해당 취소 ID를 업데이트합니다
                cursor.execute(""" 
                    UPDATE `online_payment`
                    SET `cancels_id` = %s
                    WHERE `order_id` = %s
                """, (cancels_id, order_id))

                # 'online_payment' 테이블에서 last_transaction_key를 취소된 transaction_key로 업데이트
                cursor.execute(""" 
                    UPDATE `online_payment`
                    SET `last_transaction_key` = %s
                """, (transaction_key,))  # 튜플로 감싸서 전달

        conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# 데이터 삽입 함수 호출
insert_fake_data()

# 연결 종료
cursor.close()
conn.close()
