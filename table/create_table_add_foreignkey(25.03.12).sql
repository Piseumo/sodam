-- 1. 테이블 생성
use sodam;

CREATE TABLE Customer (
    customer_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '고객명',
    email VARCHAR(255) NOT NULL COMMENT '고객 이메일',
    phone VARCHAR(255) NOT NULL COMMENT '휴대폰 번호',
    password VARCHAR(255) NULL COMMENT '비밀번호',
    login_type ENUM('Form', 'Kakao', 'Google') NOT NULL COMMENT '로그인 타입'
);

CREATE TABLE Point (
    point_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    total_amount INT NULL COMMENT '결제 금액',
    current_points INT NOT NULL COMMENT '현재 포인트',
    type ENUM('Earned', 'Used', 'Expired') NOT NULL COMMENT '포인트 유형',
    delta INT NOT NULL COMMENT '포인트 증감량',
    total_points INT NOT NULL COMMENT '총 포인트',
    date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '포인트 적립/차감 시간'
);

CREATE TABLE Warehouse_Orders_Log (
    log_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id BIGINT NOT NULL,
    status ENUM('요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소') NOT NULL COMMENT '상태',
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Delivery_Address (
    address_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    city VARCHAR(255) NOT NULL COMMENT '시',
    district VARCHAR(255) NOT NULL COMMENT '구',
    address VARCHAR(255) NOT NULL COMMENT '주소',
    address2 VARCHAR(255) NOT NULL COMMENT '상세 주소',
    postal_code VARCHAR(10) NOT NULL COMMENT '우편번호',
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Grade (
    grade_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    name ENUM('Normal', 'VIP', 'VVIP', 'SVIP') NOT NULL COMMENT '등급',
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accumulated_amount BIGINT NOT NULL COMMENT '총 누적 결제 금액',
    reason VARCHAR(255) NULL COMMENT '변경 사유'
);

CREATE TABLE Training_Log (
    training_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    complete_date DATE NOT NULL
);

CREATE TABLE Store_Order_Logs (
    log_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id BIGINT NOT NULL,
    status ENUM('요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소') NOT NULL COMMENT '상태',
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '변동 일자'
);

CREATE TABLE Warehouse_Inventory (
    inventory_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    warehouse_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Delivery_Car (
    car_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    number VARCHAR(255) NOT NULL COMMENT '차량번호(1t 탑차로 통일)',
    status ENUM('배송가능', '수리중', '배송중', '고장') NOT NULL COMMENT '차량 상태',
    insert_date DATE NOT NULL COMMENT '차량 입고일',
    last_activity_date DATE NULL COMMENT '마지막 활동일',
    insurance BOOLEAN NOT NULL COMMENT '차량보험'
);

CREATE TABLE Warehouses (
    warehouse_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '물류센터 이름',
    contact_number VARCHAR(255) NOT NULL COMMENT '물류센터 전화번호',
    address TEXT NOT NULL COMMENT '물류센터 주소',
    manager_id BIGINT NOT NULL COMMENT '물류센터 관리자',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜',
    registration_number VARCHAR(255) NOT NULL UNIQUE COMMENT '사업자 등록번호',
    industry_type ENUM('물류') NOT NULL COMMENT '산업 유형'
);

CREATE TABLE QnA (
    qna_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    inquiry_content TEXT NOT NULL COMMENT '문의 내용',
    image VARCHAR(255) NULL COMMENT '첨부 사진',
    inquiry_time DATETIME NOT NULL COMMENT '문의 시간',
    status ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending' COMMENT '답변 상태',
    employee_id BIGINT NULL COMMENT '답변한 직원',
    answer_time DATETIME NULL COMMENT '답변 시간',
    answer_content TEXT NULL COMMENT '답변 내용'
);

CREATE TABLE Offline_Cart (
    offline_cart_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    c_id BIGINT NOT NULL,
    total_price INT NOT NULL
);

CREATE TABLE Warehouse_Orders_Details (
    detail_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Online_Cart` (
    `online_cart_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `total_price` INT NOT NULL,
    -- 외래 키 설정
    CONSTRAINT fk_customer_id FOREIGN KEY (`customer_id`) REFERENCES `Customer` (`customer_id`)
);

CREATE TABLE Store_Order_Details (
    detail_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    request_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL COMMENT '상품 수량',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 일자'
);

CREATE TABLE Delivery_Review (
    review_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    point INT NULL COMMENT '리뷰점수',
    content VARCHAR(255) NULL COMMENT '리뷰내용',
    insert_date DATE NOT NULL COMMENT '등록날짜',
    update_date DATE NULL COMMENT '수정날짜',
    delete_date DATE NULL COMMENT '삭제날짜',
    delivery_id BIGINT NOT NULL
);

CREATE TABLE Delivery (
    delivery_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    car_id BIGINT NOT NULL,
    online_payment_id BIGINT NOT NULL,
    status ENUM('배송준비', '배송중', '배송완료', '배송중사고') NOT NULL COMMENT '배송 상태',
    start_date DATETIME NULL COMMENT '배송출발일',
    end_date DATE NULL COMMENT '배송완료일',
    request_type ENUM('물류센터', '고객') NOT NULL COMMENT '요청 유형'
);

CREATE TABLE Delivery_Price (
    price_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    price INT NOT NULL COMMENT '배송비용',
    option_type ENUM('일반배송', '새벽배송', '예약배송') NOT NULL COMMENT '배송 옵션',
    weight DOUBLE NOT NULL COMMENT '무게 단위(kg)'
);

CREATE TABLE Offline_Card (
    card_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    card_code VARCHAR(3) NOT NULL COMMENT '신용카드사별 코드',
    card_name VARCHAR(20) NOT NULL COMMENT '결제 카드사 이름 예) 비씨',
    card_num VARCHAR(20) NULL COMMENT '카드번호 앞 6자 마지막 4자를 제외한 가운데 숫자 마스킹 처리됨 예) 536112******1234',
    card_quota VARCHAR(3) NOT NULL COMMENT '할부개월 0:일시불, 2:2개월, 3:3개월 …',
    is_interest_free TINYINT(1) NOT NULL DEFAULT 0 COMMENT '상점분담무이자 여부 true:무이자, false:일반',
    card_type VARCHAR(10) NULL COMMENT '카드 구분 (credit:신용, check:체크)',
    can_part_cancel TINYINT(1) NOT NULL COMMENT '부분취소 가능 여부 true:가능, false:불가능',
    acqu_card_code VARCHAR(3) NOT NULL COMMENT '매입카드사코드',
    acqu_card_name VARCHAR(100) NOT NULL COMMENT '매입카드사명'
);

CREATE TABLE Discounts (
    discounts_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    rate INT NULL COMMENT '할인율',
    reason VARCHAR(255) NULL COMMENT '할인 사유',
    start DATETIME NULL COMMENT '할인 시작 날짜',
    end DATETIME NULL COMMENT '할인 종료 날짜',
    price_id BIGINT NOT NULL
);

CREATE TABLE Product_Price (
    price_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    current_price INT NULL COMMENT '원래 가격',
    type ENUM('Increase', 'Decrease') NULL COMMENT '증감 타입',
    delta INT NULL COMMENT '증감 가격',
    reason VARCHAR(255) NULL COMMENT '가격 변동 사유',
    final_price INT NOT NULL COMMENT '최종 가격',
    date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Delivery_Return (
    return_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    status ENUM('파손', '잘못배송', '수량부족', '상태불량') NOT NULL COMMENT '반품 상태',
    application_date DATE NOT NULL COMMENT '신청일',
    drop_date DATE NULL COMMENT '배송기사 반송품 회수일',
    return_date DATE NULL COMMENT '반송품 도착일(물류센터 도착일)',
    return_complete_date DATE NULL COMMENT '반송 최종 완료일 (ex: 환불금 고객 지급까지)',
    status_check ENUM('검사대기', '검사완료') NOT NULL COMMENT '검사 상태',
    employee_id BIGINT NOT NULL,
    return_types ENUM('재배송', '환불', '교환') NULL COMMENT '반품 유형',
    delivery_id BIGINT NOT NULL
);

CREATE TABLE offline_cancels (
    cancels_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tid VARCHAR(30) NOT NULL COMMENT '승인 취소 거래번호',
    amount INT NOT NULL COMMENT '취소금액',
    cancelled_at DATETIME NOT NULL COMMENT '취소된 시각 ISO 8601',
    reason VARCHAR(100) NOT NULL COMMENT '취소 사유',
    receipt_url VARCHAR(200) NOT NULL COMMENT '취소에 대한 매출전표 확인 URL',
    coupon_amt INT NULL COMMENT '쿠폰 취소 금액'
);

CREATE TABLE `online_order` (
    `order_id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `online_cart_id` BIGINT NOT NULL,
    `point_id` BIGINT NOT NULL,
    `receiver_name` VARCHAR(255) NULL,
    `receiver_address` VARCHAR(255) NOT NULL,
    `status` ENUM('주문 접수', '결제 완료', '배송 준비 중', '배송 중', '배송 완료', '주문 취소') NOT NULL,
    -- 외래 키 설정
    CONSTRAINT fk_online_cart_id FOREIGN KEY (`online_cart_id`) REFERENCES `Online_Cart` (`online_cart_id`),
    CONSTRAINT fk_point_id FOREIGN KEY (`point_id`) REFERENCES `Point` (`point_id`)
);

CREATE TABLE online_card (
    card_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    amount INT NOT NULL COMMENT '결제 요청 금액',
    issuer_code INT NOT NULL COMMENT '카드 발급사 코드',
    acquirer_code INT NOT NULL COMMENT '카드 매입사 코드',
    number VARCHAR(255) NOT NULL COMMENT '카드번호 마스킹',
    installment_plan_months INT NOT NULL DEFAULT 0 COMMENT '할부 개월 수',
    approve_no VARCHAR(8) NOT NULL COMMENT '카드사 승인 번호',
    use_card_point TINYINT NOT NULL DEFAULT 0 COMMENT '카드사 포인트 사용 여부',
    card_type VARCHAR(20) NOT NULL COMMENT '카드 종류',
    owner_type VARCHAR(20) NOT NULL COMMENT '카드 소유자 종류',
    acquire_status ENUM('READY', 'REQUESTED', 'COMPLETED', 'CANCEL_REQUEST', 'CANCELED') NOT NULL COMMENT '매입 상태',
    is_interested_free TINYINT NOT NULL DEFAULT 0 COMMENT '무이자 할부 적용 여부'
);

CREATE TABLE Store_Order_Requests (
    request_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT NOT NULL,
    quantity INT NOT NULL COMMENT '요청 수량',
    status ENUM('요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소') NOT NULL COMMENT '상태',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 일자',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 일자'
);
CREATE TABLE Online_Easy_Pay (
    easy_pay_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(255) NOT NULL COMMENT '선택한 간편결제사 코드',
    amount INT NOT NULL COMMENT '간편결제로 결제한 금액',
    discount_amount INT NULL COMMENT '간편결제 서비스의 포인트로 할인된 금액'
);
CREATE TABLE `online_cancels` (
    `cancels_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '결제 취소 ID',
    `transaction_key` VARCHAR(64) NOT NULL COMMENT '취소건의 키값',
    `cancel_reason` VARCHAR(255) NOT NULL COMMENT '결제를 취소한 이유',
    `tax_exemption_amount` INT NOT NULL DEFAULT 0 COMMENT '취소된 금액 중 과세 제외 금액(컵 보증금 등)',
    `canceled_at` DATETIME NOT NULL COMMENT '결제 취소가 일어난 날짜및시간 정보',
    `transfer_discount_amount` INT NOT NULL DEFAULT 0 COMMENT '퀵계좌이체 서비스의 즉시할인에서 취소된 금액',
    `easyPay_discount_amount` INT NOT NULL DEFAULT 0 COMMENT '간편결제 서비스의 포인트, 쿠폰, 즉시할인과 같은 적립식 결제수단에서 취소된 금액',
    `cancel_amount` INT NOT NULL COMMENT '결제를 취소한 금액',
    `tax_free_amount` INT NOT NULL COMMENT '취소된 금액 중 면세 금액',
    `refundable_amount` INT NOT NULL COMMENT '결제 취소 후 환불 가능한 잔액',
    `cancel_status` VARCHAR(20) NOT NULL COMMENT '결제 취소 진행 상태(DONE, IN_PROGRESS, ABORTED-취소 실패)',
    `cancel_request_id` VARCHAR(255) NULL
);


CREATE TABLE `online_payment` (
    `online_payment_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `mid` VARCHAR(255) NOT NULL DEFAULT 'tosspayments',
    `last_transaction_key` VARCHAR(64) NOT NULL COMMENT '최초 결제 승인 시 키 값 -> 마지막 거래의 키 값',
    `payment_key` VARCHAR(200) NOT NULL COMMENT 'unique',
    `order_id` BIGINT NOT NULL,  -- BIGINT로 수정
    `order_name` VARCHAR(255) NOT NULL COMMENT 'ex) 상품명 외 2개',
    `tax_exemption_amount` INT NOT NULL DEFAULT 0 COMMENT '과세를 제외한 결제 금액(컵 보증금 등)',
    `status` VARCHAR(20) NOT NULL COMMENT '결제 처리 상태 (READY, IN_PROGRESS, WAITING_FOR_DEPOSIT, DONE, CANCELED, PARTIAL_CANCELED, ABORTED, EXPIRED)',
    `requested_at` DATETIME NOT NULL COMMENT '결제가 일어난 날짜와 시간 정보(결제 요청 시간)',
    `approved_at` DATETIME NULL COMMENT '결제 승인이 일어난 날짜와 시간 정보(결제 승인 시간)',
    `use_escrow` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '에스크로(제품 수령 후 결제) 여부',
    `culture_expense` INT NOT NULL DEFAULT 0 COMMENT '문화비 사용여부(계좌 결제 시에만)  따라서 우리 서비스에서는 항상 0(false) 반환 받음',
    `discount_amount` INT NULL COMMENT '카드 결제사 즉시 할인 프로모션 정보, 즉시 할인 프로모션이 적용 됬을 때만 생성',
    `secret` VARCHAR(50) NULL COMMENT '웹훅을 검증하는 최대 50자 값입니다. 가상계좌 웹훅 이벤트 본문으로 돌아온 secret과 같으면 정상적인 웹훅입니다. 결제 상태 웹훅 이벤트로 돌아오는 Payment 객체의 secret과 같으면 정상적인 웹훅입니다.',
    `type` VARCHAR(10) NOT NULL COMMENT '결제 타입 정보(NORMAL, BILLING, BRANDPAY) - 우리는 일반 결제, 간편 결제만 사용해서 NORMAL만 받아올 듯',
    `country` VARCHAR(2) NOT NULL COMMENT '결제한 국가입니다. ISO-3166의 두 자리 국가 코드 형식',
    `failure_code` VARCHAR(5) NULL COMMENT '결제 실패 코드',
    `failure_message` VARCHAR(510) NULL COMMENT '결제 실패 메시지',
    `is_partial_cancelable` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '부분 취소 가능 여부',
    `reciept_url` VARCHAR(200) NULL COMMENT '구매자에게 제공할 수 있는 결제수단별 영수증입니다. 카드 결제는 매출전표, 가상계좌는 무통장 거래 명세서, 계좌이체・휴대폰・상품권 결제는 결제 거래 내역 확인서가 제공',
    `check_out_url` VARCHAR(200) NULL COMMENT '결제창이 열리는 주소',
    `currency` VARCHAR(5) NOT NULL COMMENT '결제할 때 사용한 통화',
    `total_amount` INT NOT NULL COMMENT '총 결제 금액입니다. 결제가 취소되는 등 결제 상태가 변해도 최초에 결제된 결제 금액으로 유지',
    `balance_amount` INT NOT NULL COMMENT '취소할 수 있는 금액(잔고)입니다. 이 값은 결제 취소나 부분 취소가 되고 나서 남은 값입니다. 결제 상태 변화에 따라 vat, suppliedAmount, taxFreeAmount, taxExemptionAmount와 함께 값이 변합니다.',
    `supplied_amount` INT NOT NULL COMMENT '공급가액입니다. 결제 취소 및 부분 취소가 되면 공급가액도 일부 취소되어 값이 바뀝니다',
    `vat` INT NOT NULL COMMENT '부가세입니다. 결제 취소 및 부분 취소가 되면 부가세도 일부 취소되어 값이 바뀝니다. (결제 금액 amount - 면세 금액 taxFreeAmount) / 11 후 소수점 첫째 자리에서 반올림해서 계산합니다.  (e.g. 결제 금액이 10,000원이고, 면세 금액이 3,000원이라면 부가세는 (10000-3000)/11 = 636.3636..을 반올림한 값 636원입니다.)',
    `tax_free_amount` INT NOT NULL DEFAULT 0 COMMENT '결제 금액 중 면세 금액입니다. 결제 취소 및 부분 취소가 되면 면세 금액도 일부 취소되어 값이 바뀝니다.  * 일반 상점일 때는 면세 금액으로 0이 돌아옵니다. 면세 상점, 복합 과세 상점일 때만 면세 금액이 돌아옵니다',
    `method` VARCHAR(20) NOT NULL COMMENT '일발 결제 시 - "카드, 가상계좌, 계좌 이체, 휴대폰" , 간편 결제 시 - "간편 결제"     우리는 "카드", "간편 결제" 두개만 사용 예정',
    `version` VARCHAR(50) NOT NULL DEFAULT '2022-11-16' COMMENT 'Payment 객체의 응답 버전입니다. 버전 2022-06-08부터 날짜 기반 버저닝을 사용',
    -- 외래 키 제약 조건 추가
    CONSTRAINT fk_order_id FOREIGN KEY (`order_id`) REFERENCES `online_order` (`order_id`),
    -- card_id, easy_pay_id, cancels_id 컬럼 추가
    `card_id` BIGINT NULL,
    `easy_pay_id` BIGINT NULL,
    `cancels_id` BIGINT NULL,
    CONSTRAINT fk_card_id FOREIGN KEY (`card_id`) REFERENCES `online_card` (`card_id`),
    CONSTRAINT fk_easy_pay_id FOREIGN KEY (`easy_pay_id`) REFERENCES `Online_Easy_Pay` (`easy_pay_id`),
    CONSTRAINT fk_cancels_id FOREIGN KEY (`cancels_id`) REFERENCES `online_cancels` (`cancels_id`)
);
CREATE TABLE offline_cash (
    offline_cash_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount INT NOT NULL COMMENT '결제 금액',
    currency VARCHAR(3) NOT NULL DEFAULT 'KRW' COMMENT '사용 통화',
    pay_date DATETIME NOT NULL COMMENT '결제 시간',
    status ENUM('PENDING', 'COMPLETE', 'CANCELED') NOT NULL COMMENT '결제 상태',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '결제 생성 시간',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 시간',
    cash_receipt_request_num VARCHAR(50) NULL COMMENT '현금 영수증 요청 번호',
    cash_receipt_approval_num VARCHAR(50) NULL COMMENT '현금 영수증 승인 번호'
);


CREATE TABLE Delivery_Alarm (
    alarm_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    delivery_id BIGINT NOT NULL,
    text TEXT NULL COMMENT '알람 내용',
    send_date DATE NOT NULL COMMENT '알람 송신 날짜'
);



CREATE TABLE Delivery_Accident_Log (
    accident_log_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    delivery_id BIGINT NOT NULL,
    log_types ENUM('차량사고', '배송품파손', '운전기사이상', '기상이변', '도로정체') NOT NULL COMMENT '사고 유형',
    text TEXT NULL COMMENT '사고 내용',
    status ENUM('사고접수', '처리중', '처리완료') NOT NULL COMMENT '사고 처리 상태',
    accident_date DATE NULL COMMENT '사고 발생일',
    report_date DATE NOT NULL COMMENT '사고 등록일',
    complete_date DATE NULL COMMENT '처리 완료일'
);

CREATE TABLE Product (
    product_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL COMMENT '상품명',
    option_detail VARCHAR(255) NULL COMMENT '상품 옵션',
    main_image VARCHAR(255) NOT NULL COMMENT '메인 이미지',
    detail_image VARCHAR(255) NOT NULL COMMENT '상세 이미지',
    expire_date DATETIME NULL COMMENT '유효기간',
    capacity_value INT NULL COMMENT '상품용량 값',
    capacity_unit VARCHAR(20) NULL COMMENT '상품용량 단위'
);

CREATE TABLE Offline_Order (
    order_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    offline_cart_id BIGINT NOT NULL,
    point_id BIGINT NOT NULL,
    pay_method ENUM('카드 결제', '현금 결제') NOT NULL COMMENT '결제 방식',
    status ENUM('결제 대기', '결제 완료') NOT NULL COMMENT '결제 상태'
);

CREATE TABLE Store_Inventory (
    inventory_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL COMMENT '재고 수량',
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Delivery_Option (
    option_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    price_id BIGINT NOT NULL,
    request_datetime DATE NULL COMMENT '요청 일시'
);

CREATE TABLE Offline_Cart_Product (
    cart_product_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    offline_cart_id BIGINT NOT NULL,
    inventory_id BIGINT NOT NULL,
    quantity TINYINT NOT NULL,
    price INT NOT NULL
);

CREATE TABLE Category (
    category_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    main VARCHAR(255) NOT NULL COMMENT '대분류',
    sub VARCHAR(255) NOT NULL COMMENT '중분류',
    detail VARCHAR(255) NOT NULL COMMENT '소분류'
);

CREATE TABLE Offline_Payment (
    offline_payment_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '오프라인 결제 ID',
    result_code VARCHAR(4) NOT NULL COMMENT '0000 - 성공, 그 외 실패',
    result_message VARCHAR(100) NOT NULL COMMENT '결과 메시지',
    tid VARCHAR(30) NOT NULL COMMENT '결제 승인 키',
    cancelled_tid VARCHAR(30) NULL COMMENT '취소 거래 키',
    order_id BIGINT NOT NULL,
    card_id BIGINT NOT NULL,
    cancels_id BIGINT NOT NULL,
    edi_date DATETIME NULL COMMENT '응답 전문 생성 일시',
    signature VARCHAR(256) NULL COMMENT '위변조 검증 데이터',
    status ENUM('paid', 'ready', 'failed', 'cancelled', 'partialCancelled', 'expired') NOT NULL COMMENT '결제 상태',
    paid_at DATETIME NOT NULL COMMENT '결제 완료 시점',
    failed_at DATETIME NOT NULL COMMENT '결제 실패 시점',
    cancelled_at DATETIME NOT NULL COMMENT '결제 취소 시점',
    pay_method ENUM('card', 'vbank', 'naverpay', 'kakaopay', 'payco', 'ssgpay', 'samsungpay') NOT NULL COMMENT '결제 수단',
    amount INT NOT NULL COMMENT '결제 금액',
    balance_amt INT NOT NULL COMMENT '취소 가능 잔액',
    goods_name VARCHAR(40) NOT NULL COMMENT '상품명',
    mall_reserved VARCHAR(500) NULL COMMENT '상점 정보 전달용 필드',
    use_escrow TINYINT NOT NULL DEFAULT 0 COMMENT '에스크로 거래 여부',
    currency VARCHAR(3) NOT NULL DEFAULT 'KRW' COMMENT '결제 승인 화폐 단위',
    channel ENUM('pc', 'mobile') NULL COMMENT '결제 채널',
    approve_no VARCHAR(30) NULL COMMENT '제휴사 승인 번호',
    buyer_name VARCHAR(30) NULL COMMENT '구매자 명',
    buyer_tel VARCHAR(40) NULL COMMENT '구매자 전화번호',
    buyer_email VARCHAR(60) NULL COMMENT '구매자 이메일',
    issued_cash_receipt TINYINT NOT NULL DEFAULT 0 COMMENT '현금 영수증 발급 여부',
    receipt_url VARCHAR(200) NULL COMMENT '매출전표 확인 URL'
);

CREATE TABLE Employees (
    employee_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '직원 이름',
    phone VARCHAR(255) NOT NULL COMMENT '직원 휴대폰번호',
    email VARCHAR(255) NULL COMMENT '직원 이메일',
    store_id BIGINT NULL COMMENT '매장 직원',
    warehouse_id BIGINT NULL COMMENT '물류센터 직원',
    role ENUM('고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사'),
    hire_date DATE NOT NULL COMMENT '고용 날짜',
    salary DECIMAL(10, 2) NOT NULL COMMENT '급여',
    location_type ENUM('매장', '물류센터') NOT NULL COMMENT '근무 장소',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜',
    insurance BOOLEAN NOT NULL COMMENT '보험 가입 여부'
);

CREATE TABLE `Online_Cart_Product` (
    `cart_product_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `online_cart_id` BIGINT NOT NULL,
    `inventory_id` BIGINT NOT NULL,
    `quantity` TINYINT NOT NULL,
    `price` INT NOT NULL,
    -- 외래 키 설정
    CONSTRAINT fk_online_cart_product_online_cart_id FOREIGN KEY (`online_cart_id`) REFERENCES `Online_Cart` (`online_cart_id`),  -- 외래 키 이름 변경
    CONSTRAINT fk_inventory_id FOREIGN KEY (`inventory_id`) REFERENCES `Warehouse_Inventory` (`inventory_id`)
);

CREATE TABLE Stores (
    store_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '매장 이름',
    contact_number VARCHAR(255) NOT NULL COMMENT '매장 전화번호',
    open_time DATETIME NOT NULL COMMENT '개장 시간',
    close_time DATETIME NOT NULL COMMENT '폐장 시간',
    address TEXT NOT NULL COMMENT '매장 주소',
    status ENUM('운영', '휴점', '폐점') NOT NULL DEFAULT '운영' COMMENT '매장 운영 상태',
    manager_id BIGINT NOT NULL COMMENT '매장 관리자',
    registration_number VARCHAR(255) NOT NULL UNIQUE COMMENT '사업자 등록번호',
    industry_type ENUM('소매업') NOT NULL DEFAULT '소매업' COMMENT '업종',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜'
);

CREATE TABLE Delivery_Driver (
    driver_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    status ENUM('근무가능', '병가', '휴가', '배송중사고', '배송중') NOT NULL COMMENT '근무 상태',
    training_check BOOLEAN NOT NULL COMMENT '교육훈련 유무',
    insurance BOOLEAN NOT NULL COMMENT '보험가입 유무',
    zone ENUM('서구', '동구', '남구', '달서구', '북구', '수성구', '중구') NOT NULL COMMENT '근무 지역'
);

CREATE TABLE Warehouse_Orders_Requests (
    request_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    warehouse_id BIGINT NOT NULL,
    type ENUM('입고', '출고') NOT NULL COMMENT '요청 유형',
    source ENUM('매장발주', '공급처발주', '온라인주문') NOT NULL COMMENT '발주 출처',
    status ENUM('요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소') NOT NULL COMMENT '상태',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 생성 날짜',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '요청 수정 날짜'
);



CREATE TABLE Review (
    review_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL COMMENT '리뷰 작성자',
    product_id BIGINT NOT NULL COMMENT '리뷰 상품',
    star TINYINT NOT NULL DEFAULT 1 COMMENT '별점 (1~5)',
    content TEXT NOT NULL COMMENT '리뷰 내용',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '리뷰 작성 날짜',
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '리뷰 수정 날짜',
    image VARCHAR(255) NULL COMMENT '첨부 사진'
);

CREATE TABLE Employee_Store_Assignments (
    assignment_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '직원-매장 근무 배정 PK',
    
    employee_id BIGINT NOT NULL COMMENT '직원 ID',
    store_id BIGINT NOT NULL COMMENT '매장 ID',

    role ENUM('고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사') NOT NULL COMMENT '배정 역할',

    assigned_at DATE NOT NULL COMMENT '배정 시작일',
    ended_at DATE NULL COMMENT '배정 종료일 (NULL이면 현재 근무 중)',

    status ENUM('근무 중', '전출', '종료', '휴직', '파견') NOT NULL DEFAULT '근무 중' COMMENT '근무 상태',

    notes VARCHAR(255) NULL COMMENT '기타 비고 또는 변경 사유',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록 일시',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 일시',

    CONSTRAINT FK_ESA_Employee FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
    CONSTRAINT FK_ESA_Store FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);

-- 2. 외래키 제약 조건 추가
ALTER TABLE Stores MODIFY open_time TIME;
ALTER TABLE Stores MODIFY close_time TIME;

alter table store_inventory
	drop column location;

ALTER TABLE Store_Inventory
  ADD COLUMN location VARCHAR(255) NULL COMMENT '상품 위치';

ALTER TABLE Warehouse_Inventory
  ADD COLUMN location VARCHAR(255) NULL COMMENT '상품 위치';
  
ALTER TABLE Store_Inventory
	ADD COLUMN expiration_date TIMESTAMP null COMMENT '유통기한';
    
ALTER TABLE Warehouse_Inventory
	ADD COLUMN expiration_date TIMESTAMP null COMMENT '유통기한';
    
ALTER TABLE Employees
  ADD COLUMN birth_date DATE NULL COMMENT '직원 생년월일'; -- 0.094 sec
  
  ALTER TABLE Store_Order_Requests
DROP COLUMN quantity; -- 0.078 sec

ALTER TABLE Store_Order_Requests
ADD COLUMN reason VARCHAR(255) NULL COMMENT '발주 사유'; -- 0.047 sec

ALTER TABLE Store_Order_Requests
ADD COLUMN warehouse_request_id BIGINT NULL COMMENT '연결된 물류센터 발주 요청 ID'; -- 0.047 sec

ALTER TABLE Store_Order_Requests
ADD CONSTRAINT FK_SOR_Warehouse_Request
FOREIGN KEY (warehouse_request_id) REFERENCES Warehouse_Orders_Requests(request_id); -- 3.703 sec

ALTER TABLE Warehouse_Orders_Log
  ADD CONSTRAINT FK_WOL_Request
  FOREIGN KEY (request_id) REFERENCES Warehouse_Orders_Requests(request_id);

ALTER TABLE Delivery_Address
  ADD CONSTRAINT FK_DA_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE Grade
  ADD CONSTRAINT FK_Grade_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE Training_Log
  ADD CONSTRAINT FK_TL_Driver
  FOREIGN KEY (driver_id) REFERENCES Delivery_Driver(driver_id);

ALTER TABLE Store_Order_Logs
  ADD CONSTRAINT FK_SOL_Request
  FOREIGN KEY (request_id) REFERENCES Store_Order_Requests(request_id);

ALTER TABLE Warehouse_Inventory
  ADD CONSTRAINT FK_WI_Warehouse
  FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id);

ALTER TABLE Warehouse_Inventory
  ADD CONSTRAINT FK_WI_Product
  FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Warehouses
  ADD CONSTRAINT FK_Warehouses_Manager
  FOREIGN KEY (manager_id) REFERENCES Employees(employee_id);

ALTER TABLE QnA
  ADD CONSTRAINT FK_QnA_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE QnA
  ADD CONSTRAINT FK_QnA_Employee
  FOREIGN KEY (employee_id) REFERENCES Employees(employee_id);

ALTER TABLE Offline_Cart
  ADD CONSTRAINT FK_Off_Customer
  FOREIGN KEY (c_id) REFERENCES Customer(customer_id);

ALTER TABLE Warehouse_Orders_Details
  ADD CONSTRAINT FK_WOD_Request
  FOREIGN KEY (request_id) REFERENCES Warehouse_Orders_Requests(request_id);

ALTER TABLE Warehouse_Orders_Details
  ADD CONSTRAINT FK_WOD_Product
  FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Online_Cart
  ADD CONSTRAINT FK_ON_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE Store_Order_Details
  ADD CONSTRAINT FK_SOD_Request
  FOREIGN KEY (request_id) REFERENCES Store_Order_Requests(request_id);

ALTER TABLE Store_Order_Details
  ADD CONSTRAINT FK_SOD_Product
  FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Delivery_Review
  ADD CONSTRAINT FK_DR_Delivery
  FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id);

ALTER TABLE Delivery
  ADD CONSTRAINT FK_Delivery_Driver
  FOREIGN KEY (driver_id) REFERENCES Delivery_Driver(driver_id);

ALTER TABLE Delivery
  ADD CONSTRAINT FK_Delivery_Car
  FOREIGN KEY (car_id) REFERENCES Delivery_Car(car_id);

ALTER TABLE Delivery
  ADD CONSTRAINT FK_Delivery_Payment
  FOREIGN KEY (online_payment_id) REFERENCES online_payment(online_payment_id);

ALTER TABLE Delivery_Price
  ADD CONSTRAINT FK_DP_Delivery
  FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id);

ALTER TABLE Review
  ADD CONSTRAINT FK_Review_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE Review
  ADD CONSTRAINT FK_Review_Product
  FOREIGN KEY (product_id) REFERENCES Online_Cart_Product(cart_product_id);

ALTER TABLE Discounts
  ADD CONSTRAINT FK_Discounts_PP
  FOREIGN KEY (price_id) REFERENCES Product_Price(price_id);

ALTER TABLE Product_Price
  ADD CONSTRAINT FK_PP_Product
  FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Delivery_Return
  ADD CONSTRAINT FK_DR_Employee
  FOREIGN KEY (employee_id) REFERENCES Employees(employee_id);

ALTER TABLE Delivery_Return
  ADD CONSTRAINT FK_DR_Return_Delivery
  FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id);

