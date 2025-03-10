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
        cursor.execute("SELECT customer_id FROM Customer ORDER BY RAND() LIMIT 1")
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
    
    total_price = cursor.fetchone()[0] or 0  # `NULL`이 나오면 `0`으로 처리

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
    address2 = f"{random.randint(1, 50)}동 {random.randint(101, 1904)}호"  # 직접 생성
    postal_code = fake.postcode()  # 우편번호
    
    return f"{city} {district} {address} {address2} {postal_code}"

def create_online_order_data(online_cart_ids):
    for online_cart_id in online_cart_ids:
        print(f"Processing online_cart_id: {online_cart_id}")

        cursor.execute("""
            SELECT customer_id FROM Online_Cart WHERE online_cart_id = %s
        """, (online_cart_id,))
        customer_row = cursor.fetchone()
        
        if not customer_row:
            print(f"❌ No customer found for online_cart_id {online_cart_id}")
            continue  
        customer_id = customer_row[0]

        cursor.execute("""
            SELECT name FROM Customer WHERE customer_id = %s
        """, (customer_id,))
        customer_row = cursor.fetchone()
        
        if not customer_row:
            print(f"❌ No customer name found for customer_id {customer_id}")
            continue
        customer_name = customer_row[0]

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
            print(f"⚠️ No delivery address found for customer_id {customer_id}, using random Daegu address.")
            customer_address = get_daegu_address()

        if random.random() < 0.8:
            receiver_name = customer_name
            receiver_address = customer_address
        else:
            receiver_name = fake.name()
            receiver_address = get_daegu_address()

        cursor.execute("""
            SELECT point_id FROM Point 
            WHERE customer_id = %s 
            ORDER BY date_time DESC 
            LIMIT 1
        """, (customer_id,))
        point_row = cursor.fetchone()
        point_id = point_row[0] if point_row else None

        if point_id is None:
            print(f"⚠️ No point_id found for customer_id {customer_id}, inserting NULL.")

        status = random.choice(['주문 접수', '결제 완료', '배송 준비 중', '배송 중', '배송 완료', '주문 취소'])

        try:
            cursor.execute("""
                INSERT INTO online_order (online_cart_id, point_id, receiver_name, receiver_address, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (online_cart_id, point_id, receiver_name, receiver_address, status))
            conn.commit()
            print(f"✅ Successfully inserted order for cart_id {online_cart_id}")
        except Exception as e:
            print(f"❌ Error inserting order for cart_id {online_cart_id}: {e}")
            conn.rollback()

# 더미 데이터 생성 호출
create_online_cart_data(100)

# 연결 종료
cursor.close()
conn.close()