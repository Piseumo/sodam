import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Faker 객체 생성
fake = Faker('ko_KR')

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

# 커서 생성
cursor = db.cursor()

# 데이터 삽입 쿼리 (Delivery_Accident_Log 테이블)
insert_query = """
    INSERT INTO Delivery_Accident_Log (employee_id, delivery_id, log_types, text, status, accident_date, report_date, complete_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# 사고 유형 리스트
log_types = ['차량사고', '배송품파손', '운전기사이상', '기상이변', '도로정체']

# 사고 내용 생성 함수 (정해진 텍스트)
def generate_accident_text(log_type):
    if log_type == '차량사고':
        return "배송중 충돌사고로 차량이 고장났습니다."
    elif log_type == '배송품파손':
        return "배송품이 운송중 파손되었습니다."
    elif log_type == '운전기사이상':
        return "몸이 갑자기 좋지 않아 배송을 중단해야 할 것 같습니다."
    elif log_type == '기상이변':
        return "날씨가 흐려서 도로가 복잡해 배송시간이 정체되었습니다."
    elif log_type == '도로정체':
        return "길이 막혀 예상 배송시간 보다 늦어질 예정입니다."
    return "사고 발생에 대한 자세한 정보가 없습니다."

# 사고 로그 생성 함수
def generate_accident_log(delivery_id):
    # Delivery 테이블에서 배송중사고인 데이터만 가져오기
    cursor.execute("""
        SELECT delivery_id, start_date 
        FROM Delivery 
        WHERE delivery_id = %s AND status = '배송중사고'
    """, (delivery_id,))
    result = cursor.fetchone()
    
    if not result:
        return  # 배송중사고 상태가 아니면 종료

    # 배송 정보 가져오기
    delivery_id = result[0]
    start_date = result[1]

    # 직원 정보 가져오기 (role이 '고객지원'인 직원)
    cursor.execute("""
        SELECT employee_id 
        FROM Employees 
        WHERE role = '고객지원'
    """)
    employees = cursor.fetchall()
    
    if not employees:
        return  # 고객지원 직원이 없으면 종료
    
    # 직원 ID 랜덤으로 선택
    employee_id = random.choice(employees)[0]

    # 사고 유형 랜덤 선택 (20%씩 분배)
    log_type = random.choices(log_types, k=1)[0]

    # 사고 설명 생성
    text = generate_accident_text(log_type)

    # 사고 발생일 및 처리 완료일
    accident_date = start_date + timedelta(days=random.randint(1, 7))  # 사고 발생일은 start_date와 1~7일 사이로 설정
    complete_date = accident_date + timedelta(days=random.randint(7, 14))  # 사고 발생 후 7~14일 뒤에 처리 완료일 설정

    # 사고 등록일 (report_date) - start_date와 그 다음날 사이
    report_date = start_date + timedelta(days=random.randint(1, 2))  # start_date와 그 다음날 사이로 설정

    # 상태는 '처리완료'로 설정
    status = '처리완료'

    # 데이터 삽입
    cursor.execute(insert_query, (employee_id, delivery_id, log_type, text, status, accident_date, report_date, complete_date))
    db.commit()

    print(f"Accident log for delivery_id {delivery_id} added. Status: {status}, Accident Date: {accident_date}, Report Date: {report_date}")

# Delivery 테이블에서 '배송중사고'인 항목에 대해 사고 로그 생성
cursor.execute("""
    SELECT delivery_id 
    FROM Delivery 
    WHERE status = '배송중사고'
""")  # '배송중사고' 상태인 delivery_id만 가져오기
delivery_records = cursor.fetchall()

for delivery_id, in delivery_records:
    # 사고 로그 생성
    generate_accident_log(delivery_id)

# 커서와 데이터베이스 연결 종료
cursor.close()
db.close()

print("✅ 사고 로그 데이터 삽입 완료!")