ALTER TABLE online_order
  ADD CONSTRAINT FK_online_order_OnlineCart
  FOREIGN KEY (online_cart_id) REFERENCES Online_Cart(online_cart_id);

ALTER TABLE online_order
  ADD CONSTRAINT FK_online_order_Point
  FOREIGN KEY (point_id) REFERENCES Point(point_id);

ALTER TABLE Store_Order_Requests
  ADD CONSTRAINT FK_SOR_Stores
  FOREIGN KEY (store_id) REFERENCES Stores(store_id);

ALTER TABLE online_payment
  ADD CONSTRAINT FK_online_payment_Order
  FOREIGN KEY (order_id) REFERENCES online_order(order_id);

ALTER TABLE online_payment
  ADD CONSTRAINT FK_online_payment_Card
  FOREIGN KEY (card_id) REFERENCES online_card(card_id);

ALTER TABLE online_payment
  ADD CONSTRAINT FK_online_payment_Cancels
  FOREIGN KEY (cancels_id) REFERENCES online_cancels(cancels_id);

ALTER TABLE online_payment
  ADD CONSTRAINT FK_online_payment_EasyPay
  FOREIGN KEY (easy_pay_id) REFERENCES Online_Easy_Pay(easy_pay_id);

ALTER TABLE offline_cash
  ADD CONSTRAINT FK_offline_cash_Order
  FOREIGN KEY (order_id) REFERENCES Offline_Order(order_id);

