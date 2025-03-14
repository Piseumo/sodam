import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",      
    port= 50006,
    user="root",           
    password="1234",  
    database="sodam"
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Category;")
cursor.execute("TRUNCATE TABLE Product;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print(" 기존 데이터 삭제 완료!")

# 1. Category 데이터 삽입
categories_data = {
    "식료품": {
        "간편식": [
            "델리/치킨/초밥", "라면/즉석식품/통조림", "베이커리/잼",
            "냉장/냉동/밀키트", "과자/시리얼", "커피/차", "생수/음료"
        ],
        "식재료": [
            "과일", "쌀/잡곡", "채소", "견과", "수산물/건어물",
            "정육/계란", "장류/양념/제빵", "우유/유제품", "두부/김치/반찬"
        ]
    },
    "소모품": {
        "청소/위생 용품": {
            "청소 도구": ["먼지 제거 롤러", "극세사 걸레", "청소포", "빗자루", "청소용 브러시", "먼지털이개"],
            "청소 기기 소모품": ["진공 청소기 필터", "물걸레 청소포", "로봇청소기 필터"],
            "화장실/욕실 용품": ["욕실 탈취제", "배수구 클리너", "곰팡이 제거제", "변기 세정제"],
            "위생 용품": ["휴지", "키친타올", "손 세정제", "손 소독제", "일회용 마스크", "KF94 마스크"],
            "개인 위생 용품": ["비누", "샴푸", "린스", "바디워시", "칫솔", "치약", "면도기", "면도날"]
        },
        "주방 소모품": {
            "일회용품": ["일회용 장갑", "종이컵", "종이 접시", "플라스틱 컵", "빨대", "지퍼백", "종이 호일", "랩", "알루미늄 포일"],
            "주방 세척용품": ["주방 세제", "수세미", "철수세미", "식기 건조용 행주", "싱크대 거름망", "식기세척기 세제"]
        }
    }
}

for main_cat, sub_dict in categories_data.items():
    for sub_cat, details in sub_dict.items():
        for detail in details:
            sql = "INSERT INTO Category (main, sub, detail) VALUES (%s, %s, %s)"
            cursor.execute(sql, (main_cat, sub_cat, detail))

conn.commit()
print("✅ Category 데이터 삽입 완료!")

# Category 테이블에서 생성된 category_id 목록 가져오기
cursor.execute("SELECT category_id FROM Category")
category_ids = [row[0] for row in cursor.fetchall()]

# 2. 상품명 생성 관련 설정
adjectives = ["프리미엄", "고급", "유기농", "자연유래", "베스트셀러", "신상"]
nouns = ["샴푸", "치약", "세탁 세제", "핸드크림", "면도기", "주방 세제", "수세미", "커피", "즉석밥", "라면", "초콜릿"]
colors = ["화이트", "블랙", "핑크", "네이비", "골드", "베이지"]

# 3. Product 테이블에 더미 데이터 삽입
num_products = 100000
for _ in range(num_products):
    category_id = random.choice(category_ids)

    # 상품명 생성
    product_name = f"{random.choice(adjectives)} {random.choice(colors)} {random.choice(nouns)}"

    # 옵션 설정 (가끔 None이 나오도록 확률 조정)
    option_detail = random.choices(
        ["색상: 블랙", "색상: 화이트", "사이즈: 대", "사이즈: 중", "사이즈: 소", None], 
        weights=[2, 2, 1, 1, 1, 3],  # None이 3/10 확률로 나오도록 설정
        k=1
    )[0]

    # 더미 이미지 URL 생성
    main_image = f"https://example.com/images/{random.randint(1, 100)}.jpg"
    detail_image = f"https://example.com/images/{random.randint(101, 200)}.jpg"

    # 유통기한 설정 (식료품이면 유통기한, 소모품이면 랜덤 미래 날짜)
    expire_date = fake.date_time_between(start_date="now", end_date="+1y")

    # 용량 (식료품 & 소모품 단위 설정)
    capacity_value = random.randint(1, 100)
    capacity_unit = random.choice(["ml", "g", "L", "kg", "pcs"])

    sql = """INSERT INTO Product 
             (category_id, name, option_detail, main_image, detail_image, expire_date, capacity_value, capacity_unit)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (category_id, product_name, option_detail, main_image, detail_image, expire_date, capacity_value, capacity_unit)
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ Product 데이터 삽입 완료!")
