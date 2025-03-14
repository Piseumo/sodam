import mysql.connector

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
     host="192.168.0.104",  
    user="my_user",   
    password="1234", 
    database="sodam"
)

cursor = db.cursor()

# 삭제할 배치 크기 설정 (예: 한 번에 1000개씩 삭제)
batch_size = 1000

# 데이터 삭제 루프
while True:
    # 데이터 삭제 쿼리 (배치 크기 만큼, ID 순으로 정렬하여 삭제)
    query = f"DELETE FROM delivery ORDER BY delivery_id LIMIT {batch_size}"
    
    cursor.execute(query)
    
    # 변경된 행 수 확인
    rows_affected = cursor.rowcount
    print(f"삭제된 데이터 수: {rows_affected}")
    
    # 만약 삭제된 데이터가 배치 크기보다 적으면 종료 (마지막 배치)
    if rows_affected < batch_size:
        print("모든 데이터를 삭제했습니다.")
        break

    # 커밋
    db.commit()

# 연결 종료
cursor.close()
db.close()
