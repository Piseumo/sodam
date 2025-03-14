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

# ✅ (1) 기존 데이터 삭제 (TRUNCATE TABLE → AUTO_INCREMENT 초기화)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Warehouse_Inventory;")
cursor.execute("TRUNCATE TABLE Store_Inventory;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

conn.commit()

print("기존 데이터 삭제 완료!")

# ✅ 변수 설정
warehouse_id = 1
store_ids = [1, 2, 3, 4, 5]
product_ids = list(range(1, 1000001))  # ✅ 상품 ID: 1~1,000,000

# ✅ Warehouse_Inventory 데이터 생성 및 삽입 (각 상품 1개씩, 총 100개)
for product_id in product_ids:
    quantity = random.randint(100, 5000)  # ✅ 창고 재고 수량
    last_updated = fake.date_time_between(start_date="-1y", end_date="now")

    sql = """
    INSERT INTO Warehouse_Inventory (warehouse_id, product_id, quantity, last_updated)
    VALUES (%s, %s, %s, %s);
    """
    values = (warehouse_id, product_id, quantity, last_updated)

    cursor.execute(sql, values)

conn.commit()
print("Warehouse_Inventory 데이터 삽입 완료!")

# ✅ Store_Inventory 데이터 생성 및 삽입 (각 매장이 50~100개 상품을 가질 수도 있도록 수정)
for store_id in store_ids:
    
    selected_products = product_ids  # ✅ 모든 매장이 100개 상품을 가짐
    
    for product_id in selected_products:
        quantity = random.randint(100, 1000)  # ✅ 매장 재고 수량
        last_updated = fake.date_time_between(start_date="-1y", end_date="now")

        sql = """
        INSERT INTO Store_Inventory (store_id, product_id, quantity, last_updated)
        VALUES (%s, %s, %s, %s);
        """
        values = (store_id, product_id, quantity, last_updated)

        cursor.execute(sql, values)

conn.commit()
print("Store_Inventory 데이터 삽입 완료!")

# ✅ 커서 및 연결 종료
cursor.close()
conn.close()

print("상품별 창고 및 매장 재고 데이터가 성공적으로 삽입되었습니다! 🚀")