ALTER TABLE Delivery_Alarm
  ADD CONSTRAINT FK_DA_Delivery
  FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id);

ALTER TABLE Point
  ADD CONSTRAINT FK_Point_Customer
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id);

ALTER TABLE Delivery_Accident_Log
  ADD CONSTRAINT FK_DAL_Employee
  FOREIGN KEY (employee_id) REFERENCES Employees(employee_id);

ALTER TABLE Delivery_Accident_Log
  ADD CONSTRAINT FK_DAL_Delivery
  FOREIGN KEY (delivery_id) REFERENCES Delivery(delivery_id);

ALTER TABLE Product
  ADD CONSTRAINT FK_Product_Category
  FOREIGN KEY (category_id) REFERENCES Category(category_id);

ALTER TABLE Offline_Order
  ADD CONSTRAINT FK_OfflineOrder_OfflineCart
  FOREIGN KEY (offline_cart_id) REFERENCES Offline_Cart(offline_cart_id);

ALTER TABLE Offline_Order
  ADD CONSTRAINT FK_OfflineOrder_Point
  FOREIGN KEY (point_id) REFERENCES Point(point_id);

ALTER TABLE Store_Inventory
  ADD CONSTRAINT FK_StoreInventory_Stores
  FOREIGN KEY (store_id) REFERENCES Stores(store_id);

