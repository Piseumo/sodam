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
query = "SELECT assignment_id FROM delivery_assignment;"
cursor.execute(query)

# 쿼리 결과 가져오기
assignment_ids = cursor.fetchall()

# 만약 가져온 assignment_id가 없다면 종료
if not assignment_ids:
    print("No data available for assignment_id.")
    db.close()
    exit()

# 더미 데이터 삽입
for assignment_id_tuple in assignment_ids:
    assignment_id = assignment_id_tuple[0]

    # 이미 delivery 테이블에 해당 assignment_id가 존재하는지 확인
    check_query = "SELECT COUNT(*) FROM delivery WHERE assignment_id = %s"
    cursor.execute(check_query, (assignment_id,))
    result = cursor.fetchone()

    # 이미 존재하는 assignment_id라면 스킵
    if result[0] > 0:
        print(f"Skipping assignment_id={assignment_id} as it already exists in delivery table.")
        continue

    # 상태 설정
    status = '배송완료'  # 기본적으로 배송완료로 설정
    if random.random() <= 0.05:  # 10% 확률로 배송중사고
        status = '배송중사고'
    
    request_type = '일반배송'  # request_type은 항상 '일반배송'으로 설정
    
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
