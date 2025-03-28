import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = conn.cursor()

# 삭제할 배치 크기 설정 (예: 한 번에 1000개씩 삭제)
batch_size = 10000

# 데이터 삭제 루프
while True:
    # 데이터 삭제 쿼리 (배치 크기 만큼, ID 순으로 정렬하여 삭제)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    query1 = f"DELETE FROM Store_Inventory ORDER BY inventory_id LIMIT {batch_size}"
    query2 = f"DELETE FROM Warehouse_Inventory ORDER BY inventory_id LIMIT {batch_size}"
    
    
    cursor.execute(query1)
    cursor.execute(query2)
    
    # 변경된 행 수 확인
    rows_affected = cursor.rowcount
    print(" {rows_affected} 개의 행이 삭제되었습니다.")
    # 만약 삭제된 데이터가 배치 크기보다 적으면 종료 (마지막 배치)
    if rows_affected < batch_size:
        print("모든 데이터를 삭제했습니다.")
        break

    # 커밋
    conn.commit()

# 연결 종료
cursor.close()
conn.close()
