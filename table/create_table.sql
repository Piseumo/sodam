use sodam;

CREATE TABLE `Warehouse_Orders_Log` (
    `log_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `request_id` BIGINT NOT NULL,
    `status` ENUM('요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소') NOT NULL COMMENT '상태',
    `changed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Delivery_Address` (
    `address_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `city` VARCHAR(255) NOT NULL COMMENT '시',
    `district` VARCHAR(255) NOT NULL COMMENT '구',
    `address` VARCHAR(255) NOT NULL COMMENT '주소',
    `address2` VARCHAR(255) NOT NULL COMMENT '상세 주소',
    `postal_code` VARCHAR(10) NOT NULL COMMENT '우편번호',
    `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Grade` (
    `grade_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `name` ENUM('Normal', 'VIP', 'VVIP', 'SVIP') NOT NULL COMMENT '등급',
    `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `accumulated_amount` BIGINT NOT NULL COMMENT '총 누적 결제 금액',
    `reason` VARCHAR(255) NULL COMMENT '변경 사유'
);

CREATE TABLE `Training_Log` (
    `training_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `driver_id` BIGINT NOT NULL,
    `complete_date` DATE NOT NULL
);

CREATE TABLE `Store_Order_Logs` (
    `log_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `request_id` BIGINT NOT NULL,
    `status` ENUM('요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소') NOT NULL COMMENT '상태',
    `changed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '변동 일자'
);

CREATE TABLE `Warehouse_Inventory` (
    `inventory_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `warehouse_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL,
    `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Delivery_Car` (
    `car_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `number` VARCHAR(255) NOT NULL COMMENT '차량번호(1t 탑차로 통일)',
    `status` ENUM('배송가능', '수리중', '배송중', '고장') NOT NULL COMMENT '차량 상태',
    `insert_date` DATE NOT NULL COMMENT '차량 입고일',
    `last_activity_date` DATE NULL COMMENT '마지막 활동일',
    `insurance` BOOLEAN NOT NULL COMMENT '차량보험'
);

CREATE TABLE `Warehouses` (
    `warehouse_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT '물류센터 이름',
    `contact_number` VARCHAR(255) NOT NULL COMMENT '물류센터 전화번호',
    `address` TEXT NOT NULL COMMENT '물류센터 주소',
    `manager_id` BIGINT NOT NULL COMMENT '물류센터 관리자',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜',
    `registration_number` VARCHAR(255) NOT NULL UNIQUE COMMENT '사업자 등록번호',
    `industry_type` ENUM('물류') NOT NULL COMMENT '산업 유형'
);

CREATE TABLE `QnA` (
    `qna_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `inquiry_content` TEXT NOT NULL COMMENT '문의 내용',
    `image` VARCHAR(255) NULL COMMENT '첨부 사진',
    `inquiry_time` DATETIME NOT NULL COMMENT '문의 시간',
    `status` ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending' COMMENT '답변 상태',
    `employee_id` BIGINT NULL COMMENT '답변한 직원',
    `answer_time` DATETIME NULL COMMENT '답변 시간',
    `answer_content` TEXT NULL COMMENT '답변 내용'
);

CREATE TABLE `Offline_Cart` (
    `offline_cart_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `c_id` BIGINT NOT NULL,
    `total_price` INT NOT NULL
);


CREATE TABLE `Warehouse_Orders_Details` (
    `detail_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `request_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Online_Cart` (
    `online_cart_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `total_price` INT NOT NULL
);

CREATE TABLE `Store_Order_Details` (
    `detail_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `request_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL COMMENT '상품 수량',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 일자'
);

CREATE TABLE `Delivery_Review` (
    `review_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `point` INT NULL COMMENT '리뷰점수',
    `content` VARCHAR(255) NULL COMMENT '리뷰내용',
    `insert_date` DATE NOT NULL COMMENT '등록날짜',
    `update_date` DATE NULL COMMENT '수정날짜',
    `delete_date` DATE NULL COMMENT '삭제날짜',
    `delivery_id` BIGINT NOT NULL
);

CREATE TABLE `Delivery` (
    `delivery_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `driver_id` BIGINT NOT NULL,
    `car_id` BIGINT NOT NULL,
    `online_payment_id` BIGINT NOT NULL,
    `status` ENUM('배송준비', '배송중', '배송완료', '배송중사고') NOT NULL COMMENT '배송 상태',
    `start_date` DATETIME NULL COMMENT '배송출발일',
    `end_date` DATE NULL COMMENT '배송완료일',
    `request_type` ENUM('물류센터', '고객') NOT NULL COMMENT '요청 유형'
);

CREATE TABLE `Delivery_Price` (
    `price_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `delivery_id` BIGINT NOT NULL,
    `price` INT NOT NULL COMMENT '배송비용',
    `option_type` ENUM('일반배송', '새벽배송', '예약배송') NOT NULL COMMENT '배송 옵션',
    `weight` DOUBLE NOT NULL COMMENT '무게 단위(kg)'
);

CREATE TABLE `Offline_Card` (
    `card_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `card_code` VARCHAR(3) NOT NULL COMMENT '신용카드사별 코드',
    `card_name` VARCHAR(20) NOT NULL COMMENT '결제 카드사 이름 예) 비씨',
    `card_num` VARCHAR(20) NULL COMMENT '카드번호 앞 6자 마지막 4자를 제외한 가운데 숫자 마스킹 처리됨 예) 536112******1234',
    `card_quota` VARCHAR(3) NOT NULL COMMENT '할부개월 0:일시불, 2:2개월, 3:3개월 …',
    `is_interest_free` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '상점분담무이자 여부 true:무이자, false:일반',
    `card_type` VARCHAR(10) NULL COMMENT '카드 구분 credit:신용, check:체크',
    `can_part_cancel` TINYINT(1) NOT NULL COMMENT '부분취소 가능 여부 true:가능, false:불가능',
    `acqu_card_code` VARCHAR(3) NOT NULL COMMENT '매입카드사코드',
    `acqu_card_name` VARCHAR(100) NOT NULL COMMENT '매입카드사명'
);

CREATE TABLE `Discounts` (
    `discounts_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `rate` INT NULL COMMENT '할인율',
    `reason` VARCHAR(255) NULL COMMENT '할인 사유',
    `start` DATETIME NULL COMMENT '할인 시작 날짜',
    `end` DATETIME NULL COMMENT '할인 종료 날짜',
    `price_id` BIGINT NOT NULL
);

CREATE TABLE `Product_Price` (
    `price_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `product_id` BIGINT NOT NULL,
    `current_price` INT NULL COMMENT '원래 가격',
    `type` ENUM('Increase', 'Decrease') NULL COMMENT '증감 타입',
    `delta` INT NULL COMMENT '증감 가격',
    `reason` VARCHAR(255) NULL COMMENT '가격 변동 사유',
    `final_price` INT NOT NULL COMMENT '최종 가격',
    `date_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Delivery_Return` (
    `return_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `status` ENUM('파손', '잘못배송', '수량부족', '상태불량') NOT NULL COMMENT '반품 상태',
    `application_date` DATE NOT NULL COMMENT '신청일',
    `drop_date` DATE NULL COMMENT '배송기사 반송품 회수일',
    `return_date` DATE NULL COMMENT '반송품 도착일(물류센터 도착일)',
    `return_complete_date` DATE NULL COMMENT '반송 최종 완료일 (ex: 환불금 고객 지급까지)',
    `status_check` ENUM('검사대기', '검사완료') NOT NULL COMMENT '검사 상태',
    `employee_id` BIGINT NOT NULL,
    `return_types` ENUM('재배송', '환불', '교환') NULL COMMENT '반품 유형',
    `delivery_id` BIGINT NOT NULL
);


CREATE TABLE `offline_cancels` (
    `cancels_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `tid` VARCHAR(30) NOT NULL COMMENT '승인 취소 거래번호',
    `amount` INT NOT NULL COMMENT '취소금액',
    `cancelled_at` DATETIME NOT NULL COMMENT '취소된 시각 ISO 8601',
    `reason` VARCHAR(100) NOT NULL COMMENT '취소 사유',
    `receipt_url` VARCHAR(200) NOT NULL COMMENT '취소에 대한 매출전표 확인 URL',
    `coupon_amt` INT NULL COMMENT '쿠폰 취소 금액'
);

CREATE TABLE `online_order` (
    `order_id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `online_cart_id` BIGINT NOT NULL,
    `point_id` BIGINT NOT NULL AUTO_INCREMENT,
    `receiver_name` VARCHAR(255) NULL,
    `receiver_address` VARCHAR(255) NOT NULL,
    `status` ENUM('주문 접수', '결제 완료', '배송 준비 중', '배송 중', '배송 완료', '주문 취소') NOT NULL
);

CREATE TABLE `online_card` (
    `card_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `amount` INT NOT NULL COMMENT '결제 요청 금액',
    `issuer_code` INT NOT NULL COMMENT '카드 발급사 코드',
    `acquirer_code` INT NOT NULL COMMENT '카드 매입사 코드',
    `number` VARCHAR(255) NOT NULL COMMENT '카드번호 마스킹',
    `installment_plan_months` INT NOT NULL DEFAULT 0 COMMENT '할부 개월 수',
    `approve_no` VARCHAR(8) NOT NULL COMMENT '카드사 승인 번호',
    `use_card_point` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '카드사 포인트 사용 여부',
    `card_type` VARCHAR(20) NOT NULL COMMENT '카드 종류',
    `owner_type` VARCHAR(20) NOT NULL COMMENT '카드 소유자 종류',
    `acquire_status` ENUM('READY', 'REQUESTED', 'COMPLETED', 'CANCEL_REQUEST', 'CANCELED') NOT NULL COMMENT '매입 상태',
    `is_interested_free` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '무이자 할부 적용 여부'
);

CREATE TABLE `Store_Order_Requests` (
    `request_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `store_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL COMMENT '요청 수량',
    `status` ENUM('요청', '승인', '출고 중', '출고 완료', '배송 중', '입고 완료', '취소') NOT NULL COMMENT '상태',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 일자',
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 일자'
);

CREATE TABLE `online_payment` (
    `online_payment_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `mid` VARCHAR(255) NOT NULL DEFAULT 'tosspayments',
    `last_transaction_key` VARCHAR(64) NOT NULL COMMENT '최초 결제 승인 키',
    `payment_key` VARCHAR(200) NOT NULL COMMENT 'unique',
    `order_id` VARCHAR(64) NOT NULL,
    `order_name` VARCHAR(255) NOT NULL COMMENT '상품명 외 2개',
    `tax_exemption_amount` INT NOT NULL DEFAULT 0 COMMENT '과세 제외 금액',
    `status` ENUM('READY', 'IN_PROGRESS', 'WAITING_FOR_DEPOSIT', 'DONE', 'CANCELED', 'PARTIAL_CANCELED', 'ABORTED', 'EXPIRED') NOT NULL COMMENT '결제 상태',
    `requested_at` DATETIME NOT NULL COMMENT '결제 요청 시간',
    `approved_at` DATETIME NULL COMMENT '결제 승인 시간',
    `use_escrow` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '에스크로 여부',
    `total_amount` INT NOT NULL COMMENT '총 결제 금액',
    `balance_amount` INT NOT NULL COMMENT '취소 가능 금액',
    `method` VARCHAR(20) NOT NULL COMMENT '결제 방식',
    `currency` VARCHAR(5) NOT NULL COMMENT '통화'
);

CREATE TABLE `offline_cash` (
    `offline_cash_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `order_id` VARCHAR(64) NOT NULL,
    `amount` INT NOT NULL COMMENT '결제 금액',
    `currency` VARCHAR(3) NOT NULL DEFAULT 'KRW' COMMENT '사용 통화',
    `pay_date` DATETIME NOT NULL COMMENT '결제 시간',
    `status` ENUM('PENDING', 'COMPLETE', 'CANCELED') NOT NULL COMMENT '결제 상태',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '결제 생성 시간',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 시간',
    `cash_receipt_request_num` VARCHAR(50) NULL COMMENT '현금 영수증 요청 번호',
    `cash_receipt_approval_num` VARCHAR(50) NULL COMMENT '현금 영수증 승인 번호'
);

CREATE TABLE `online_cancels` (
    `cancels_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `transaction_key` VARCHAR(64) NOT NULL COMMENT '취소 건 키 값',
    `cancel_reason` VARCHAR(255) NOT NULL COMMENT '취소 이유',
    `tax_exemption_amount` INT NOT NULL DEFAULT 0 COMMENT '과세 제외 금액',
    `canceled_at` DATETIME NOT NULL COMMENT '결제 취소 시간',
    `cancel_amount` INT NOT NULL COMMENT '취소 금액',
    `cancel_status` ENUM('DONE', 'IN_PROGRESS', 'ABORTED') NOT NULL COMMENT '취소 상태'
);

CREATE TABLE `Delivery_Alarm` (
    `alarm_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `delivery_id` BIGINT NOT NULL,
    `text` TEXT NULL COMMENT '알람 내용',
    `send_date` DATE NOT NULL COMMENT '알람 송신 날짜'
);

CREATE TABLE `Customer` (
    `customer_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT '고객명',
    `email` VARCHAR(255) NOT NULL COMMENT '고객 이메일',
    `phone` VARCHAR(255) NOT NULL COMMENT '휴대폰 번호',
    `password` VARCHAR(255) NULL COMMENT '비밀번호',
    `login_type` ENUM('Form', 'Kakao', 'Google') NOT NULL COMMENT '로그인 타입'
);

CREATE TABLE `Delivery_Accident_Log` (
    `accident_log_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `employee_id` BIGINT NOT NULL,
    `delivery_id` BIGINT NOT NULL,
    `log_types` ENUM('차량사고', '배송품파손', '운전기사이상', '기상이변', '도로정체') NOT NULL COMMENT '사고 유형',
    `text` TEXT NULL COMMENT '사고 내용',
    `status` ENUM('사고접수', '처리중', '처리완료') NOT NULL COMMENT '사고 처리 상태',
    `accident_date` DATE NULL COMMENT '사고 발생일',
    `report_date` DATE NOT NULL COMMENT '사고 등록일',
    `complete_date` DATE NULL COMMENT '처리 완료일'
);

CREATE TABLE `Product` (
    `product_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `category_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL COMMENT '상품명',
    `option_detail` VARCHAR(255) NULL COMMENT '상품 옵션',
    `main_image` VARCHAR(255) NOT NULL COMMENT '메인 이미지',
    `detail_image` VARCHAR(255) NOT NULL COMMENT '상세 이미지',
    `expire_date` DATETIME NULL COMMENT '유효기간',
    `capacity_value` INT NULL COMMENT '상품용량 값',
    `capacity_unit` VARCHAR(20) NULL COMMENT '상품용량 단위'
);

CREATE TABLE `Offline_Order` (
    `order_id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `offline_cart_id` BIGINT NOT NULL,
    `point_id` BIGINT NOT NULL AUTO_INCREMENT,
    `pay_method` ENUM('카드 결제', '현금 결제') NOT NULL COMMENT '결제 방식',
    `status` ENUM('결제 대기', '결제 완료') NOT NULL COMMENT '결제 상태'
);

CREATE TABLE `Store_Inventory` (
    `inventory_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `store_id` BIGINT NOT NULL,
    `product_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL COMMENT '재고 수량',
    `last_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `Delivery_Option` (
    `option_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `price_id` BIGINT NOT NULL,
    `request_datetime` DATE NULL COMMENT '요청 일시'
);

CREATE TABLE `Offline_Cart_Product` (
    `cart_product_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `offline_cart_id` BIGINT NOT NULL,
    `inventory_id` BIGINT NOT NULL,
    `quantity` TINYINT NOT NULL,
    `price` INT NOT NULL
);

CREATE TABLE `Category` (
    `category_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `main` VARCHAR(255) NOT NULL COMMENT '대분류',
    `sub` VARCHAR(255) NOT NULL COMMENT '중분류',
    `detail` VARCHAR(255) NOT NULL COMMENT '소분류'
);

CREATE TABLE `Offline_Payment` (
    `offline_payment_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '오프라인 결제 ID',
    `result_code` VARCHAR(4) NOT NULL COMMENT '0000 - 성공, 그 외 실패',
    `result_message` VARCHAR(100) NOT NULL COMMENT '결과 메시지',
    `tid` VARCHAR(30) NOT NULL COMMENT '결제 승인 키',
    `cancelled_tid` VARCHAR(30) NULL COMMENT '취소 거래 키',
    `order_id` VARCHAR(64) NOT NULL,
    `edi_date` DATETIME NULL COMMENT '응답 전문 생성 일시',
    `signature` VARCHAR(256) NULL COMMENT '위변조 검증 데이터',
    `status` ENUM('paid', 'ready', 'failed', 'cancelled', 'partialCancelled', 'expired') NOT NULL COMMENT '결제 상태',
    `paid_at` DATETIME NOT NULL COMMENT '결제 완료 시점',
    `failed_at` DATETIME NOT NULL COMMENT '결제 실패 시점',
    `cancelled_at` DATETIME NOT NULL COMMENT '결제 취소 시점',
    `pay_method` ENUM('card', 'vbank', 'naverpay', 'kakaopay', 'payco', 'ssgpay', 'samsungpay') NOT NULL COMMENT '결제 수단',
    `amount` INT NOT NULL COMMENT '결제 금액',
    `balance_amt` INT NOT NULL COMMENT '취소 가능 잔액',
    `goods_name` VARCHAR(40) NOT NULL COMMENT '상품명',
    `mall_reserved` VARCHAR(500) NULL COMMENT '상점 정보 전달용 필드',
    `use_escrow` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '에스크로 거래 여부',
    `currency` VARCHAR(3) NOT NULL DEFAULT 'KRW' COMMENT '결제 승인 화폐 단위',
    `channel` ENUM('pc', 'mobile') NULL COMMENT '결제 채널',
    `approve_no` VARCHAR(30) NULL COMMENT '제휴사 승인 번호',
    `buyer_name` VARCHAR(30) NULL COMMENT '구매자 명',
    `buyer_tel` VARCHAR(40) NULL COMMENT '구매자 전화번호',
    `buyer_email` VARCHAR(60) NULL COMMENT '구매자 이메일',
    `issued_cash_receipt` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '현금 영수증 발급 여부',
    `receipt_url` VARCHAR(200) NULL COMMENT '매출전표 확인 URL'
);

CREATE TABLE `Employees` (
    `employee_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT '직원 이름',
    `phone` VARCHAR(255) NOT NULL COMMENT '직원 휴대폰번호',
    `email` VARCHAR(255) NULL COMMENT '직원 이메일',
    `store_id` BIGINT NULL COMMENT '매장 직원',
    `warehouse_id` BIGINT NULL COMMENT '물류센터 직원',
    `role` ENUM('고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사'),
    `hire_date` DATE NOT NULL COMMENT '고용 날짜',
    `salary` DECIMAL(10, 2) NOT NULL COMMENT '급여',
    `location_type` ENUM('매장', '물류센터') NOT NULL COMMENT '근무 장소',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜',
    `insurance` BOOLEAN NOT NULL COMMENT '보험 가입 여부'
);

CREATE TABLE `Online_Cart_Product` (
    `product_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `online_cart_id` BIGINT NOT NULL,
    `inventory_id` BIGINT NOT NULL,
    `quantity` TINYINT NOT NULL,
    `price` INT NOT NULL
);

CREATE TABLE `Stores` (
    `store_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT '매장 이름',
    `contact_number` VARCHAR(255) NOT NULL COMMENT '매장 전화번호',
    `open_time` DATETIME NOT NULL COMMENT '개장 시간',
    `close_time` DATETIME NOT NULL COMMENT '폐장 시간',
    `address` TEXT NOT NULL COMMENT '매장 주소',
    `status` ENUM('운영', '휴점', '폐점') NOT NULL DEFAULT '운영' COMMENT '매장 운영 상태',
    `manager_id` BIGINT NOT NULL COMMENT '매장 관리자',
    `registration_number` VARCHAR(255) NOT NULL UNIQUE COMMENT '사업자 등록번호',
    `industry_type` ENUM('소매업') NOT NULL DEFAULT '소매업' COMMENT '업종',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'DB 입력 날짜',
    `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정 날짜'
);

CREATE TABLE `Delivery_Driver` (
    `driver_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `employee_id` BIGINT NOT NULL,
    `status` ENUM('근무가능', '병가', '휴가', '배송중사고', '배송중') NOT NULL COMMENT '근무 상태',
    `training_check` BOOLEAN NOT NULL COMMENT '교육훈련 유무',
    `insurance` BOOLEAN NOT NULL COMMENT '보험가입 유무',
    `zone` ENUM('서구', '동구', '남구', '달서구', '북구', '수성구', '중구') NOT NULL COMMENT '근무 지역'
);

CREATE TABLE `Warehouse_Orders_Requests` (
    `request_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `warehouse_id` BIGINT NOT NULL,
    `type` ENUM('입고', '출고') NOT NULL COMMENT '요청 유형',
    `source` ENUM('매장발주', '공급처발주', '온라인주문') NOT NULL COMMENT '발주 출처',
    `status` ENUM('요청', '승인', '입고 준비 중', '입고 완료', '출고 준비 중', '출고 완료', '배송 중', '취소') NOT NULL COMMENT '상태',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '요청 생성 날짜',
    `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '요청 수정 날짜'
);

CREATE TABLE `Online_Easy_Pay` (
    `easy_pay_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `provider` VARCHAR(255) NOT NULL COMMENT '선택한 간편결제사 코드',
    `amount` INT NOT NULL COMMENT '간편결제로 결제한 금액',
    `discount_amount` INT NULL COMMENT '간편결제 서비스의 포인트로 할인된 금액'
);

CREATE TABLE `Point` (
    `point_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `total_amount` INT NULL COMMENT '결제 금액',
    `type` ENUM('Earned', 'Used', 'Expired') NOT NULL COMMENT '포인트 유형',
    `delta` INT NOT NULL COMMENT '포인트 증감량',
    `total_points` INT NOT NULL COMMENT '총 포인트',
    `date_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '포인트 적립/차감 시간'
);

CREATE TABLE `Review` (
    `review_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL COMMENT '리뷰 작성자',
    `product_id` BIGINT NOT NULL COMMENT '리뷰 상품',
    `star` TINYINT NOT NULL DEFAULT 1 COMMENT '별점 (1~5)',
    `content` TEXT NOT NULL COMMENT '리뷰 내용',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '리뷰 작성 날짜',
    `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '리뷰 수정 날짜',
    `image` VARCHAR(255) NULL COMMENT '첨부 사진'
);


ALTER TABLE `Warehouse_Orders_Log` ADD CONSTRAINT `PK_WAREHOUSE_ORDERS_LOG` PRIMARY KEY (
	`log_id`
);

ALTER TABLE `Delivery address` ADD CONSTRAINT `PK_DELIVERY ADDRESS` PRIMARY KEY (
	`address_id`
);

ALTER TABLE `Grade` ADD CONSTRAINT `PK_GRADE` PRIMARY KEY (
	`grade_id`
);

ALTER TABLE `training log` ADD CONSTRAINT `PK_TRAINING LOG` PRIMARY KEY (
	`training_id`
);

ALTER TABLE `Store_Order_Logs` ADD CONSTRAINT `PK_STORE_ORDER_LOGS` PRIMARY KEY (
	`log_id`
);

ALTER TABLE `Warehouse_Inventory` ADD CONSTRAINT `PK_WAREHOUSE_INVENTORY` PRIMARY KEY (
	`inventory_id`
);

ALTER TABLE `Delivery Car` ADD CONSTRAINT `PK_DELIVERY CAR` PRIMARY KEY (
	`car_id`
);

ALTER TABLE `Warehouses` ADD CONSTRAINT `PK_WAREHOUSES` PRIMARY KEY (
	`warehouse_id`
);

ALTER TABLE `QnA` ADD CONSTRAINT `PK_QNA` PRIMARY KEY (
	`qna_id`
);

ALTER TABLE `offline_cart` ADD CONSTRAINT `PK_OFFLINE_CART` PRIMARY KEY (
	`offline_cart_id`
);

ALTER TABLE `Warehouse_Orders_Details` ADD CONSTRAINT `PK_WAREHOUSE_ORDERS_DETAILS` PRIMARY KEY (
	`detail_id`
);

ALTER TABLE `online_cart` ADD CONSTRAINT `PK_ONLINE_CART` PRIMARY KEY (
	`online_cart_id`
);

ALTER TABLE `Store_Order_Details` ADD CONSTRAINT `PK_STORE_ORDER_DETAILS` PRIMARY KEY (
	`detail_id`
);

ALTER TABLE `Delivery  review` ADD CONSTRAINT `PK_DELIVERY  REVIEW` PRIMARY KEY (
	`review_id`
);

ALTER TABLE `Delivery` ADD CONSTRAINT `PK_DELIVERY` PRIMARY KEY (
	`delivery_ id`
);

ALTER TABLE `Delivery price` ADD CONSTRAINT `PK_DELIVERY PRICE` PRIMARY KEY (
	`price_id`
);

ALTER TABLE `offline_card` ADD CONSTRAINT `PK_OFFLINE_CARD` PRIMARY KEY (
	`card_id`
);

ALTER TABLE `Discounts` ADD CONSTRAINT `PK_DISCOUNTS` PRIMARY KEY (
	`discounts_id`
);

ALTER TABLE `Product Price` ADD CONSTRAINT `PK_PRODUCT PRICE` PRIMARY KEY (
	`price_id`
);

ALTER TABLE `Delivery return` ADD CONSTRAINT `PK_DELIVERY RETURN` PRIMARY KEY (
	`return_id`
);

ALTER TABLE `offline_cancels` ADD CONSTRAINT `PK_OFFLINE_CANCELS` PRIMARY KEY (
	`cancels_id`
);

ALTER TABLE `online_order` ADD CONSTRAINT `PK_ONLINE_ORDER` PRIMARY KEY (
	`order_id`
);

ALTER TABLE `online_card` ADD CONSTRAINT `PK_ONLINE_CARD` PRIMARY KEY (
	`card_id`
);

ALTER TABLE `Store_Order_Requests` ADD CONSTRAINT `PK_STORE_ORDER_REQUESTS` PRIMARY KEY (
	`request_id`
);

ALTER TABLE `online_payment` ADD CONSTRAINT `PK_ONLINE_PAYMENT` PRIMARY KEY (
	`online_payment_id`
);

ALTER TABLE `offline_cash` ADD CONSTRAINT `PK_OFFLINE_CASH` PRIMARY KEY (
	`offline_cash_id`
);

ALTER TABLE `online_cancels` ADD CONSTRAINT `PK_ONLINE_CANCELS` PRIMARY KEY (
	`cancels_id`
);

ALTER TABLE `Delivery alarm` ADD CONSTRAINT `PK_DELIVERY ALARM` PRIMARY KEY (
	`alarm_id`
);

ALTER TABLE `Customer` ADD CONSTRAINT `PK_CUSTOMER` PRIMARY KEY (
	`customer_id`
);

ALTER TABLE `Delivery accident log` ADD CONSTRAINT `PK_DELIVERY ACCIDENT LOG` PRIMARY KEY (
	`accident_log_id`
);

ALTER TABLE `Product` ADD CONSTRAINT `PK_PRODUCT` PRIMARY KEY (
	`product_id`
);

ALTER TABLE `offline_order` ADD CONSTRAINT `PK_OFFLINE_ORDER` PRIMARY KEY (
	`order_id`
);

ALTER TABLE `Store_Inventory` ADD CONSTRAINT `PK_STORE_INVENTORY` PRIMARY KEY (
	`inventory_id`
);

ALTER TABLE `Delivery option` ADD CONSTRAINT `PK_DELIVERY OPTION` PRIMARY KEY (
	`option_id`
);

ALTER TABLE `offline_cart_product` ADD CONSTRAINT `PK_OFFLINE_CART_PRODUCT` PRIMARY KEY (
	`cart_product_id`
);

ALTER TABLE `Category` ADD CONSTRAINT `PK_CATEGORY` PRIMARY KEY (
	`category_id`
);

ALTER TABLE `offline_payment` ADD CONSTRAINT `PK_OFFLINE_PAYMENT` PRIMARY KEY (
	`offline_payment_id`
);

ALTER TABLE `Employees` ADD CONSTRAINT `PK_EMPLOYEES` PRIMARY KEY (
	`employee_id`
);

ALTER TABLE `online_cart_product` ADD CONSTRAINT `PK_ONLINE_CART_PRODUCT` PRIMARY KEY (
	`product_id`
);

ALTER TABLE `매장` ADD CONSTRAINT `PK_매장` PRIMARY KEY (
	`store_id`
);

ALTER TABLE `Delivery driver` ADD CONSTRAINT `PK_DELIVERY DRIVER` PRIMARY KEY (
	`driver_Id`
);

ALTER TABLE `Warehouse_Orders_Requests` ADD CONSTRAINT `PK_WAREHOUSE_ORDERS_REQUESTS` PRIMARY KEY (
	`request_id`
);

ALTER TABLE `online_easy_pay` ADD CONSTRAINT `PK_ONLINE_EASY_PAY` PRIMARY KEY (
	`easy_pay_id`
);

ALTER TABLE `Point` ADD CONSTRAINT `PK_POINT` PRIMARY KEY (
	`point_id`
);

ALTER TABLE `Review` ADD CONSTRAINT `PK_REVIEW` PRIMARY KEY (
	`review_id`
);

ALTER TABLE `Warehouse_Orders_Log` ADD CONSTRAINT `FK_Warehouse_Orders_Requests_TO_Warehouse_Orders_Log_1` FOREIGN KEY (
	`request_id`
)
REFERENCES `Warehouse_Orders_Requests` (
	`request_id`
);

ALTER TABLE `Delivery address` ADD CONSTRAINT `FK_Customer_TO_Delivery address_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `Grade` ADD CONSTRAINT `FK_Customer_TO_Grade_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `training log` ADD CONSTRAINT `FK_Delivery driver_TO_training log_1` FOREIGN KEY (
	`driver_Id`
)
REFERENCES `Delivery driver` (
	`driver_Id`
);

ALTER TABLE `Store_Order_Logs` ADD CONSTRAINT `FK_Store_Order_Requests_TO_Store_Order_Logs_1` FOREIGN KEY (
	`request_id`
)
REFERENCES `Store_Order_Requests` (
	`request_id`
);

ALTER TABLE `Warehouse_Inventory` ADD CONSTRAINT `FK_Warehouses_TO_Warehouse_Inventory_1` FOREIGN KEY (
	`warehouse_id`
)
REFERENCES `Warehouses` (
	`warehouse_id`
);

ALTER TABLE `Warehouse_Inventory` ADD CONSTRAINT `FK_Product_TO_Warehouse_Inventory_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `Product` (
	`product_id`
);

ALTER TABLE `Warehouses` ADD CONSTRAINT `FK_Employees_TO_Warehouses_1` FOREIGN KEY (
	`manager_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `QnA` ADD CONSTRAINT `FK_Customer_TO_QnA_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `QnA` ADD CONSTRAINT `FK_Employees_TO_QnA_1` FOREIGN KEY (
	`employee_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `offline_cart` ADD CONSTRAINT `FK_Customer_TO_offline_cart_1` FOREIGN KEY (
	`c_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `Warehouse_Orders_Details` ADD CONSTRAINT `FK_Warehouse_Orders_Requests_TO_Warehouse_Orders_Details_1` FOREIGN KEY (
	`request_id`
)
REFERENCES `Warehouse_Orders_Requests` (
	`request_id`
);

ALTER TABLE `Warehouse_Orders_Details` ADD CONSTRAINT `FK_Product_TO_Warehouse_Orders_Details_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `Product` (
	`product_id`
);

ALTER TABLE `online_cart` ADD CONSTRAINT `FK_Customer_TO_online_cart_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `Store_Order_Details` ADD CONSTRAINT `FK_Store_Order_Requests_TO_Store_Order_Details_1` FOREIGN KEY (
	`request_id`
)
REFERENCES `Store_Order_Requests` (
	`request_id`
);

ALTER TABLE `Store_Order_Details` ADD CONSTRAINT `FK_Product_TO_Store_Order_Details_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `Product` (
	`product_id`
);

ALTER TABLE `Delivery  review` ADD CONSTRAINT `FK_Delivery_TO_Delivery  review_1` FOREIGN KEY (
	`delivery_ id`
)
REFERENCES `Delivery` (
	`delivery_ id`
);

ALTER TABLE `Delivery` ADD CONSTRAINT `FK_Delivery driver_TO_Delivery_1` FOREIGN KEY (
	`driver_Id`
)
REFERENCES `Delivery driver` (
	`driver_Id`
);

ALTER TABLE `Delivery` ADD CONSTRAINT `FK_Delivery Car_TO_Delivery_1` FOREIGN KEY (
	`car_id`
)
REFERENCES `Delivery Car` (
	`car_id`
);

ALTER TABLE `Delivery` ADD CONSTRAINT `FK_online_payment_TO_Delivery_1` FOREIGN KEY (
	`online_payment_id`
)
REFERENCES `online_payment` (
	`online_payment_id`
);

ALTER TABLE `Delivery price` ADD CONSTRAINT `FK_Delivery_TO_Delivery price_1` FOREIGN KEY (
	`Delivery_ id`
)
REFERENCES `Delivery` (
	`delivery_ id`
);

ALTER TABLE `Discounts` ADD CONSTRAINT `FK_Product Price_TO_Discounts_1` FOREIGN KEY (
	`price_id`
)
REFERENCES `Product Price` (
	`price_id`
);

ALTER TABLE `Product Price` ADD CONSTRAINT `FK_Product_TO_Product Price_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `Product` (
	`product_id`
);

ALTER TABLE `Delivery return` ADD CONSTRAINT `FK_Employees_TO_Delivery return_1` FOREIGN KEY (
	`employee_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `Delivery return` ADD CONSTRAINT `FK_Delivery_TO_Delivery return_1` FOREIGN KEY (
	`delivery_ id`
)
REFERENCES `Delivery` (
	`delivery_ id`
);

ALTER TABLE `online_order` ADD CONSTRAINT `FK_online_cart_TO_online_order_1` FOREIGN KEY (
	`online_cart_id`
)
REFERENCES `online_cart` (
	`online_cart_id`
);

ALTER TABLE `online_order` ADD CONSTRAINT `FK_Point_TO_online_order_1` FOREIGN KEY (
	`point_id`
)
REFERENCES `Point` (
	`point_id`
);

ALTER TABLE `Store_Order_Requests` ADD CONSTRAINT `FK_매장_TO_Store_Order_Requests_1` FOREIGN KEY (
	`store_id`
)
REFERENCES `매장` (
	`store_id`
);

ALTER TABLE `online_payment` ADD CONSTRAINT `FK_online_order_TO_online_payment_1` FOREIGN KEY (
	`order_id`
)
REFERENCES `online_order` (
	`order_id`
);

ALTER TABLE `online_payment` ADD CONSTRAINT `FK_online_card_TO_online_payment_1` FOREIGN KEY (
	`card_id`
)
REFERENCES `online_card` (
	`card_id`
);

ALTER TABLE `online_payment` ADD CONSTRAINT `FK_online_cancels_TO_online_payment_1` FOREIGN KEY (
	`cancels_id`
)
REFERENCES `online_cancels` (
	`cancels_id`
);

ALTER TABLE `online_payment` ADD CONSTRAINT `FK_online_easy_pay_TO_online_payment_1` FOREIGN KEY (
	`easy_pay_id`
)
REFERENCES `online_easy_pay` (
	`easy_pay_id`
);

ALTER TABLE `offline_cash` ADD CONSTRAINT `FK_offline_order_TO_offline_cash_1` FOREIGN KEY (
	`order_id`
)
REFERENCES `offline_order` (
	`order_id`
);

ALTER TABLE `Delivery alarm` ADD CONSTRAINT `FK_Delivery_TO_Delivery alarm_1` FOREIGN KEY (
	`delivery_id`
)
REFERENCES `Delivery` (
	`delivery_ id`
);

ALTER TABLE `Delivery accident log` ADD CONSTRAINT `FK_Employees_TO_Delivery accident log_1` FOREIGN KEY (
	`employee_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `Delivery accident log` ADD CONSTRAINT `FK_Delivery_TO_Delivery accident log_1` FOREIGN KEY (
	`Delivery_ id`
)
REFERENCES `Delivery` (
	`delivery_ id`
);

ALTER TABLE `Product` ADD CONSTRAINT `FK_Category_TO_Product_1` FOREIGN KEY (
	`category_id`
)
REFERENCES `Category` (
	`category_id`
);

ALTER TABLE `offline_order` ADD CONSTRAINT `FK_offline_cart_TO_offline_order_1` FOREIGN KEY (
	`offline_cart_id`
)
REFERENCES `offline_cart` (
	`offline_cart_id`
);

ALTER TABLE `offline_order` ADD CONSTRAINT `FK_Point_TO_offline_order_1` FOREIGN KEY (
	`point_id`
)
REFERENCES `Point` (
	`point_id`
);

ALTER TABLE `Store_Inventory` ADD CONSTRAINT `FK_매장_TO_Store_Inventory_1` FOREIGN KEY (
	`store_id`
)
REFERENCES `매장` (
	`store_id`
);

ALTER TABLE `Store_Inventory` ADD CONSTRAINT `FK_Product_TO_Store_Inventory_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `Product` (
	`product_id`
);

ALTER TABLE `Delivery option` ADD CONSTRAINT `FK_Delivery price_TO_Delivery option_1` FOREIGN KEY (
	`price_id`
)
REFERENCES `Delivery price` (
	`price_id`
);

ALTER TABLE `offline_cart_product` ADD CONSTRAINT `FK_offline_cart_TO_offline_cart_product_1` FOREIGN KEY (
	`offline_cart_id`
)
REFERENCES `offline_cart` (
	`offline_cart_id`
);

ALTER TABLE `offline_cart_product` ADD CONSTRAINT `FK_Store_Inventory_TO_offline_cart_product_1` FOREIGN KEY (
	`inventory_id`
)
REFERENCES `Store_Inventory` (
	`inventory_id`
);

ALTER TABLE `offline_payment` ADD CONSTRAINT `FK_offline_order_TO_offline_payment_1` FOREIGN KEY (
	`order_id`
)
REFERENCES `offline_order` (
	`order_id`
);

ALTER TABLE `offline_payment` ADD CONSTRAINT `FK_offline_card_TO_offline_payment_1` FOREIGN KEY (
	`card_id`
)
REFERENCES `offline_card` (
	`card_id`
);

ALTER TABLE `offline_payment` ADD CONSTRAINT `FK_offline_cancels_TO_offline_payment_1` FOREIGN KEY (
	`cancels_id`
)
REFERENCES `offline_cancels` (
	`cancels_id`
);

ALTER TABLE `Employees` ADD CONSTRAINT `FK_매장_TO_Employees_1` FOREIGN KEY (
	`store_id`
)
REFERENCES `매장` (
	`store_id`
);

ALTER TABLE `Employees` ADD CONSTRAINT `FK_Warehouses_TO_Employees_1` FOREIGN KEY (
	`warehouse_id`
)
REFERENCES `Warehouses` (
	`warehouse_id`
);

ALTER TABLE `online_cart_product` ADD CONSTRAINT `FK_online_cart_TO_online_cart_product_1` FOREIGN KEY (
	`online_cart_id`
)
REFERENCES `online_cart` (
	`online_cart_id`
);

ALTER TABLE `online_cart_product` ADD CONSTRAINT `FK_Warehouse_Inventory_TO_online_cart_product_1` FOREIGN KEY (
	`inventory_id`
)
REFERENCES `Warehouse_Inventory` (
	`inventory_id`
);

ALTER TABLE `매장` ADD CONSTRAINT `FK_Employees_TO_매장_1` FOREIGN KEY (
	`manager_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `Delivery driver` ADD CONSTRAINT `FK_Employees_TO_Delivery driver_1` FOREIGN KEY (
	`employee_id`
)
REFERENCES `Employees` (
	`employee_id`
);

ALTER TABLE `Warehouse_Orders_Requests` ADD CONSTRAINT `FK_Warehouses_TO_Warehouse_Orders_Requests_1` FOREIGN KEY (
	`warehouse_id`
)
REFERENCES `Warehouses` (
	`warehouse_id`
);

ALTER TABLE `Point` ADD CONSTRAINT `FK_Customer_TO_Point_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `Review` ADD CONSTRAINT `FK_Customer_TO_Review_1` FOREIGN KEY (
	`customer_id`
)
REFERENCES `Customer` (
	`customer_id`
);

ALTER TABLE `Review` ADD CONSTRAINT `FK_online_cart_product_TO_Review_1` FOREIGN KEY (
	`product_id`
)
REFERENCES `online_cart_product` (
	`product_id`
);



