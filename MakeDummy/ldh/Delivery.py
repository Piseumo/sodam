import mysql.connector
import random
from datetime import datetime, timedelta

# 데이터베이스 연결
db = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)

# 커서 생성
cursor = db.cursor()

# delivery_assignment 테이블에서 assignment_id 가져오기
query = "SELECT assignment_id FROM delivery_assignment LIMIT 10;"  # 10개의 데이터를 예시로 가져옴
cursor.execute(query)

# 쿼리 결과 가져오기
assignment_ids = cursor.fetchall()

# 더미 데이터 삽입
for assignment_id_tuple in assignment_ids:
    assignment_id = assignment_id_tuple[0]

    # 상태와 요청 유형 설정
    status_options = ['배송완료', '배송중사고']
    status = random.choice(status_options)  # 배송완료 또는 배송중사고 랜덤 선택
    request_type = '일반배송'  # 모든 값은 '일반배송'으로 고정
    
    # start_date는 오늘로부터 3일 전
    start_date = datetime.now() - timedelta(days=3)
    
    # end_date는 start_date에서 랜덤 시간으로 설정 (시간 단위로 랜덤)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)
    end_date = start_date.replace(hour=random_hour, minute=random_minute, second=random_second)
    
    # delivery 테이블에 데이터 삽입
    insert_query = """
        INSERT INTO delivery (status, start_date, end_date, request_type, assignment_id)
        VALUES (%s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (status, start_date, end_date, request_type, assignment_id))
    
    # 삽입된 ID 확인
    delivery_id = cursor.lastrowid
    print(f"Inserted: delivery_id={delivery_id}, assignment_id={assignment_id}, status={status}, request_type={request_type}, start_date={start_date}, end_date={end_date}")

# 커밋하여 데이터 반영
db.commit()

# 연결 종료
cursor.close()
db.close()
