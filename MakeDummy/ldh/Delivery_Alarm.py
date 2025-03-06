import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Faker 객체 생성
fake = Faker('ko_KR')

# MySQL 데이터베이스 연결
db = mysql.connector.connect(
    # host="192.168.0.104",  
    host="192.168.0.9",  
    port=3306,   
    user="root",    
    password="1234", 
    database="sodam"
)

# 커서 생성
cursor = db.cursor()

# 데이터 삽입 쿼리 (Delivery_Alarm 테이블)
insert_query = """
    INSERT INTO Delivery_Alarm (delivery_id, text, send_date)
    VALUES (%s, %s, %s)
"""

# 상태별 알람 내용 생성
def generate_alarm_text(status, send_date):
    # 상태에 따른 알람 텍스트 생성
    if status == '배송중':
        return f"배송이 진행 중입니다. (알람 송신일: {send_date})"
    elif status == '배송완료':
        return f"배송이 완료되었습니다. (알람 송신일: {send_date})"
    elif status == '배송중사고':
        return f"배송 중 사고가 발생했습니다. (알람 송신일: {send_date})"
    else:
        return f"상태 업데이트가 있었습니다. (알람 송신일: {send_date})"

# 알람 생성 함수
def generate_alarm_for_status_change(delivery_id, status):
    # 상태에 따른 send_date 설정
    if status == '배송중':
        cursor.execute("SELECT start_date FROM Delivery WHERE delivery_id = %s", (delivery_id,))
        result = cursor.fetchone()
        send_date = result[0].strftime('%Y-%m-%d %H:%M:%S') if result else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif status == '배송완료':
        cursor.execute("SELECT end_date FROM Delivery WHERE delivery_id = %s", (delivery_id,))
        result = cursor.fetchone()
        send_date = result[0].strftime('%Y-%m-%d %H:%M:%S') if result else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        send_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 알람 텍스트 생성
    alarm_text = generate_alarm_text(status, send_date)

    # 데이터 삽입
    cursor.execute(insert_query, (delivery_id, alarm_text, send_date))
    db.commit()
    print(f"Alarm for delivery_id {delivery_id} added: {alarm_text}, Send date: {send_date}")

# Delivery 테이블에서 status가 '배송중', '배송완료', '배송중사고'인 항목에 대해 알람을 생성
cursor.execute("""
    SELECT delivery_id, status 
    FROM Delivery 
    WHERE status IN ('배송중', '배송완료', '배송중사고')
""")  # '배송중', '배송완료', '배송중사고'인 상태만 가져옵니다.
delivery_records = cursor.fetchall()

for delivery_id, status in delivery_records:
    # 상태가 변경될 때마다 알람 추가
    generate_alarm_for_status_change(delivery_id, status)

# 커서와 데이터베이스 연결 종료
cursor.close()
db.close()

print("✅ 알람 데이터 삽입 완료!")
