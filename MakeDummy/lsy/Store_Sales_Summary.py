import mysql.connector
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# DB 연결 설정 (원격)
remote_conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
remote_cursor = remote_conn.cursor()

# 설정값
total_days = (datetime(2025, 3, 21) - datetime(2024, 1, 1)).days + 1
store_ids = [1, 2, 3, 4, 5]  # 매장 ID 5개

# 더미 데이터 생성 및 INSERT
print("✅ 데이터 생성 및 INSERT 시작")

for day in range(total_days):
    current_date = datetime(2024, 1, 1) + timedelta(days=day)
    print(f"🔄 {current_date.strftime('%Y-%m-%d')} 데이터 생성 중...")

    batch_data = []
    for store_id in store_ids:
        card_sales = random.randint(1000000, 5000000)
        cash_sales = random.randint(1000000, 5000000)
        point_used = random.randint(10000, 500000)
        discount_amount = random.randint(50000, 700000)
        total_sales = card_sales + cash_sales
        net_sales = total_sales - point_used - discount_amount

        batch_data.append((
            store_id, current_date.date(), card_sales, cash_sales, total_sales,
            point_used, discount_amount, net_sales
        ))

    # INSERT (batch)
    insert_query = """
    INSERT INTO Store_Sales_Summary
        (store_id, report_date, card_sales, cash_sales, total_sales, point_used, discount_amount, net_sales)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        card_sales = VALUES(card_sales),
        cash_sales = VALUES(cash_sales),
        total_sales = VALUES(total_sales),
        point_used = VALUES(point_used),
        discount_amount = VALUES(discount_amount),
        net_sales = VALUES(net_sales)
    """
    remote_cursor.executemany(insert_query, batch_data)
    remote_conn.commit()

print("🎉 모든 더미 데이터 삽입 완료!")
remote_cursor.close()
remote_conn.close()
