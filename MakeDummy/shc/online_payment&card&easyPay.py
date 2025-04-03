import mysql.connector
import random

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
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

def random_card_num():
    return "".join([str(random.randint(0, 9)) for _ in range(16)])

def execute_payment():
    try:
        cursor.execute("SELECT order_id FROM online_order")
        order_ids = [row[0] for row in cursor.fetchall()]

        print(f"📌 총 {len(order_ids)}개의 주문을 처리합니다.")

        for i, order_id in enumerate(order_ids, start=1):
            use_point = random.randint(0,300)
            if random.random() < 0.7:
                issuer_code, acquirer_code = random.choice(card_companies)[1], random.choice(card_companies)[1]
                card_num = random_card_num()
                installment_plan = random.randint(0, 24)
                query = """
                    CALL online_payment_card(%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (order_id, use_point, issuer_code, acquirer_code, card_num, installment_plan))
                print(f"✅ [{i}/{len(order_ids)}] 카드 결제 완료 (주문 ID: {order_id}, 카드사 코드: {issuer_code}, 매입사 코드: {acquirer_code}, 할부: {installment_plan}개월)")
            else:
                provider = random.choice(payment_providers)
                query = """
                    CALL online_payment_easy_pay(%s, %s, %s)
                """
                cursor.execute(query, (use_point, order_id, provider))
                print(f"✅ [{i}/{len(order_ids)}] 간편 결제 완료 (주문 ID: {order_id}, 제공자: {provider})")

            conn.commit()
        
        print("🎉 모든 주문에 대해 결제 프로시저 실행 완료.")

    except Exception as e:
        conn.rollback()
        print(f"🚨 오류 발생: {e}")
    finally:
        cursor.close()
        conn.close()

execute_payment()