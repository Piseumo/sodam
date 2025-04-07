import mysql.connector
import random

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)

cursor = conn.cursor()

def get_customer_ids():
    cursor.execute("SELECT customer_id FROM customer")
    return [row[0] for row in cursor.fetchall()]

def get_inventory_ids():
    cursor.execute("SELECT inventory_id FROM store_inventory ORDER BY inventory_id")
    return [row[0] for row in cursor.fetchall()]

pay_methods = ["카드 결제", "현금 결제"]

customer_ids = get_customer_ids()

inventory_ids = get_inventory_ids()

print(f"📌 고객 ID 개수: {len(customer_ids)}, 상품 ID 개수: {len(inventory_ids)}")

def create_order(customer_id):
    new_order_id = None
    pay_method = random.choice(pay_methods)

    try:
        cursor.callproc("create_offline_order", (customer_id, pay_method, new_order_id))

        cursor.execute("SELECT LAST_INSERT_ID()")
        new_order_id = cursor.fetchone()[0]

        print(f"✅ 주문 생성 완료! 주문 ID: {new_order_id} (고객 ID: {customer_id})")
        conn.commit()

        return new_order_id
    except Exception as e:
        print(f"🚨 주문 생성 실패: {e}")
        return None
    
def create_order_details(order_id):
    if not order_id or not inventory_ids:
        return
    
    for _ in range(random.randint(1, 10)):
        inventory_id = random.choice(inventory_ids)
        buy_quantity = random.randint(1,10)

        try:
            cursor.callproc("create_offline_order_detail", (order_id, inventory_id, buy_quantity))
            print(f"  🛒 주문 상세 추가 완료 (상품 ID: {inventory_id}, 수량: {buy_quantity})")
            conn.commit()
        except Exception as e:
            print(f"🚨 주문 상세 추가 실패: {e}")

for _ in range(3000):
    customer_id = random.choice(customer_ids)
    order_id = create_order(customer_id)
    create_order_details(order_id)

cursor.close()
conn.close()