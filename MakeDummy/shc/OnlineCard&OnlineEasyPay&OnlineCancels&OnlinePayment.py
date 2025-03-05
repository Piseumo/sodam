import mysql.connector
from faker import Faker
import random

# Faker 한글 로케일 적용
fake = Faker("ko_KR")  

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

# ENUM 타입 매입 상태 값
acquire_status_options = ["READY", "REQUESTED", "COMPLETED", "CANCEL_REQUEST", "CANCELED"]
card_types = ["신용", "체크", "기프트", "미확인"]  # 카드 타입 한글
owner_types = ["개인", "기업", "미확인"]  # 카드 소유자 종류 (한글)

# 카드 번호 마스킹 함수
def mask_card_number(card_number):
    # 앞 8자리, 중간 4자리 *, 뒤 3자리, 마지막 1자리 *
    masked = card_number[:8] + "****" + card_number[-4:-1] + "*"
    return masked

# 더미 데이터 삽입
for _ in range(1000):  # 원하는 개수로 변경 가능
    issuer = random.choice(card_companies)  # 발급사 랜덤 선택
    acquirer = random.choice(card_companies)  # 매입사 랜덤 선택
    
    amount = random.randint(1000, 500000)  # 결제 요청 금액 (1,000 ~ 500,000)
    raw_card_number = fake.credit_card_number()  # 원본 카드 번호
    card_number = mask_card_number(raw_card_number)  # 마스킹된 카드 번호
    installment_plan_months = random.randint(0, 18)  # 할부 개월 수 (0 ~ 18)
    approve_no = fake.random_number(digits=8, fix_len=True)  # 승인 번호 (8자리 랜덤 숫자)
    use_card_point = random.choice([0, 1])  # 카드 포인트 사용 여부
    card_type = random.choice(card_types)  # 카드 종류 (한글)
    owner_type = random.choice(owner_types)  # 카드 소유자 종류 (한글)
    acquire_status = random.choice(acquire_status_options)  # 매입 상태 (ENUM 값)
    is_interested_free = random.choice([0, 1])  # 무이자 할부 적용 여부

    # SQL 쿼리 작성
    sql = """
    INSERT INTO online_card (
        amount, issuer_code, acquirer_code, number, installment_plan_months, 
        approve_no, use_card_point, card_type, owner_type, acquire_status, is_interested_free
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        amount, 
        issuer[1],  # issuer_code (두 번째 값)
        acquirer[1],  # acquirer_code (두 번째 값)
        card_number, 
        installment_plan_months, 
        approve_no, 
        use_card_point, 
        card_type, 
        owner_type, 
        acquire_status, 
        is_interested_free
    )

    cursor.execute(sql, values)

# 변경 사항 커밋
conn.commit()

# 간편결제사 데이터 (이름, 코드)
payment_providers = [
    ("TOSSPAY"),
    ("NAVERPAY"),
    ("SAMSUNGPAY"),
    ("APPLEPAY"),
    ("LPAY"),
    ("KAKAOPAY"),
    ("PINPAY"),
    ("PAYCO"),
    ("SSG")
]

# 더미 데이터 삽입
for _ in range(1000):  # 원하는 개수로 변경 가능
    provider_code = random.choice(payment_providers)  # 간편결제사 코드 랜덤 선택
    amount = random.randint(1000, 500000)  # 결제 금액 (1,000 ~ 500,000)
    discount_amount = random.randint(0, amount // 2)  # 최대 할인 금액은 결제 금액의 절반 이내로 설정

    # SQL 쿼리 작성
    sql = """
    INSERT INTO Online_Easy_Pay (provider, amount, discount_amount) 
    VALUES (%s, %s, %s)
    """
    
    values = (provider_code, amount, discount_amount)

    cursor.execute(sql, values)

# 변경 사항 커밋
conn.commit()

# 64자 랜덤 고유 문자열 생성 함수
def generate_unique_key(length=64):
    characters = string.ascii_letters + string.digits  # 대소문자 및 숫자
    return ''.join(random.choice(characters) for _ in range(length))

# 구매자가 제시할 수 있는 취소 이유 리스트
cancel_reasons = [
    "상품이 마음에 들지 않아서",
    "배송이 늦어서",
    "가격이 비싸서",
    "구매 후 가격이 더 낮아져서",
    "상품 설명과 달라서",
    "배송 상태가 불만족스러워서",
    "교환이 필요해서",
    "기타 개인적인 사유"
]

# 취소 상태 리스트
cancel_statuses = ["DONE", "IN_PROGRESS", "ABORTED"]

# 더미 데이터 삽입
for _ in range(1000):  # 원하는 개수로 변경 가능
    transaction_key = generate_unique_key()  # 64자리 고유 문자열 생성
    cancel_reason = random.choice(cancel_reasons)  # 취소 이유 랜덤 선택
    tax_exemption_amount = random.randint(0, 100000)  # 과세 제외 금액 (0 ~ 100,000)
    canceled_at = fake.date_time_this_year()  # 올해의 랜덤한 날짜 및 시간
    transfer_discount_amount = random.randint(0, 10000)  # 퀵계좌이체 서비스의 즉시할인에서 취소된 금액
    easyPay_discount_amount = random.randint(0, 10000)  # 간편결제 서비스의 적립식 결제수단에서 취소된 금액
    cancel_amount = random.randint(1000, 500000)  # 취소 금액 (1,000 ~ 500,000)
    tax_free_amount = random.randint(0, 100000)  # 면세 금액 (0 ~ 100,000)
    refundable_amount = cancel_amount - (tax_exemption_amount + transfer_discount_amount + easyPay_discount_amount + tax_free_amount)
    cancel_status = random.choice(cancel_statuses)  # 취소 상태 랜덤 선택
    cancel_request_id = fake.uuid4()  # 취소 요청 ID (UUID 생성)

    # SQL 쿼리 작성
    sql = """
    INSERT INTO online_cancels (
        transaction_key, cancel_reason, tax_exemption_amount, canceled_at, 
        transfer_discount_amount, easyPay_discount_amount, cancel_amount, 
        tax_free_amount, refundable_amount, cancel_status, cancel_request_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        transaction_key, cancel_reason, tax_exemption_amount, canceled_at, 
        transfer_discount_amount, easyPay_discount_amount, cancel_amount, 
        tax_free_amount, refundable_amount, cancel_status, cancel_request_id
    )

    cursor.execute(sql, values)

# 변경 사항 커밋
conn.commit()

# 연결 종료
cursor.close()
conn.close()

print("1000개의 더미 데이터 삽입 완료")