ALTER TABLE Store_Inventory
  ADD CONSTRAINT FK_StoreInventory_Product
  FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Delivery_Option
  ADD CONSTRAINT FK_DO_DeliveryPrice
  FOREIGN KEY (price_id) REFERENCES Delivery_Price(price_id);

ALTER TABLE Offline_Cart_Product
  ADD CONSTRAINT FK_OCP_OfflineCart
  FOREIGN KEY (offline_cart_id) REFERENCES Offline_Cart(offline_cart_id);

ALTER TABLE Offline_Cart_Product
  ADD CONSTRAINT FK_OCP_StoreInventory
  FOREIGN KEY (inventory_id) REFERENCES Store_Inventory(inventory_id);

ALTER TABLE Offline_Payment
  ADD CONSTRAINT FK_OP_OfflineOrder
  FOREIGN KEY (order_id) REFERENCES Offline_Order(order_id);

ALTER TABLE Offline_Payment
  ADD CONSTRAINT FK_OP_OfflineCard
  FOREIGN KEY (card_id) REFERENCES Offline_Card(card_id);

ALTER TABLE Offline_Payment
  ADD CONSTRAINT FK_OP_OfflineCancels
  FOREIGN KEY (cancels_id) REFERENCES offline_cancels(cancels_id);

ALTER TABLE Employees
  ADD CONSTRAINT FK_Employees_Stores
  FOREIGN KEY (store_id) REFERENCES Stores(store_id);

