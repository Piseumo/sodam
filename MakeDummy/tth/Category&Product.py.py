import mysql.connector
from faker import Faker
import random

fake = Faker("ko_KR")

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="112.222.157.156",
    port=50006,
    user="root",
    password="1234",
    database="sodam"
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Product;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print("✅ 기존 Product 데이터 삭제 완료!")

# Category 정보 가져오기 (category_id, main)
cursor.execute("SELECT category_id, main FROM Category")
category_list = cursor.fetchall()

# 식료품용 이름 구성
food_adjectives_1 = ["신선한", "국산", "냉장", "친환경", "유기농", "세척한", "1인용" ,"소분된" , "GAP 인증", "비살균", "무농약", "손질된"]
food_nouns_1 = [
    "대파", "고기", "계란", "사과", "참외", "양파", "배추",
    "당근", "오이", "브로콜리", "애호박", "감자", "고구마", "미나리",
    "쪽파", "레몬", "방울토마토", "표고버섯", "팽이버섯", "느타리버섯",
    "상추", "깻잎", "무", "깐마늘", "생강", "연근", "콩나물",
    "숙주", "쌀", "현미", "찹쌀", "잡곡", "두부", "김치", "우유",
    "요거트", "크림치즈", "카망베르", "계피", "호두", "잣", "아몬드"
]

food_adjectives_2 = [
    "냉동", "즉석", "달콤한", "매콤한",
    "간편식", "레토르트", "오븐에 구운", "에어프라이어용", "전자레인지용",
    "매운맛", "순한맛", "치즈맛", "마늘맛", "트러플향", "한끼용",
    "가정간편식", "밀키트형", "포장용", "혼밥용", "핫한", "바삭한",
    "쫄깃한", "촉촉한", "진한", "연한", "감칠맛", "저염", "고단백",
    "저지방", "고칼슘", "저칼로리", "풍미가득", "수제", "홈메이드", 
    "국물맛", "찜전용", "볶음전용", "구이전용", "핫팩동봉", "특제소스"
]

food_nouns_2 = [
    "만두", "라면", "삼겹살", "떡볶이", "피자", "볶음밥",
    "순대", "돈까스", "치킨너겟", "갈비찜", "잡채", "국밥",
    "카레", "햄버거", "핫도그", "오므라이스", "리조또", "스파게티",
    "볶음우동", "닭갈비", "부대찌개", "김치찌개", "된장찌개", "육개장",
    "미역국", "계란찜", "감자조림", "버섯볶음", "김밥", "유부초밥",
    "죽", "양념치킨", "간장치킨", "마늘치킨", "순살치킨", "계란말이",
    "낙지볶음", "오징어채", "건새우", "멸치볶음", "장조림", "스프"
]

# 소모품용 이름 구성
item_adjectives_1 = ["고급", "향기로운", "부드러운", "프리미엄", "항균"]
item_nouns_1 = ["샴푸", "치약", "핸드크림", "비누", "린스", "바디워시"]

item_adjectives_2 = ["강력한", "일회용", "편리한", "다용도", "습기제거"]
item_nouns_2 = [
    "청소포", "수세미", "키친타올", "물티슈", "방향제", "세제",
    "주방세제", "세탁세제", "섬유유연제", "락스", "주방행주", "고무장갑",
    "지퍼백", "랩", "알루미늄호일", "음식물쓰레기봉투", "청소브러시", "청소장갑",
    "먼지털이개", "빗자루", "쓰레기봉투", "먼지제거 롤러", "욕실세정제", "배수구클리너",
    "곰팡이제거제", "변기세정제", "휴지", "화장지", "소독스프레이", "종이컵",
    "종이접시", "일회용숟가락", "일회용포크", "일회용젓가락", "실리콘수세미", "세탁망",
    "걸레", "극세사타월", "청소기필터", "스펀지수세미", "필터백", "행주티슈"
]

# Product 더미 데이터 삽입
num_products = 10000
for _ in range(num_products):
    category_id, main_category = random.choice(category_list)

    # 상품명 생성
    if main_category == "식료품":
        if random.choice([True, False]):
            product_name = f"{random.choice(food_adjectives_1)} {random.choice(food_nouns_1)}"
        else:
            product_name = f"{random.choice(food_adjectives_2)} {random.choice(food_nouns_2)}"
    else:
        if random.choice([True, False]):
            product_name = f"{random.choice(item_adjectives_1)} {random.choice(item_nouns_1)}"
        else:
            product_name = f"{random.choice(item_adjectives_2)} {random.choice(item_nouns_2)}"

        # 조건별 필드 처리
    if main_category == "식료품":
        option_detail = None
        capacity_value = random.randint(1, 100)
        capacity_unit = random.choice(["ml", "g", "L", "kg", "pcs"])
    else:
        option_detail = random.choices(
            ["색상: 블랙", "색상: 화이트", "사이즈: 대", "사이즈: 중", "사이즈: 소", None],
            weights=[2, 2, 1, 1, 1, 3],
            k=1
        )[0]
        capacity_value = None
        capacity_unit = None

    # 이미지 URL
    main_image = f"https://example.com/images/{random.randint(1, 100)}.jpg"
    detail_image = f"https://example.com/images/{random.randint(101, 200)}.jpg"

    # DB 삽입
    sql = """
        INSERT INTO Product 
        (category_id, name, option_detail, main_image, detail_image, capacity_value, capacity_unit)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        category_id, product_name, option_detail,
        main_image, detail_image, capacity_value, capacity_unit
    )
    cursor.execute(sql, values)


conn.commit()
cursor.close()
conn.close()

print("✅ Product 데이터 삽입 완료!")
