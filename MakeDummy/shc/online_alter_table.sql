-- 참조하는 테이블부터 삭제
DROP TABLE `Online_Cart_Product`;  -- 이 테이블은 `Online_Cart`를 참조
DROP TABLE `online_payment`;       -- 이 테이블은 `online_order`, `online_card`, `Online_Easy_Pay`, `online_cancels`를 참조
DROP TABLE `online_order`;         -- 이 테이블은 `Online_Cart`와 `Point`를 참조
DROP TABLE `Online_Cart`;          -- 이 테이블은 `Customer`를 참조
DROP TABLE `online_cancels`;       -- 이 테이블은 `online_payment`를 참조

-- 테이블 순서대로 생성
CREATE TABLE `Online_Cart` (
    `online_cart_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `customer_id` BIGINT NOT NULL,
    `total_price` INT NOT NULL,
    -- 외래 키 설정
    CONSTRAINT fk_customer_id FOREIGN KEY (`customer_id`) REFERENCES `Customer` (`customer_id`)
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

ALTER TABLE `online_card`
MODIFY COLUMN `issuer_code` VARCHAR(2) NOT NULL COMMENT '카드 발급사 코드',
MODIFY COLUMN `acquirer_code` VARCHAR(2) NOT NULL COMMENT '카드 매입사 코드';