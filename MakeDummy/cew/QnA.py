import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE QnA;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("기존 데이터 삭제 완료!")

cursor.execute("SELECT customer_id FROM Customer;")
customer_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT employee_id FROM Employees;")
employee_ids = [row[0] for row in cursor.fetchall()]

# 문의 및 답변 유형별 매핑
type_contents = {
    '회원': (
        ["회원 탈퇴는 어떻게 하나요?", "로그인이 되지 않습니다.", "이메일 인증이 안됩니다."],
        ["회원 탈퇴는 마이페이지에서 가능합니다.", "로그인 문제는 브라우저 캐시 삭제를 권장합니다.", "스팸 메일함을 확인해주세요."]
    ),
    '주문/결제/배송': (
        ["배송이 늦습니다.", "결제 오류가 발생했습니다.", "배송지를 잘못 입력했어요."],
        ["배송 지연 죄송합니다.", "결제 오류 확인 중입니다.", "배송지를 변경해드리겠습니다."]
    ),
    '취소/교환/반품': (
        ["교환하고 싶습니다.", "반품 절차가 궁금합니다.", "환불 요청드립니다."],
        ["교환 신청 안내드립니다.", "반품 신청은 고객센터로 연락주세요.", "환불은 3~5일 내 처리됩니다."]
    ),
    '상품': (
        ["상품 품질이 안 좋습니다.", "재고가 있나요?", "제품 상세 정보가 부족해요."],
        ["상품 불량 죄송합니다.", "재고 확인 후 안내드리겠습니다.", "추가 정보를 곧 업데이트하겠습니다."]
    ),
    '포인트/할인': (
        ["포인트가 적립되지 않았어요.", "할인이 적용되지 않았습니다.", "쿠폰 사용 방법을 알려주세요."],
        ["포인트 확인 후 조치하겠습니다.", "할인 적용 문제를 처리 중입니다.", "쿠폰 사용법 안내드립니다."]
    ),
    '기타': (
        ["기타 문의 사항이 있습니다.", "이벤트 일정이 궁금해요."],
        ["추가 문의 사항을 접수했습니다.", "이벤트 일정은 홈페이지 공지를 참고하세요."]
    )
}

statuses = ['Pending', 'Completed']
types_list = list(type_contents.keys())

num_records = 1000000
batch_size = 10000
qna_to_insert = []

for _ in range(num_records):
    qna_type = random.choice(types_list)
    inquiry_content = random.choice(type_contents[qna_type][0])
    inquiry_time = fake.date_time_between(start_date="-1y", end_date="now")
    image = fake.image_url() if random.random() < 0.3 else None
    status = random.choice(statuses)

    customer_id = random.choice(customer_ids)
    
    if status == "Completed" and employee_ids:
        employee_id = random.choice(employee_ids)
        answer_time = fake.date_time_between(start_date=inquiry_time, end_date="now")
        answer_content = random.choice(type_contents[qna_type][1])
    else:
        employee_id = None
        answer_time = None
        answer_content = None

    qna_to_insert.append((customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content, qna_type))

    if len(qna_to_insert) >= batch_size:
        sql_qna = """
        INSERT INTO QnA (customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(sql_qna, qna_to_insert)
        conn.commit()
        qna_to_insert = []

if qna_to_insert:
    sql_qna = """
    INSERT INTO QnA (customer_id, inquiry_content, image, inquiry_time, status, employee_id, answer_time, answer_content, type)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(sql_qna, qna_to_insert)
    conn.commit()

print("QnA 데이터 삽입 완료!")

cursor.close()
conn.close()

print("문의(QnA) 데이터가 성공적으로 삽입되었습니다! 🚀")
