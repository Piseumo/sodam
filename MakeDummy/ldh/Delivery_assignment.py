import mysql.connector
import random
from datetime import datetime  # 현재 날짜와 시간을 가져오는 모듈

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

# "결제 완료" 상태인 주문들의 order_id와 receiver_address 가져오기
query_orders = """
    SELECT order_id, receiver_address
    FROM online_order
    WHERE status = '결제 완료';
"""
cursor.execute(query_orders)

# 쿼리 결과 가져오기
orders = cursor.fetchall()

# 30건만 처리하기
orders = orders[:30]  # orders 리스트에서 처음 30건만 가져오기

# 확인: orders에 데이터가 들어왔는지 출력
if not orders:
    print("No orders found in the database.")
else:
    print(f"Found {len(orders)} orders.")

# 배송기사 드라이버 ID 조건에 맞는 드라이버 가져오기
query_drivers = """
    SELECT driver_id, zone
    FROM delivery_driver
    WHERE status = '근무가능'
    AND training_check = 1
    AND insurance = 1;
"""
cursor.execute(query_drivers)

# 쿼리 결과 가져오기
drivers = cursor.fetchall()

# 차량 상태가 '배송가능'이고 insurance가 1인 차량을 가져오는 함수
def get_available_car():
    query = """
        SELECT car_id 
        FROM delivery_car 
        WHERE status = '배송가능' AND insurance = 1;
    """
    cursor.execute(query)
    cars = cursor.fetchall()
    return [car[0] for car in cars]  # 차량 ID 리스트 반환

# 배송기사별 배송 건수를 추적하기 위한 쿼리
def get_driver_delivery_count(driver_id):
    query = """
        SELECT COUNT(*) 
        FROM delivery_assignment
        WHERE driver_id = %s;
    """
    cursor.execute(query, (driver_id,))
    return cursor.fetchone()[0]

# 배송기사와 해당 차량을 매칭하는 딕셔너리 (한 번 할당된 차량을 계속 할당)
driver_car_map = {}

# 지역에 맞는 area 값을 계산하는 함수
def get_area(receiver_address):
    if '서구' in receiver_address and '달서구' not in receiver_address:
        return 'A'
    elif '동구' in receiver_address:
        return 'B'
    elif '남구' in receiver_address:
        return 'C'
    elif '달서구' in receiver_address:
        return 'D'
    elif '북구' in receiver_address:
        return 'E'
    elif '수성구' in receiver_address:
        return 'F'
    elif '중구' in receiver_address:
        return 'G'
    else:
        return 'I'

# 배송기사 zone에 맞는 area를 결정하는 함수
def get_driver_area(zone):
    if zone == '서구':
        return 'A'
    elif zone == '동구':
        return 'B'
    elif zone == '남구':
        return 'C'
    elif zone == '달서구':
        return 'D'
    elif zone == '북구':
        return 'E'
    elif zone == '수성구':
        return 'F'
    elif zone == '중구':
        return 'G'
    else:
        return 'I'

# delivery_assignment 테이블에 더미 데이터 삽입 (중복된 order_id를 확인 후 삽입)
for order_id, receiver_address in orders:
    # "order_id"가 이미 delivery_assignment에 존재하는지 확인
    query_check_order = """
        SELECT COUNT(*) 
        FROM delivery_assignment 
        WHERE order_id = %s;
    """
    cursor.execute(query_check_order, (order_id,))
    order_exists = cursor.fetchone()[0]

    # 만약 order_id가 이미 존재하면 건너뛰기
    if order_exists > 0:
        print(f"Skipping order_id {order_id}, already assigned.")
        continue

    # 지역 계산
    area = get_area(receiver_address)  # receiver_address에 따른 지역
    # 드라이버가 해당 지역에 있을 경우만 할당
    assigned = False  # 드라이버 할당 여부
    for driver_id, driver_zone in drivers:
        # 지역이 맞고, 해당 드라이버가 배송 건수가 10건 미만인 경우에만 할당
        if area == get_driver_area(driver_zone):
            driver_delivery_count = get_driver_delivery_count(driver_id)
            if driver_delivery_count < 10:  # 배송 건수가 10건 미만인 경우에만 할당
                # 차량 할당
                if driver_id not in driver_car_map:
                    # 아직 차량이 할당되지 않은 경우, 차량을 랜덤으로 선택
                    available_cars = get_available_car()
                    if available_cars:
                        assigned_car_id = random.choice(available_cars)
                        driver_car_map[driver_id] = assigned_car_id  # 해당 배송기사에게 차량 할당
                    else:
                        continue  # 사용할 수 있는 차량이 없으면 넘기기

                # 이미 할당된 차량 사용
                assigned_car_id = driver_car_map[driver_id]

                # 현재 날짜와 시간을 list_update로 설정
                list_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 드라이버와 차량이 할당되었으므로 삽입
                insert_query = """
                    INSERT INTO delivery_assignment (order_id, driver_id, car_id, area, is_checked, list_update)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (order_id, driver_id, assigned_car_id, area, 0, list_update))  # is_checked 값 0 전달

                # lastrowid로 assignment_id를 가져옴
                assignment_id = cursor.lastrowid

                # 로그 출력 (INSERT 된 데이터 확인)
                print(f"Inserted: assignment_id={assignment_id}, order_id={order_id}, driver_id={driver_id}, car_id={assigned_car_id}, area={area}, is_checked=0, list_update={list_update}")

                assigned = True
                break  # 배송 건수가 10건 미만인 드라이버가 할당되었으므로 더 이상 반복하지 않음
    
    # 만약 아직 할당되지 않았다면, 배송 건수가 10건 미만인 다른 드라이버를 찾아야 함
    if not assigned:
        for driver_id, driver_zone in drivers:
            driver_delivery_count = get_driver_delivery_count(driver_id)
            if driver_delivery_count < 10:
                # 지역이 맞는 드라이버가 없을 경우에도, 배송 건수가 10건 미만인 드라이버로 할당
                if area == get_driver_area(driver_zone):
                    # 차량 할당
                    if driver_id not in driver_car_map:
                        # 아직 차량이 할당되지 않은 경우, 차량을 랜덤으로 선택
                        available_cars = get_available_car()
                        if available_cars:
                            assigned_car_id = random.choice(available_cars)
                            driver_car_map[driver_id] = assigned_car_id  # 해당 배송기사에게 차량 할당
                        else:
                            continue  # 사용할 수 있는 차량이 없으면 넘기기

                    # 이미 할당된 차량 사용
                    assigned_car_id = driver_car_map[driver_id]

                    # 현재 날짜와 시간을 list_update로 설정
                    list_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    insert_query = """
                        INSERT INTO delivery_assignment (order_id, driver_id, car_id, area, is_checked, list_update)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(insert_query, (order_id, driver_id, assigned_car_id, area, 0, list_update))  # is_checked 값 0 전달

                    # lastrowid로 assignment_id를 가져옴
                    assignment_id = cursor.lastrowid

                    # 로그 출력 (INSERT 된 데이터 확인)
                    print(f"Inserted: assignment_id={assignment_id}, order_id={order_id}, driver_id={driver_id}, car_id={assigned_car_id}, area={area}, is_checked=0, list_update={list_update}")
                    break

# 커밋하여 데이터 반영
db.commit()

# 연결 종료
cursor.close()
db.close()
