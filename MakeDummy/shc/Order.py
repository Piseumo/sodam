import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="sodam"
)

cursor = conn.cursor()

# 더미 데이터 생성 함수
def create_online_cart_data(num_entries=10):
    online_cart_ids = []  # 생성된 online_cart_id를 저장할 리스트
    for _ in range(num_entries):
        # customer 테이블에서 임의로 customer_id를 가져옵니다.
        cursor.execute("SELECT id FROM customer ORDER BY RAND() LIMIT 1")
        customer_id = cursor.fetchone()[0]  # 첫 번째 열 값(즉, customer_id) 가져오기
        
        # 온라인 장바구니 삽입
        cursor.execute("""
            INSERT INTO Online_Cart (customer_id, total_price)
            VALUES (%s, %s)
        """, (customer_id, 0))  # 초기 total_price는 0으로 설정
        conn.commit()

        # 온라인 장바구니 ID 가져오기
        online_cart_id = cursor.lastrowid  # 방금 삽입된 online_cart_id
        online_cart_ids.append(online_cart_id)  # 생성된 ID를 저장

        # `Online_Cart_Product`에 제품 삽입
        create_online_cart_product_data(online_cart_id)

        # `Online_Cart`의 `total_price`를 갱신
        update_total_price(online_cart_id)

    # Online_Cart들에 대해 1대1로 Online_Order 생성
    create_online_order_data(online_cart_ids)

def create_online_cart_product_data(online_cart_id, num_entries=None):
    # num_entries가 제공되지 않으면, 1~10개의 랜덤한 개수로 설정
    if num_entries is None:
        num_entries = random.randint(1, 10)

    for _ in range(num_entries):
        # Warehouse_Inventory에서 임의의 inventory_id를 선택
        cursor.execute("SELECT inventory_id, product_id FROM Warehouse_Inventory ORDER BY RAND() LIMIT 1")
        inventory_row = cursor.fetchone()
        
        if inventory_row:
            inventory_id = inventory_row[0]  # inventory_id 값
            product_id = inventory_row[1]  # product_id 값
        else:
            continue  # 재고가 없다면 건너뛰기

        # 해당 product_id에 대해 Product_Price 테이블에서 현재 가격을 가져옴
        cursor.execute("""
            SELECT final_price FROM Product_Price
            WHERE product_id = %s ORDER BY date_time DESC LIMIT 1
        """, (product_id,))
        price_row = cursor.fetchone()
        
        if price_row:
            price = price_row[0]  # final_price 값
        else:
            price = 0  # 가격이 없으면 0으로 설정 (혹은 예외 처리)

        # 임의의 수량
        quantity = random.randint(1, 5)
        
        # Online_Cart_Product 테이블에 데이터 삽입
        cursor.execute("""
            INSERT INTO Online_Cart_Product (online_cart_id, inventory_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (online_cart_id, inventory_id, quantity, price))
        conn.commit()

def update_total_price(online_cart_id):
    # 해당 online_cart_id에 대한 total_price 계산
    cursor.execute("""
        SELECT SUM(quantity * price) FROM Online_Cart_Product
        WHERE online_cart_id = %s
    """, (online_cart_id,))
    total_price = cursor.fetchone()[0]  # 계산된 총 가격 가져오기

    # `Online_Cart` 테이블에서 total_price 업데이트
    cursor.execute("""
        UPDATE Online_Cart
        SET total_price = %s
        WHERE online_cart_id = %s
    """, (total_price, online_cart_id))
    conn.commit()

def get_daegu_address():
    city = "대구광역시"  # 대구시 고정
    district = fake.city_suffix()  # 랜덤 구 (중구, 동구, 서구 등)
    address = fake.street_name() + " " + fake.building_number()  # 도로명 + 건물번호
    address2 = fake.secondary_address()  # 상세주소 (예: 101동 202호)
    postal_code = fake.postcode()  # 우편번호
    
    return f"{city} {district} {address} {address2} {postal_code}"

def create_online_order_data(online_cart_ids):
    for online_cart_id in online_cart_ids:
        # Online_Cart에서 customer_id 가져오기
        cursor.execute("""
            SELECT customer_id FROM Online_Cart WHERE online_cart_id = %s
        """, (online_cart_id,))
        customer_id = cursor.fetchone()[0]  # 해당 장바구니의 customer_id 가져오기

        # 해당 customer_id로 Customer 테이블에서 receiver_name을 조회
        cursor.execute("""
            SELECT name FROM Customer WHERE customer_id = %s
        """, (customer_id,))
        customer_name = cursor.fetchone()[0]  # 고객의 이름 가져오기

        # 해당 customer_id의 배송지 정보 가져오기
        cursor.execute("""
            SELECT city, district, address, address2, postal_code 
            FROM Delivery_Address 
            WHERE customer_id = %s 
            ORDER BY last_update DESC 
            LIMIT 1
        """, (customer_id,))
        address_row = cursor.fetchone()

        if address_row:
            customer_address = f"{address_row[0]} {address_row[1]} {address_row[2]} {address_row[3]} {address_row[4]}"
        else:
            customer_address = None  # 배송지가 없을 경우 대비

        # 80% 확률로 고객 본인의 정보 사용, 20% 확률로 랜덤 정보 사용
        if random.random() < 0.8:
            receiver_name = customer_name  # 고객 본인의 이름 사용
            receiver_address = customer_address if customer_address else get_daegu_address()  # 고객 기본 배송지 또는 랜덤 대구 주소
        else:
            receiver_name = fake.name()  # 랜덤한 이름 생성
            receiver_address = get_daegu_address()  # 랜덤한 대구 주소 생성

        # 고객의 최신 포인트 ID 가져오기
        cursor.execute("""
            SELECT point_id FROM Point 
            WHERE customer_id = %s 
            ORDER BY date_time DESC 
            LIMIT 1
        """, (customer_id,))
        point_row = cursor.fetchone()

        if point_row:
            point_id = point_row[0]  # 가장 최근 포인트 ID 사용
        else:
            point_id = None  # 해당 고객의 포인트 내역이 없을 경우 NULL 처리

        # 주문 정보 생성
        status = random.choice(['주문 접수', '결제 완료', '배송 준비 중', '배송 중', '배송 완료', '주문 취소'])

        # Online_Order 테이블에 데이터 삽입
        cursor.execute("""
            INSERT INTO online_order (online_cart_id, point_id, receiver_name, receiver_address, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (online_cart_id, point_id, receiver_name, receiver_address, status))
        conn.commit()

# 더미 데이터 생성 호출
create_online_cart_data(10)  # 10개의 온라인 장바구니 데이터 생성

# 연결 종료
cursor.close()
conn.close()