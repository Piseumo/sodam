import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")

# ✅ MySQL 연결
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

# ✅ 기존 데이터 초기화
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Warehouse_Inventory;")
cursor.execute("TRUNCATE TABLE Store_Inventory;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
print("✅ 기존 재고 데이터 초기화 완료")

# ✅ ID 가져오기
cursor.execute("SELECT store_id FROM Stores")
store_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("""
    SELECT p.product_id, c.main 
    FROM Product p 
    JOIN Category c ON p.category_id = c.category_id
""")
product_infos = cursor.fetchall()

warehouse_id = 1
batch_size = 1000
inserted_count = 0

# ✅ batch 처리
for i in range(0, len(product_infos), batch_size):
    batch = product_infos[i:i+batch_size]
    warehouse_rows = []
    store_rows = []

    for product_id, main in batch:
        is_food = (main == '식료품')

        # ✅ 창고 데이터
        quantity_wh = random.randint(100, 5000)
        last_updated_wh = fake.date_time_between(start_date='-1y', end_date='now')
        location_wh = fake.bothify(text='W-###-##')
        expiration_wh = fake.date_time_between(start_date='-6M', end_date='+6M') if is_food else None

        warehouse_rows.append((warehouse_id, product_id, quantity_wh, last_updated_wh, location_wh, expiration_wh))

        # ✅ 매장들에 대한 재고 데이터
        for store_id in store_ids:
            quantity_st = random.randint(100, 1000)
            last_updated_st = fake.date_time_between(start_date='-1y', end_date='now')
            location_st = fake.bothify(text='S-###-##')
            expiration_st = fake.date_time_between(start_date='-3M', end_date='+3M') if is_food else None

            store_rows.append((store_id, product_id, quantity_st, last_updated_st, location_st, expiration_st))

    # ✅ INSERT 실행
    cursor.executemany("""
        INSERT INTO Warehouse_Inventory 
        (warehouse_id, product_id, quantity, last_updated, location, expiration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, warehouse_rows)

    cursor.executemany("""
        INSERT INTO Store_Inventory 
        (store_id, product_id, quantity, last_updated, location, expiration_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, store_rows)

    conn.commit()
    inserted_count += len(batch)
    print(f"✅ {inserted_count}개 상품 처리 완료")

cursor.close()
conn.close()
print("🎉 모든 재고 더미 데이터 삽입 완료!")
