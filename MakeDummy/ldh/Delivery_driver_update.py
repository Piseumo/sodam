import mysql.connector

# MySQL 연결
db = mysql.connector.connect(
      host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# 1. `Delivery_Driver` 테이블에서 모든 `driver_id`를 조회
cursor.execute("SELECT driver_id FROM Delivery_Driver")

# 2. 모든 `driver_id` 목록을 가져옴
drivers = cursor.fetchall()

# 3. 업데이트된 더미 데이터 갯수 추적
updated_count = 0

# 4. 각 `driver_id`에 대해 `car_id`를 확인하고 업데이트
for driver in drivers:
    driver_id = driver[0]  # driver_id 값

    # 5. `Delivery_Car` 테이블에서 해당 `car_id`가 존재하는지 확인
    cursor.execute("SELECT car_id FROM Delivery_Car WHERE car_id = %s", (driver_id,))
    car = cursor.fetchone()

    if car:
        # car_id가 존재하면 `car_id`와 동일하게 업데이트
        car_id = car[0]
    else:
        # car_id가 없으면 NULL로 설정
        car_id = None

    # 6. `Delivery_Driver` 테이블에서 `car_id` 업데이트
    update_query = """
        UPDATE Delivery_Driver
        SET car_id = %s
        WHERE driver_id = %s;
    """
    cursor.execute(update_query, (car_id, driver_id))

    # 7. 업데이트가 성공적으로 실행되면 카운트 증가
    if cursor.rowcount > 0:  # 업데이트된 행이 있을 경우
        updated_count += 1

# 8. 변경 사항 커밋
db.commit()

# 9. 업데이트된 갯수 출력
print(f"업데이트된 더미 데이터의 갯수: {updated_count}")

# 10. 연결 종료
cursor.close()
db.close()
