import mysql.connector
import random
import datetime

# MySQL 연결 설정
db = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = db.cursor()

# Delivery 테이블에 더미 데이터 삽입
def insert_delivery():
    # 상태 비율 설정 (배송완료 95%, 배송중사고 5%)
    statuses = ['배송완료', '배송중사고']
    status_weights = [0.95, 0.05]

    # 요청 유형을 고객 100%로 설정
    request_types = ['고객']
    request_weights = [1.0]  # 100% 고객

    # Delivery 테이블에 데이터를 삽입하기 위한 driver_id, car_id, online_payment_id 가져오기
    cursor.execute("SELECT driver_id FROM Delivery_Driver")  # 배송기사
    driver_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT car_id FROM Delivery_Car")  # 차량
    car_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT online_payment_id FROM online_payment")  # 온라인 결제
    online_payment_ids = [row[0] for row in cursor.fetchall()]

    # Delivery 테이블에 데이터 삽입
    if driver_ids and car_ids and online_payment_ids:
        for driver_id in driver_ids:  # 모든 배송기사에 대해
            for car_id in car_ids:  # 모든 차량에 대해
                for online_payment_id in online_payment_ids:  # 모든 온라인 결제에 대해
                    # status는 배송완료 95%, 배송중사고 5% 확률로 선택
                    status = random.choices(statuses, weights=status_weights, k=1)[0]

                    # start_date는 오늘로부터 3일 이하~1년 이하 사이에 랜덤값 생성
                    start_date = datetime.datetime.today() + datetime.timedelta(days=random.randint(1, 365))  # 1일부터 365일까지 랜덤

                    # end_date는 start_date로부터 3일 이후 다만 status가 배송중사고이면 NULL값으로
                    if status == '배송중사고':
                        end_date = None  # 배송중사고 상태일 때는 end_date를 NULL로 설정
                    else:
                        end_date = start_date + datetime.timedelta(days=random.randint(3, 7))  # 3일 이후 ~ 7일 내로 설정

                    # request_type은 100% 고객으로 설정
                    request_type = random.choices(request_types, weights=request_weights, k=1)[0]

                    # Delivery 테이블에 데이터 삽입
                    query = """
                    INSERT INTO Delivery (driver_id, car_id, online_payment_id, status, start_date, end_date, request_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (driver_id, car_id, online_payment_id, status, start_date, end_date, request_type))

        db.commit()

# Delivery 테이블에 모든 데이터를 삽입
insert_delivery()

# 연결 종료
cursor.close()
db.close()

print("✅ 배송테이블 데이터 전부 삽입 완료!")
