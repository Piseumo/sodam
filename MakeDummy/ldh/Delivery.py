import mysql.connector
import random
import datetime

# MySQL 연결 설정
db = mysql.connector.connect(
    host="192.168.0.104",  
    user="my_user",   
    password="1234", 
    database="sodam"
)

# 커서 생성
cursor = db.cursor()

def insert_delivery():
    # 상태 설정: 배송완료 99%, 배송중사고 1%
    statuses = ['배송완료', '배송중사고']
    status_weights = [0.99, 0.01]  # 배송완료 99%, 배송중사고 1%

    # 요청 유형을 고객 100%로 설정
    request_types = ['고객']
    request_weights = [1.0]  # 100% 고객

    # 온라인 결제 상태가 'COMPLETED'인 online_payment_id 가져오기
    cursor.execute("SELECT online_payment_id FROM online_payment WHERE status = 'COMPLETED'")
    online_payment_ids = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(online_payment_ids)} online_payment_ids")  # 디버깅

    # Delivery_Driver 테이블에서 근무가능, training_check 1, insurance 1인 driver_id 가져오기
    cursor.execute("SELECT driver_id FROM Delivery_Driver WHERE status = '근무가능' AND training_check = 1 AND insurance = 1")
    driver_ids = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(driver_ids)} driver_ids")  # 디버깅

    # Delivery_Car 테이블에서 배송가능, insurance 1인 car_id 가져오기
    cursor.execute("SELECT car_id FROM Delivery_Car WHERE status = '배송가능' AND insurance = 1")
    car_ids = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(car_ids)} car_ids")  # 디버깅

    if not driver_ids or not car_ids or not online_payment_ids:
        print("필요한 데이터가 부족합니다. 데이터를 확인해주세요.")
        return

    # 중복된 online_payment_id를 추적하기 위한 집합
    used_online_payment_ids = set()

    # 여러 데이터 삽입할 리스트
    data_to_insert = []

    # 배치 크기 설정 (예: 한 번에 1000개씩 삽입)
    BATCH_SIZE = 1000

    # driver_id, car_id, online_payment_id의 가능한 모든 조합 반복
    for online_payment_id in online_payment_ids:
        # 랜덤하게 driver_id와 car_id 선택
        driver_id = random.choice(driver_ids)
        car_id = random.choice(car_ids)

        # 이미 사용된 online_payment_id는 건너뛰기
        if online_payment_id in used_online_payment_ids:
            continue

        # status는 배송완료 99%, 배송중사고 1% 확률로 설정
        status = random.choices(statuses, weights=status_weights, k=1)[0]

        # start_date는 오늘로부터 7일 전에서 4일 전까지 랜덤값 생성
        start_date = datetime.datetime.today() - datetime.timedelta(days=random.randint(4, 7))

        # end_date는 start_date로부터 2일 이후
        end_date = start_date + datetime.timedelta(days=2)

        # request_type은 100% 고객으로 설정
        request_type = random.choices(request_types, weights=request_weights, k=1)[0]

        # 삽입할 데이터를 리스트에 저장
        data_to_insert.append((driver_id, car_id, online_payment_id, status, start_date, end_date, request_type))

        # 사용된 online_payment_id를 집합에 추가
        used_online_payment_ids.add(online_payment_id)

        # 배치 크기 만큼 데이터가 모이면 실행
        if len(data_to_insert) >= BATCH_SIZE:
            query = """
            INSERT INTO Delivery (driver_id, car_id, online_payment_id, status, start_date, end_date, request_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.executemany(query, data_to_insert)  # 여러 데이터 삽입
                db.commit()  # 커밋
                print(f"Inserted {len(data_to_insert)} records.")  # 삽입된 데이터 수 확인
            except mysql.connector.Error as err:
                db.rollback()  # 오류 발생 시 롤백
                print(f"Error: {err}")
            data_to_insert = []  # 데이터 리스트 초기화

    # 나머지 데이터 삽입
    if data_to_insert:
        query = """
        INSERT INTO Delivery (driver_id, car_id, online_payment_id, status, start_date, end_date, request_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.executemany(query, data_to_insert)  # 나머지 데이터 삽입
            db.commit()  # 커밋
            print(f"Inserted {len(data_to_insert)} records.")  # 삽입된 데이터 수 확인
        except mysql.connector.Error as err:
            db.rollback()  # 오류 발생 시 롤백
            print(f"Error: {err}")

    # 최종 완료 메시지
    print("✅ 배송테이블 데이터 전부 삽입 완료!")

# 함수 호출
insert_delivery()