ALTER TABLE Employees
  ADD CONSTRAINT FK_Employees_Warehouses
  FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id);

ALTER TABLE Online_Cart_Product
  ADD CONSTRAINT FK_OCP_OnlineCart
  FOREIGN KEY (online_cart_id) REFERENCES Online_Cart(online_cart_id);

ALTER TABLE Online_Cart_Product
  ADD CONSTRAINT FK_OCP_WarehouseInventory
  FOREIGN KEY (inventory_id) REFERENCES Warehouse_Inventory(inventory_id);

ALTER TABLE Stores
  ADD CONSTRAINT FK_Stores_Manager
  FOREIGN KEY (manager_id) REFERENCES Employees(employee_id);

ALTER TABLE Delivery_Driver
  ADD CONSTRAINT FK_Driver_Employee
  FOREIGN KEY (employee_id) REFERENCES Employees(employee_id);

ALTER TABLE Warehouse_Orders_Requests
  ADD CONSTRAINT FK_WOR_Warehouses
  FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id);


ALTER TABLE `online_card`
MODIFY COLUMN `issuer_code` VARCHAR(2) NOT NULL COMMENT '카드 발급사 코드',
MODIFY COLUMN `acquirer_code` VARCHAR(2) NOT NULL COMMENT '카드 매입사 코드';


  
