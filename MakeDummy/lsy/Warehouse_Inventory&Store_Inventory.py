import mysql.connector
from faker import Faker
import random
from datetime import datetime

fake = Faker("ko_KR")  # ✅ 한글 로케일 적용

# ✅ MySQL 연결 설정
conn = mysql.connector.connect(
    host="localhost",
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

# ✅ warehouse_id 고정값 설정
warehouse_id = 1
store_ids = [2, 3, 4, 5, 6]
product_ids = []


