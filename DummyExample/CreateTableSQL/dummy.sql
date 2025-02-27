use dummy;
show tables;
SELECT user, host FROM mysql.user;

select count(*) from user_info;
select * from user_info;

SELECT name, email, COUNT(*)
FROM user_info
GROUP BY name, email
HAVING COUNT(*) > 1;

drop table customer;


CREATE TABLE `customer` (
    `customer_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL COMMENT '고객명',
    `email` VARCHAR(255) NOT NULL COMMENT '고객 이메일',
    `phone` VARCHAR(255) NOT NULL COMMENT '휴대폰 번호',
    `password` VARCHAR(255) NULL COMMENT '비밀번호(폼로그인만 해당)',
    `login_type` ENUM('Form', 'Kakao', 'Google') NOT NULL COMMENT '로그인 타입',
    PRIMARY KEY (`customer_id`)
);

DESC customer;
select * from customer;

select * from customer;

select name from customer
where name like '%';

DELETE FROM customer;
TRUNCATE TABLE customer;
TRUNCATE TABLE Delivery_address;


CREATE TABLE `Delivery_address` (
    address_id BIGINT NOT NULL AUTO_INCREMENT,  -- ✅ Auto Increment 적용
    customer_id BIGINT NOT NULL,
    city VARCHAR(255) NOT NULL COMMENT '시',
    district VARCHAR(255) NOT NULL COMMENT '도',
    address VARCHAR(255) NOT NULL COMMENT '주소',
    address2 VARCHAR(255) NOT NULL COMMENT '상세 주소',
    postal_code VARCHAR(10) NOT NULL COMMENT '우편번호',
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ✅ 기본 키 설정
    PRIMARY KEY (address_id),

    -- ✅ 외래 키 설정 (customer 테이블을 참조)
    CONSTRAINT fk_배송지_고객 FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
);

select * from customer;
select * from Delivery_address;
select count(*) from customer;
select count(*) from Delivery_address;
