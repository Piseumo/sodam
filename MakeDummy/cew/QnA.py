import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# ✅ 한글 문의 & 답변 템플릿 (확장)
inquiry_samples = [
    "배송이 너무 늦어요. 언제 도착하나요?",
    "상품이 불량이어서 교환 요청합니다.",
    "결제 오류가 발생했습니다. 확인 부탁드려요.",
    "회원 탈퇴는 어떻게 하나요?",
    "재고가 언제 다시 들어오나요?",
    "쿠폰을 사용했는데 할인 적용이 안 되었어요.",
    "반품 요청하려면 어떻게 해야 하나요?",
    "제품 상세 정보에 없는 추가 정보가 궁금합니다.",
    "포인트 적립이 안 되었어요. 확인해주세요.",
    "사이트에서 로그인 오류가 납니다.",
    "배송이 엉뚱한 주소로 갔어요. 다시 배송받을 수 있을까요?",
    "회원가입 시 이메일 인증이 안 돼요.",
    "주문을 취소하고 싶은데 환불은 어떻게 되나요?",
    "상품 설명과 실제 제품이 달라요. 반품 가능한가요?",
    "비밀번호를 변경하려면 어떻게 해야 하나요?",
    "카카오페이로 결제했는데 결제 내역이 안 보여요.",
    "할인 이벤트는 언제까지 진행되나요?",
    "선물용으로 포장 가능한가요?",
    "리뷰를 작성하면 포인트 적립이 되나요?",
    "적립된 포인트를 어떻게 사용할 수 있나요?"
]

answer_samples = [
    "고객님, 배송이 지연되어 죄송합니다. 빠른 시일 내 도착할 수 있도록 하겠습니다.",
    "교환 절차는 마이페이지에서 신청 가능합니다. 자세한 사항은 고객센터로 문의해주세요.",
    "결제 오류는 카드사 문제일 수 있습니다. 다시 한 번 시도해보시고, 지속되면 연락주세요.",
    "회원 탈퇴는 설정 페이지에서 가능합니다. 계정 삭제 후 복구가 불가능하니 유의해주세요.",
    "현재 재고 확보 중이며, 다음 주 중에 입고될 예정입니다.",
    "쿠폰 사용 오류를 확인하고 있습니다. 담당 부서에서 처리 후 연락드리겠습니다.",
    "반품 신청은 고객센터를 통해 가능합니다. 반품 접수 후 3일 내 회수 진행됩니다.",
    "추가 정보는 상품 상세 페이지 업데이트 예정입니다. 추가로 궁금한 점은 문의 주세요.",
    "포인트 적립 오류를 확인했습니다. 조속히 조치하겠습니다.",
    "로그인 문제는 브라우저 캐시를 삭제 후 다시 시도해보시길 바랍니다.",
    "배송 문제로 불편을 끼쳐드려 죄송합니다. 재배송 가능하도록 조치하겠습니다.",
    "이메일 인증 메일이 스팸함으로 이동했는지 확인해 주세요. 그래도 안 되면 고객센터로 문의 바랍니다.",
    "주문 취소 후 환불은 영업일 기준 3~5일 내 처리됩니다.",
    "상품 반품이 가능하며, 반품 절차에 대해 자세히 안내해 드리겠습니다.",
    "비밀번호 변경은 마이페이지 > 계정 설정에서 가능합니다.",
    "결제 내역이 확인되지 않는 경우, 카드사 또는 간편결제사에 문의 부탁드립니다.",
    "할인 이벤트는 이번 달 말까지 진행됩니다. 기회를 놓치지 마세요!",
    "선물 포장 옵션은 결제 페이지에서 선택하실 수 있습니다.",
    "리뷰 작성 시 포인트가 적립됩니다. 이벤트 페이지에서 적립 기준을 확인하세요.",
    "적립된 포인트는 결제 시 사용 가능합니다. 사용 가능 포인트는 마이페이지에서 확인하세요."
]

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

# ✅ (1) 기존 데이터 삭제 (TRUNCATE TABLE → AUTO_INCREMENT 초기화)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE QnA;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("기존 데이터 삭제 완료!")

# ✅ (2) `customer_id` 목록 가져오기 (QnA 작성자)
cursor.execute("SELECT customer_id FROM Customer;")
customer_ids = [row[0] for row in cursor.fetchall()]  # ✅ 고객 ID 리스트

# ✅ (3) `employee_id` 목록 가져오기 (QnA 답변자 - 직원)
cursor.execute("SELECT employee_id FROM Employees;")
employee_ids = [row[0] for row in cursor.fetchall()]  # ✅ 직원 ID 리스트

# ✅ (4) 상태 ENUM 값 정의
statuses = ['Pending', 'Completed']

# ✅ (5) QnA 데이터 생성 및 삽입
if customer_ids:
    num_records = 1000000  # ✅ 생성할 데이터 개수
    batch_size = 10000  # ✅ 대량 삽입을 위한 배치 크기
    qna_to_insert = []

    for _ in range(num_records):
        customer_id = random.choice(customer_ids)  # ✅ 고객 ID 선택
        inquiry_content = random.choice(inquiry_samples)  # ✅ 한글 문의 내용 선택
        inquiry_time = fake.date_time_between(start_date="-1y", end_date="now")  # ✅ 최근 1년 내 문의 시간
        image = fake.image_url() if random.random() < 0.3 else None  # ✅ 30% 확률로 이미지 포함
        status = random.choice(statuses)  # ✅ 상태 값 랜덤 선택

        if status == "Completed" and employee_ids:  # ✅ 답변 완료된 경우
            employee_id = random.choice(employee_ids)  # ✅ 랜덤 직원 배정
            answer_time = fake.date_time_between(start_date=inquiry_time, end_date="now")  # ✅ 문의 이후 랜덤 답변 시간
            answer_content = random.choice(answer_samples)  # ✅ 한글 답변 내용 선택
        else:
            employee_id = None
            answer_time = None
            answer_content = None

        qna_to_insert.append((customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content))

        # ✅ 일정 개수마다 DB에 삽입 (배치 처리)
        if len(qna_to_insert) >= batch_size:
            sql_qna = """
            INSERT INTO QnA (customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.executemany(sql_qna, qna_to_insert)
            conn.commit()
            qna_to_insert = []

    # ✅ 마지막 남은 데이터 삽입
    if qna_to_insert:
        sql_qna = """
        INSERT INTO QnA (customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(sql_qna, qna_to_insert)
        conn.commit()

    print("QnA 데이터 삽입 완료!")

# ✅ (6) 커서 및 연결 종료
cursor.close()
conn.close()

print("문의(QnA) 데이터가 성공적으로 삽입되었습니다! 🚀")
