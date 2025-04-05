INSERT INTO Employees (name, phone, hire_date, salary, role, location_type, insurance) VALUES ('홍길동', '010-1234-5678', '2024-03-10', 3000000, '매장 직원', '매장', 1);
INSERT INTO Employees (name, phone, hire_date, salary, role, location_type, insurance) VALUES ('김철수', '010-9999-8888', '2024-03-10', -500000, '매장 직원', '매장', 1);
SELECT * FROM Store_Inventory WHERE store_id = 1 AND product_id = 5;
UPDATE Store_Inventory SET quantity = quantity - 10 WHERE store_id = 1 AND product_id = 5;
INSERT INTO Store_Order_Requests (store_id, quantity, status) VALUES (1, 100, '요청');
INSERT INTO Store_Order_Requests (store_id, status) VALUES (1, '요청');
INSERT INTO offline_payment (store_id, total_amount, payment_method) VALUES (1, 50000, '카드');

ALTER TABLE employees
ADD CONSTRAINT chk_positive CHECK (salary >= 0);

UPDATE Employees SET store_id = 2 WHERE employee_id = 3345;
UPDATE Employees SET role = '매장 재고 담당' WHERE employee_id = 367;
UPDATE Employees SET store_id = 999 WHERE employee_id = 5;
UPDATE Employees SET role = '배송 기사' WHERE employee_id = 15 AND store_id IS NOT NULL;

SELECT * FROM Employees WHERE employee_id = 15;

DELIMITER //

CREATE TRIGGER trg_validate_employee_role_update
BEFORE UPDATE ON Employees
FOR EACH ROW
BEGIN
    IF NEW.role = '배송 기사' AND OLD.store_id IS NOT NULL THEN
	INSERT INTO Employee_Trigger_Log (employee_id, old_role, new_role, old_store_id, new_store_id, old_warehouse_id, new_warehouse_id, action_type)
    VALUES (OLD.employee_id, OLD.role, NEW.role, OLD.store_id, NEW.store_id, OLD.warehouse_id, NEW.warehouse_id, 'UPDATE');
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '물류센터 직원은 매장에서 근무할 수 없습니다.';
    END IF;     

    
    -- 매장 직원의 역할에서 물류 직원으로 변경 시 store_id가 NULL이 아니면 예외 발생
    IF NEW.role IN ('물류 직원', '물류 재고 담당', '물류 관리자') AND OLD.store_id IS NOT NULL THEN
    INSERT INTO Employee_Trigger_Log (employee_id, old_role, new_role, old_store_id, new_store_id, old_warehouse_id, new_warehouse_id, action_type)
    VALUES (OLD.employee_id, OLD.role, NEW.role, OLD.store_id, NEW.store_id, OLD.warehouse_id, NEW.warehouse_id, 'UPDATE');
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '물류센터 직원은 매장에서 근무할 수 없습니다.';
    END IF;
    
    -- 물류 직원의 역할에서 매장 직원으로 변경 시 warehouse_id가 NULL이 아니면 예외 발생
    IF NEW.role IN ('매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자') AND OLD.warehouse_id IS NOT NULL THEN
    INSERT INTO Employee_Trigger_Log (employee_id, old_role, new_role, old_store_id, new_store_id, old_warehouse_id, new_warehouse_id, action_type)
    VALUES (OLD.employee_id, OLD.role, NEW.role, OLD.store_id, NEW.store_id, OLD.warehouse_id, NEW.warehouse_id, 'UPDATE');
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '매장 직원은 물류센터에서 근무할 수 없습니다.';
    END IF;
    
END //

DELIMITER ;

CREATE TABLE Employee_Trigger_Log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    old_role ENUM('고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사') NOT NULL,
    new_role ENUM('고객지원', '매장 직원', '매장 캐셔', '매장 재고 담당', '매장 관리자', '물류 직원', '물류 재고 담당', '물류 관리자', '배송 기사') NOT NULL,
    old_store_id BIGINT NULL,
    new_store_id BIGINT NULL,
    old_warehouse_id BIGINT NULL,
    new_warehouse_id BIGINT NULL,
    action_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from employee_trigger_log;

DELIMITER //

CREATE PROCEDURE sp_request_store_order(
    IN p_store_id BIGINT, 
    IN p_product_id BIGINT, 
    IN p_quantity INT
)
BEGIN
    DECLARE v_available_quantity INT;
    DECLARE v_request_id BIGINT;

    -- ✅ 1. 물류센터의 총 재고 중 10% 이하만 신청 가능하도록 제한
    SELECT quantity INTO v_available_quantity
    FROM Warehouse_Inventory 
    WHERE product_id = p_product_id;

    IF p_quantity > v_available_quantity * 0.1 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '요청한 수량이 물류센터 재고의 10%를 초과합니다.';
    END IF;

    -- ✅ 2. 매장 발주 요청 테이블에 데이터 삽입
    INSERT INTO Store_Order_Requests (store_id, quantity, status)
    VALUES (p_store_id, p_quantity, '요청');

    SET v_request_id = LAST_INSERT_ID(); -- 발주 요청 ID 저장

    -- ✅ 3. Store_Order_Details 테이블에 데이터 삽입
    INSERT INTO Store_Order_Details (request_id, product_id, quantity)
    VALUES (v_request_id, p_product_id, p_quantity);

    -- ✅ 4. Store_Order_Logs 테이블에 상태 변경 기록
    INSERT INTO Store_Order_Logs (request_id, status, changed_at)
    VALUES (v_request_id, '요청', NOW());

    -- ✅ 5. 물류센터 요청 테이블에도 동기화
    INSERT INTO Warehouse_Orders_Requests (warehouse_id, type, source, status)
    VALUES (1, '출고', '매장발주', '요청');

    -- ✅ 6. Warehouse_Orders_Details 테이블에 데이터 삽입
    INSERT INTO Warehouse_Orders_Details (request_id, product_id, quantity)
    VALUES (v_request_id, p_product_id, p_quantity);

    -- ✅ 7. Warehouse_Orders_Log 테이블에 상태 변경 기록
    INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
    VALUES (v_request_id, '요청', NOW());

END //

DELIMITER ;

select * from Store_Order_Requests order by request_id desc;

CALL sp_request_store_order(2, 5, 15); -- store_id, product_id, quantity

select * from Warehouse_Inventory where product_id = 5;


DELIMITER //
-- ✅ 트리거: Warehouse_Orders_Requests 상태 변경 → 매장(Store_Order_Requests) 동기화
CREATE TRIGGER trg_warehouse_order_status_update
AFTER UPDATE ON Warehouse_Orders_Requests
FOR EACH ROW
BEGIN
    -- 상태 변경 로그 기록 (Warehouse_Orders_Log)
    INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
    VALUES (NEW.request_id, NEW.status, NOW());

    -- ✅ 물류센터에서 상태 변경 가능한 값: 승인, 출고 준비 중, 출고 완료, 배송 중
    IF NEW.status IN ('승인', '출고 준비 중', '출고 완료', '배송 중') THEN
        UPDATE Store_Order_Requests
        SET status = NEW.status
        WHERE request_id = NEW.request_id;

        -- ✅ 매장 발주 상태 변경 로그 기록
        INSERT INTO Store_Order_Logs (request_id, status, changed_at)
        VALUES (NEW.request_id, NEW.status, NOW());
    END IF;

    -- ✅ 출고 완료 시 물류센터 재고 차감
    IF NEW.status = '출고 완료' THEN
        UPDATE Warehouse_Inventory wi
        JOIN Store_Order_Details sod ON wi.product_id = sod.product_id
        SET wi.quantity = wi.quantity - sod.quantity
        WHERE sod.request_id = NEW.request_id;
    END IF;
END //

DELIMITER ;

delimiter //

-- ✅ 트리거: Store_Order_Requests 상태 변경 → 물류센터(Warehouse_Orders_Requests) 동기화
CREATE TRIGGER trg_store_order_status_update
AFTER UPDATE ON Store_Order_Requests
FOR EACH ROW
BEGIN
    -- 상태 변경 로그 기록 (Store_Order_Logs)
    INSERT INTO Store_Order_Logs (request_id, status, changed_at)
    VALUES (NEW.request_id, NEW.status, NOW());

    -- ✅ 매장에서 상태 변경 가능한 값: 입고 준비 중, 입고 완료
    IF NEW.status IN ('입고 준비 중', '입고 완료') THEN
        UPDATE Warehouse_Orders_Requests
        SET status = NEW.status
        WHERE request_id = NEW.request_id;

        -- ✅ 물류센터 발주 상태 변경 로그 기록
        INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
        VALUES (NEW.request_id, NEW.status, NOW());
    END IF;

    -- ✅ 입고 완료 시 매장 재고 증가
    IF NEW.status = '입고 완료' THEN
        UPDATE Store_Inventory si
        JOIN Store_Order_Details sod ON si.store_id = NEW.store_id AND si.product_id = sod.product_id
        SET si.quantity = si.quantity + sod.quantity
        WHERE sod.request_id = NEW.request_id;
    END IF;
END //

delimiter ;

delimiter //
-- ✅ 트리거: Store_Order_Requests 또는 Warehouse_Orders_Requests에서 상태값이 '취소'로 변경되었을 때 동기화
CREATE TRIGGER trg_order_cancel_sync
AFTER UPDATE ON Store_Order_Requests
FOR EACH ROW
BEGIN
    -- ✅ 취소 처리: 언제든 가능 (입고 완료 이후는 매장에서만 가능)
    IF NEW.status = '취소' THEN
        UPDATE Warehouse_Orders_Requests
        SET status = '취소'
        WHERE request_id = NEW.request_id;

        -- ✅ 취소 로그 기록
        INSERT INTO Store_Order_Logs (request_id, status, changed_at)
        VALUES (NEW.request_id, '취소', NOW());

        INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
        VALUES (NEW.request_id, '취소', NOW());

        -- ✅ 입고 전에 취소된 경우 → 물류센터 재고 복구
        IF OLD.status IN ('출고 완료') THEN
            UPDATE Warehouse_Inventory wi
            JOIN Store_Order_Details sod ON wi.product_id = sod.product_id
            SET wi.quantity = wi.quantity + sod.quantity
            WHERE sod.request_id = NEW.request_id;
        END IF;

        -- ✅ 입고 후에 취소된 경우 → 매장 재고 차감, 물류센터 재고 복구
        IF OLD.status = '입고 완료' THEN
            UPDATE Store_Inventory si
            JOIN Store_Order_Details sod ON si.store_id = NEW.store_id AND si.product_id = sod.product_id
            SET si.quantity = si.quantity - sod.quantity
            WHERE sod.request_id = NEW.request_id;

            UPDATE Warehouse_Inventory wi
            JOIN Store_Order_Details sod ON wi.product_id = sod.product_id
            SET wi.quantity = wi.quantity + sod.quantity
            WHERE sod.request_id = NEW.request_id;
        END IF;
    END IF;
END //

delimiter ;

-- 1️⃣ 승인 처리 (요청 → 승인)
UPDATE Warehouse_Orders_Requests
SET status = '승인'
WHERE request_id = 123;

select * from Store_Order_Logs where request_id = 123;

-- 2️⃣ 출고 준비 중 처리 (승인 → 출고 준비 중)
UPDATE Warehouse_Orders_Requests
SET status = '출고 준비 중'
WHERE request_id = 123;

-- 3️⃣ 출고 완료 처리 (출고 준비 중 → 출고 완료) → 물류센터 재고 차감
UPDATE Warehouse_Orders_Requests
SET status = '출고 완료'
WHERE request_id = 123;

-- 4️⃣ 배송 중 처리 (출고 완료 → 배송 중)
UPDATE Warehouse_Orders_Requests
SET status = '취소'
WHERE request_id = 50001;

DELIMITER //

CREATE TRIGGER trg_online_payment_status_update
AFTER UPDATE ON online_payment
FOR EACH ROW
BEGIN
    -- ✅ 결제 완료 시 (DONE) → 창고 재고 차감
    IF NEW.status = 'DONE' THEN
        UPDATE Warehouse_Inventory wi
        JOIN Online_Cart_Product ocp ON wi.inventory_id = ocp.inventory_id
        JOIN Online_Cart oc ON ocp.online_cart_id = oc.online_cart_id
        JOIN online_order oo ON oc.online_cart_id = oo.online_cart_id
        SET wi.quantity = wi.quantity - ocp.quantity
        WHERE oo.order_id = NEW.order_id;
    END IF;

    -- ✅ 결제 취소 시 (CANCELED) → 창고 재고 복구
    IF NEW.status = 'CANCELED' THEN
        UPDATE Warehouse_Inventory wi
        JOIN Online_Cart_Product ocp ON wi.inventory_id = ocp.inventory_id
        JOIN Online_Cart oc ON ocp.online_cart_id = oc.online_cart_id
        JOIN online_order oo ON oc.online_cart_id = oo.online_cart_id
        SET wi.quantity = wi.quantity + ocp.quantity
        WHERE oo.order_id = NEW.order_id;
    END IF;

    -- ✅ 부분 취소 시 (PARTIAL_CANCELED) → 취소된 수량만큼 창고 재고 복구
IF NEW.status = 'PARTIAL_CANCELED' THEN
    UPDATE Warehouse_Inventory wi
    JOIN Online_Cart_Product ocp ON wi.inventory_id = ocp.inventory_id
    JOIN Online_Cart oc ON ocp.online_cart_id = oc.online_cart_id
    JOIN online_order oo ON oc.online_cart_id = oo.online_cart_id
    SET wi.quantity = wi.quantity + 
        CASE WHEN ocp.price != 0 THEN (NEW.total_amount - NEW.balance_amount) / ocp.price ELSE 0 END
    WHERE oo.order_id = NEW.order_id;
END IF;
END //

DELIMITER ;

UPDATE online_payment 
SET status = 'DONE'
WHERE online_payment_id = 123;
-- 주문 결제가 완료됨 (창고 재고 차감)

UPDATE online_payment 
SET status = 'CANCELED'
WHERE online_payment_id = 123;
-- 주문이 취소됨 (창고 재고 복구)

UPDATE online_payment 
SET status = 'PARTIAL_CANCELED', balance_amount = balance_amount - 5000
WHERE online_payment_id = 123;
-- 부분 취소됨 (취소된 수량만큼 창고 재고 복구)

-- 각 주문 후 물류센터 재고 확인
SELECT wi.inventory_id, wi.product_id, wi.quantity
FROM Warehouse_Inventory wi
JOIN Online_Cart_Product ocp ON wi.inventory_id = ocp.inventory_id
JOIN Online_Cart oc ON ocp.online_cart_id = oc.online_cart_id
JOIN online_order oo ON oc.online_cart_id = oo.online_cart_id
JOIN online_payment op ON oo.order_id = op.order_id
WHERE op.online_payment_id = 123;

DELIMITER //

CREATE TRIGGER trg_offline_payment_status_update
AFTER UPDATE ON Offline_Payment
FOR EACH ROW
BEGIN
    -- ✅ 결제 완료 시 (paid) → 매장 재고 차감
    IF NEW.status = 'paid' THEN
        UPDATE Store_Inventory si
        JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
        JOIN Offline_Cart oc ON ocp.offline_cart_id = oc.offline_cart_id
        JOIN Offline_Order oo ON oc.offline_cart_id = oo.offline_cart_id
        SET si.quantity = si.quantity - ocp.quantity
        WHERE oo.order_id = NEW.order_id;
    END IF;

    -- ✅ 결제 취소 시 (cancelled) → 매장 재고 복구
    IF NEW.status = 'cancelled' THEN
        UPDATE Store_Inventory si
        JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
        JOIN Offline_Cart oc ON ocp.offline_cart_id = oc.offline_cart_id
        JOIN Offline_Order oo ON oc.offline_cart_id = oo.offline_cart_id
        SET si.quantity = si.quantity + ocp.quantity
        WHERE oo.order_id = NEW.order_id;
    END IF;

    -- ✅ 부분 취소 시 (partialCancelled) → 취소된 금액만큼 매장 재고 복구
    IF NEW.status = 'partialCancelled' THEN
        UPDATE Store_Inventory si
        JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
        JOIN Offline_Cart oc ON ocp.offline_cart_id = oc.offline_cart_id
        JOIN Offline_Order oo ON oc.offline_cart_id = oo.offline_cart_id
        SET si.quantity = si.quantity + (NEW.amount - NEW.balance_amt) / ocp.price
        WHERE oo.order_id = NEW.order_id;
    END IF;
END //

DELIMITER ;

UPDATE Offline_Payment 
SET status = 'paid'
WHERE offline_payment_id = 456;
-- 결제가 완료됨 (매장 재고 차감)

UPDATE Offline_Payment 
SET status = 'cancelled'
WHERE offline_payment_id = 456;
-- 결제가 취소됨 (매장 재고 복구)

UPDATE Offline_Payment 
SET status = 'partialCancelled', balance_amt = balance_amt - 3000
WHERE offline_payment_id = 456;
-- 부분 취소됨 (취소된 수량만큼 매장 재고 복구)

-- 카드 매출만
CREATE OR REPLACE VIEW Store_Sales_Report_Card AS
SELECT 
    s.store_id AS '매장 ID',
    s.name AS '매장 이름',
    CONCAT('\\ ', FORMAT(SUM(op.amount), 0)) AS '총 카드 매출',
    DATE(op.paid_at) AS '결제일'
FROM Stores s
JOIN Store_Inventory si ON s.store_id = si.store_id
JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
JOIN Offline_Order oo ON ocp.offline_cart_id = oo.offline_cart_id
JOIN Offline_Payment op ON oo.order_id = op.order_id
WHERE op.status = 'paid'
GROUP BY s.store_id, s.name, DATE(op.paid_at);

-- 카드 매출 뷰
CREATE OR REPLACE VIEW Store_Sales_Report_Card AS
SELECT 
    s.store_id AS '매장 ID',
    s.name AS '매장 이름',
    CONCAT('\\ ', FORMAT(SUM(op.amount), 0)) AS '총 카드 매출',
    CONCAT('\\ ', FORMAT(SUM(p.delta), 0)) AS '포인트 사용 금액',
    CONCAT('\\ ', FORMAT(SUM(ocp.price - pp.final_price), 0)) AS '할인 금액',
    CONCAT('\\ ', FORMAT(SUM(op.amount) - SUM(p.delta) - SUM(ocp.price - pp.final_price), 0)) AS '순수 매출',
    DATE(op.paid_at) AS '결제일'
FROM Stores s
JOIN Store_Inventory si ON s.store_id = si.store_id
JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
JOIN Offline_Order oo ON ocp.offline_cart_id = oo.offline_cart_id
JOIN Point p ON oo.point_id = p.point_id
JOIN Offline_Payment op ON oo.order_id = op.order_id
JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
WHERE op.status = 'paid'
GROUP BY s.store_id, s.name, DATE(op.paid_at);

SELECT * 
FROM Store_Sales_Report_Card 
WHERE `결제일` = '2025-03-14'
AND `매장 ID` = 3;

SELECT *
FROM Store_Sales_Report_Card
WHERE DATE_FORMAT(`결제일`, '%Y-%m') = '2024-04'
AND `매장 ID` = 3
order by `결제일`;

SELECT 
    `매장 ID`,
    `매장 이름`,
    DATE_FORMAT(`결제일`, '%Y-%m') AS '월',
    CONCAT('\\ ', FORMAT(SUM(CAST(REPLACE(REPLACE(`총 카드 매출`, '\\ ', ''), ',', '') AS UNSIGNED)), 0)) AS '연도별 총 현금 매출'
FROM Store_Sales_Report_Card
WHERE YEAR(`결제일`) = 2024
AND `매장 ID` = 5
GROUP BY `매장 ID`, `매장 이름`, DATE_FORMAT(`결제일`, '%Y-%m')
ORDER BY `월`;

-- 현금 매출만
CREATE OR REPLACE VIEW Store_Sales_Report_Cash AS
SELECT 
    s.store_id AS '매장 ID',
    s.name AS '매장 이름',
    concat('\\ ', FORMAT(SUM(oc.amount), 0)) AS '총 현금 매출',
    DATE(oc.pay_date) AS '결제일'
FROM Stores s
JOIN Store_Inventory si ON s.store_id = si.store_id
JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
JOIN Offline_Order oo ON ocp.offline_cart_id = oo.offline_cart_id
JOIN offline_cash oc ON oo.order_id = oc.order_id
WHERE oc.status = 'COMPLETE'
GROUP BY s.store_id, s.name, DATE(oc.pay_date);

-- 현금 매출 뷰
CREATE OR REPLACE VIEW Store_Sales_Report_Cash AS
SELECT 
    s.store_id AS '매장 ID',
    s.name AS '매장 이름',
    CONCAT('\\ ', FORMAT(SUM(oc.amount), 0)) AS '총 현금 매출',
    CONCAT('\\ ', FORMAT(SUM(p.delta), 0)) AS '포인트 사용 금액',
    CONCAT('\\ ', FORMAT(SUM(ocp.price - pp.final_price), 0)) AS '할인 금액',
    CONCAT('\\ ', FORMAT(SUM(oc.amount) - SUM(p.delta) - SUM(ocp.price - pp.final_price), 0)) AS '순수 매출',
    DATE(oc.pay_date) AS '결제일'
FROM Stores s
JOIN Store_Inventory si ON s.store_id = si.store_id
JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
JOIN Offline_Order oo ON ocp.offline_cart_id = oo.offline_cart_id
JOIN Point p ON oo.point_id = p.point_id
JOIN offline_cash oc ON oo.order_id = oc.order_id
JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
WHERE oc.status = 'COMPLETE'
GROUP BY s.store_id, s.name, DATE(oc.pay_date);

SELECT * 
FROM Store_Sales_Report_Cash 
WHERE `결제일` = '2025-03-17'
AND `매장 ID` = 3;

SELECT *
FROM Store_Sales_Report_Cash
WHERE DATE_FORMAT(`결제일`, '%Y-%m') = '2024-04'
AND `매장 ID` = 3
order by `결제일`;

SELECT 
    `매장 ID`,
    `매장 이름`,
    CONCAT('\\ ', FORMAT(SUM(CAST(REPLACE(REPLACE(`총 현금 매출`, '\\ ', ''), ',', '') AS UNSIGNED)), 0)) AS '연도별 총 현금 매출',    
    DATE_FORMAT(`결제일`, '%Y-%m') AS '월'
FROM Store_Sales_Report_Cash
WHERE YEAR(`결제일`) = 2024
AND `매장 ID` = 5
GROUP BY `매장 ID`, `매장 이름`, DATE_FORMAT(`결제일`, '%Y-%m')
ORDER BY `월`;

-- 합산 매출
SELECT 
    s.store_id,
    s.name,
    c.`총 카드 매출`,
    ca.`총 현금 매출`,
    CONCAT('\\ ', FORMAT(
        COALESCE(CAST(REPLACE(REPLACE(c.`총 카드 매출`, '\\ ', ''), ',', '') AS UNSIGNED), 0) +
        COALESCE(CAST(REPLACE(REPLACE(ca.`총 현금 매출`, '\\ ', ''), ',', '') AS UNSIGNED), 0)
    , 0)) AS '총 합계 매출',
    GREATEST(
        COALESCE(c.last_card_payment_date, '1900-01-01'),
        COALESCE(ca.last_cash_payment_date, '1900-01-01')
    ) AS '최근 결제일'
FROM Stores s
LEFT JOIN (
    SELECT `매장 ID`, SUM(CAST(REPLACE(REPLACE(`총 카드 매출`, '\\ ', ''), ',', '') AS UNSIGNED)) AS `총 카드 매출`, MAX(`결제일`) AS last_card_payment_date
    FROM Store_Sales_Report_Card
    GROUP BY `매장 ID`
) c ON s.store_id = c.`매장 ID`
LEFT JOIN (
    SELECT `매장 ID`, SUM(CAST(REPLACE(REPLACE(`총 현금 매출`, '\\ ', ''), ',', '') AS UNSIGNED)) AS `총 현금 매출`, MAX(`결제일`) AS last_cash_payment_date
    FROM Store_Sales_Report_Cash
    GROUP BY `매장 ID`
) ca ON s.store_id = ca.`매장 ID`;

-- 합산 매출 쿼리
SELECT 
    s.store_id,
    s.name,
    CONCAT('\\ ', FORMAT(c.total_card_sales, 0)) AS '총 카드 매출',
    CONCAT('\\ ', FORMAT(ca.total_cash_sales, 0)) AS '총 현금 매출',
    CONCAT('\\ ', FORMAT(c.total_card_sales + ca.total_cash_sales, 0)) AS '총 합계 매출',
    CONCAT('\\ ', FORMAT(c.total_card_point + ca.total_cash_point, 0)) AS '총 포인트 사용 금액',
    CONCAT('\\ ', FORMAT(c.total_card_discount + ca.total_cash_discount, 0)) AS '총 할인 금액',
    CONCAT('\\ ', FORMAT(
        (c.total_card_sales + ca.total_cash_sales) - 
        (c.total_card_point + ca.total_cash_point) - 
        (c.total_card_discount + ca.total_cash_discount)
    , 0)) AS '총 순수 매출',
    GREATEST(
        COALESCE(c.last_card_payment_date, '1900-01-01'),
        COALESCE(ca.last_cash_payment_date, '1900-01-01')
    ) AS '최근 결제일'
FROM Stores s
LEFT JOIN (
    SELECT `매장 ID`,
        SUM(CAST(REPLACE(REPLACE(`총 카드 매출`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_card_sales,
        SUM(CAST(REPLACE(REPLACE(`포인트 사용 금액`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_card_point,
        SUM(CAST(REPLACE(REPLACE(`할인 금액`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_card_discount,
        MAX(`결제일`) AS last_card_payment_date
    FROM Store_Sales_Report_Card
    GROUP BY `매장 ID`
) c ON s.store_id = c.`매장 ID`
LEFT JOIN (
    SELECT `매장 ID`,
        SUM(CAST(REPLACE(REPLACE(`총 현금 매출`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_cash_sales,
        SUM(CAST(REPLACE(REPLACE(`포인트 사용 금액`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_cash_point,
        SUM(CAST(REPLACE(REPLACE(`할인 금액`, '\\ ', ''), ',', '') AS UNSIGNED)) AS total_cash_discount,
        MAX(`결제일`) AS last_cash_payment_date
    FROM Store_Sales_Report_Cash
    GROUP BY `매장 ID`
) ca ON s.store_id = ca.`매장 ID`;

-- 매출 보고서 프로시저 적용 INDEX
CREATE INDEX idx_payment_paid_at ON Offline_Payment(paid_at, status);

CREATE INDEX idx_cash_pay_date ON offline_cash(pay_date, status);

CREATE INDEX idx_cart_product ON Offline_Cart_Product(offline_cart_id, inventory_id);

CREATE INDEX idx_store_inventory ON Store_Inventory(inventory_id, store_id);

-- 매출 보고서 프로시저 (검색 엔진)
DELIMITER //

CREATE PROCEDURE sp_store_sales_report(
    IN p_store_id BIGINT,
    IN p_search_type VARCHAR(10),
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_method_type VARCHAR(10),
    IN p_order_by VARCHAR(50),
    IN p_order_dir VARCHAR(4)
)
BEGIN
    DECLARE date_condition VARCHAR(255);

    -- 날짜 조건 생성
    IF p_search_type = 'day' THEN
        SET date_condition = CONCAT('DATE(pay_date) = ''', p_start_date, '''');
    ELSEIF p_search_type = 'month' THEN
        SET date_condition = CONCAT('DATE_FORMAT(pay_date, ''%Y-%m'') = DATE_FORMAT(''', p_start_date, ''', ''%Y-%m'')');
    ELSEIF p_search_type = 'year' THEN
        SET date_condition = CONCAT('YEAR(pay_date) = YEAR(''', p_start_date, ''')');
    ELSEIF p_search_type = 'custom' THEN
        SET date_condition = CONCAT('DATE(pay_date) BETWEEN ''', p_start_date, ''' AND ''', p_end_date, '''');
    END IF;

    -- 동적 쿼리 생성
    SET @query = CONCAT(
        'SELECT 
            s.name AS 매장_이름,
            CASE WHEN ''', p_search_type, ''' = "year" THEN DATE_FORMAT(pay_date, "%Y-%m") ELSE DATE(pay_date) END AS 결제일,
            SUM(CASE WHEN op.offline_payment_id IS NOT NULL THEN op.amount ELSE 0 END) AS 카드_매출,
            SUM(CASE WHEN oc.offline_cash_id IS NOT NULL THEN oc.amount ELSE 0 END) AS 현금_매출,
            SUM(IFNULL(op.amount, 0) + IFNULL(oc.amount, 0)) AS 총_매출,
            SUM(p.delta) AS 포인트_사용_금액,
            SUM(ocp.price - pp.final_price) AS 할인_금액,
            SUM(IFNULL(op.amount, 0) + IFNULL(oc.amount, 0) - p.delta - (ocp.price - pp.final_price)) AS 순수_매출
        FROM Stores s
        LEFT JOIN Store_Inventory si ON s.store_id = si.store_id
        LEFT JOIN Offline_Cart_Product ocp ON si.inventory_id = ocp.inventory_id
        LEFT JOIN Offline_Cart ocart ON ocp.offline_cart_id = ocart.offline_cart_id
        LEFT JOIN Offline_Order oo ON ocart.offline_cart_id = oo.offline_cart_id
        LEFT JOIN Point p ON oo.point_id = p.point_id
        LEFT JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
        LEFT JOIN Offline_Payment op ON op.order_id = oo.order_id AND op.status = "paid"
        LEFT JOIN offline_cash oc ON oc.order_id = oo.order_id AND oc.status = "COMPLETE"
        WHERE s.store_id = ', p_store_id, '
        AND ', date_condition, '
        ', CASE WHEN p_method_type = 'card' THEN 'AND op.offline_payment_id IS NOT NULL' 
                 WHEN p_method_type = 'cash' THEN 'AND oc.offline_cash_id IS NOT NULL' ELSE '' END, '
        GROUP BY s.name, CASE WHEN ''', p_search_type, ''' = "year" THEN DATE_FORMAT(pay_date, "%Y-%m") ELSE DATE(pay_date) END
        ORDER BY ', p_order_by, ' ', p_order_dir
    );

    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;


CALL sp_store_sales_report(3, 'year', '2025-01-01', NULL, 'all', '결제일', 'desc');
-- store_id (매장 ID)
-- p_search_type ('day', 'month', 'year', 'custom')
-- p_start_date
-- p_end_date (day 타입은 NULL)
-- p_method_type ('all', 'card', 'cash')
-- p_order_by (정렬할 컬럼)
-- p_order_dir ('asc', 'desc')

DELIMITER //

CREATE PROCEDURE sp_store_sales_report_explain(
    IN p_store_id BIGINT,
    IN p_search_type VARCHAR(10),
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_method_type VARCHAR(10),
    IN p_order_by VARCHAR(50),
    IN p_order_dir VARCHAR(4)
)
BEGIN
    DECLARE date_condition VARCHAR(255);

    IF p_search_type = 'day' THEN
        SET date_condition = CONCAT('DATE(formatted_date) = ''', p_start_date, '''');
    ELSEIF p_search_type = 'month' THEN
        SET date_condition = CONCAT('DATE_FORMAT(formatted_date, ''%Y-%m'') = DATE_FORMAT(''', p_start_date, ''', ''%Y-%m'')');
    ELSEIF p_search_type = 'year' THEN
        SET date_condition = CONCAT('YEAR(formatted_date) = YEAR(''', p_start_date, ''')');
    ELSEIF p_search_type = 'custom' THEN
        SET date_condition = CONCAT('DATE(formatted_date) BETWEEN ''', p_start_date, ''' AND ''', p_end_date, '''');
    END IF;

    SET @query = CONCAT(
        'SELECT 
            s.name AS 매장_이름,
            c.formatted_date AS 결제일,
            SUM(c.card_amount) AS 카드_매출,
            SUM(c.cash_amount) AS 현금_매출,
            SUM(c.card_amount + c.cash_amount) AS 총_매출,
            SUM(c.point_used) AS 포인트_사용_금액,
            SUM(c.discount_amount) AS 할인_금액,
            SUM(c.card_amount + c.cash_amount - c.point_used - c.discount_amount) AS 순수_매출
        FROM Stores s
        LEFT JOIN (
            -- 카드 결제 집계
            SELECT 
                si.store_id, 
                CASE WHEN ''', p_search_type, ''' = "year" THEN DATE_FORMAT(op.paid_at, "%Y-%m") ELSE DATE(op.paid_at) END AS formatted_date,
                SUM(op.amount) AS card_amount,
                0 AS cash_amount,
                SUM(p.delta) AS point_used,
                SUM(ocp.price - pp.final_price) AS discount_amount
            FROM Offline_Payment op
            JOIN Offline_Order oo ON op.order_id = oo.order_id
            JOIN Point p ON oo.point_id = p.point_id
            JOIN Offline_Cart ocart ON oo.offline_cart_id = ocart.offline_cart_id
            JOIN Offline_Cart_Product ocp ON ocart.offline_cart_id = ocp.offline_cart_id
            JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
            JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
            WHERE op.status = "paid"
            GROUP BY si.store_id, formatted_date

            UNION ALL

            -- 현금 결제 집계
            SELECT 
                si.store_id,
                CASE WHEN ''', p_search_type, ''' = "year" THEN DATE_FORMAT(oc.pay_date, "%Y-%m") ELSE DATE(oc.pay_date) END AS formatted_date,
                0 AS card_amount,
                SUM(oc.amount) AS cash_amount,
                SUM(p.delta) AS point_used,
                SUM(ocp.price - pp.final_price) AS discount_amount
            FROM offline_cash oc
            JOIN Offline_Order oo ON oc.order_id = oo.order_id
            JOIN Point p ON oo.point_id = p.point_id
            JOIN Offline_Cart ocart ON oo.offline_cart_id = ocart.offline_cart_id
            JOIN Offline_Cart_Product ocp ON ocart.offline_cart_id = ocp.offline_cart_id
            JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
            JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
            WHERE oc.status = "COMPLETE"
            GROUP BY si.store_id, formatted_date
        ) c ON s.store_id = c.store_id
        WHERE s.store_id = ', p_store_id, '
        AND ', date_condition, '
        GROUP BY s.name, c.formatted_date
        ORDER BY ', p_order_by, ' ', p_order_dir
    );

    -- EXPLAIN 실행
    SET @explain_query = CONCAT('EXPLAIN ', @query);
    PREPARE stmt FROM @explain_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END //

DELIMITER ;

CALL sp_store_sales_report_explain(
    2,
    'custom',
    '2025-03-01',
    '2025-03-15',
    'all',
    '순수_매출',
    'desc'
);


CREATE TABLE Store_Sales_Summary (
    summary_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'PK',
    store_id BIGINT NOT NULL COMMENT '매장 ID',
    report_date DATE NOT NULL COMMENT '통계 날짜 (일 단위)',
    card_sales INT NOT NULL DEFAULT 0 COMMENT '카드 매출',
    cash_sales INT NOT NULL DEFAULT 0 COMMENT '현금 매출',
    total_sales INT NOT NULL DEFAULT 0 COMMENT '총 매출',
    point_used INT NOT NULL DEFAULT 0 COMMENT '포인트 사용 금액',
    discount_amount INT NOT NULL DEFAULT 0 COMMENT '할인 금액',
    net_sales INT NOT NULL DEFAULT 0 COMMENT '순수 매출',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '데이터 생성일',
    UNIQUE KEY uk_store_date (store_id, report_date)
);

-- 통계 데이터 자정마다 insert
DELIMITER //

CREATE EVENT IF NOT EXISTS daily_store_sales_summary
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 2 DAY
DO
BEGIN
    INSERT INTO Store_Sales_Summary
        (store_id, report_date, card_sales, cash_sales, total_sales, point_used, discount_amount, net_sales)
    SELECT
        si.store_id,
        CURDATE() AS report_date,
        SUM(CASE WHEN op.status = 'paid' THEN op.amount ELSE 0 END) AS card_sales,
        SUM(CASE WHEN oc.status = 'COMPLETE' THEN oc.amount ELSE 0 END) AS cash_sales,
        SUM(CASE WHEN op.status = 'paid' THEN op.amount ELSE 0 END) + SUM(CASE WHEN oc.status = 'COMPLETE' THEN oc.amount ELSE 0 END) AS total_sales,
        SUM(p.delta) AS point_used,
        SUM(CASE WHEN ocp.price > pp.final_price THEN ocp.price - pp.final_price ELSE 0 END) AS discount_amount,
        SUM(
            (CASE WHEN op.status = 'paid' THEN op.amount ELSE 0 END) +
            (CASE WHEN oc.status = 'COMPLETE' THEN oc.amount ELSE 0 END)
        ) - SUM(p.delta) - SUM(CASE WHEN ocp.price > pp.final_price THEN ocp.price - pp.final_price ELSE 0 END) AS net_sales
    FROM Offline_Cart_Product ocp
    JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
    JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
    LEFT JOIN Offline_Cart ocart ON ocp.offline_cart_id = ocart.offline_cart_id
    LEFT JOIN Offline_Order oo ON ocart.offline_cart_id = oo.offline_cart_id
    LEFT JOIN Point p ON oo.point_id = p.point_id
    LEFT JOIN Offline_Payment op ON oo.order_id = op.order_id AND op.status = 'paid' AND DATE(op.paid_at) = CURDATE()
    LEFT JOIN offline_cash oc ON oo.order_id = oc.order_id AND oc.status = 'COMPLETE' AND DATE(oc.pay_date) = CURDATE()
    GROUP BY si.store_id;
END //

DELIMITER ;

SELECT count(*) FROM Store_Sales_Summary;

DROP PROCEDURE sp_get_sales_summary_range;

DROP PROCEDURE sp_get_sales_summary_range;

-- 검색 프로시저
DELIMITER //

CREATE PROCEDURE sp_get_sales_summary_range (
    IN p_store_id INT,
    IN p_period_type VARCHAR(10), -- 'day', 'month', 'custom'
    IN p_start_date DATE,
    IN p_end_date DATE, -- custom일 때 사용
    IN p_sales_type VARCHAR(10), -- 'total', 'card', 'cash'
    IN p_order_by VARCHAR(50),
    IN p_order_dir VARCHAR(4)
)
BEGIN
    DECLARE date_condition VARCHAR(255);

    -- 날짜 필터 조건 설정
    IF p_period_type = 'day' THEN
        SET date_condition = CONCAT('report_date = ''', p_start_date, '''');
    ELSEIF p_period_type = 'month' THEN
        SET date_condition = CONCAT('DATE_FORMAT(report_date, "%Y-%m") = DATE_FORMAT(''', p_start_date, ''', "%Y-%m")');
    ELSEIF p_period_type = 'custom' THEN
        SET date_condition = CONCAT('report_date BETWEEN ''', p_start_date, ''' AND ''', p_end_date, '''');
    END IF;

    -- 동적 쿼리 생성
    SET @query = CONCAT(
        'SELECT 
            s.name AS 매장명, 
            ss.report_date AS 결제일, 
            FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''card'') THEN ss.card_sales ELSE 0 END), 0) AS 카드_매출, 
            FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''cash'') THEN ss.cash_sales ELSE 0 END), 0) AS 현금_매출, 
            FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' = ''total'' THEN ss.total_sales ELSE 0 END), 0) AS 총_매출, 
            FORMAT(SUM(ss.point_used), 0) AS 포인트_사용_금액, 
            FORMAT(SUM(ss.discount_amount), 0) AS 할인_금액, 
            FORMAT(SUM(ss.net_sales), 0) AS 순수_매출 
        FROM Store_Sales_Summary ss 
        JOIN Stores s ON ss.store_id = s.store_id 
        WHERE ss.store_id = ', p_store_id, ' AND ', date_condition, ' 
        GROUP BY s.name, ss.report_date 
        ORDER BY ', p_order_by, ' ', p_order_dir
    );

    -- 쿼리 실행
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

END //

DELIMITER ;

drop procedure sp_get_sales_summary_year;

DELIMITER //

CREATE PROCEDURE sp_get_sales_summary_year (
    IN p_store_id INT,
    IN p_start_date DATE,
    IN p_sales_type VARCHAR(10), -- 'total', 'card', 'cash'
    IN p_order_by VARCHAR(50),   -- NULL or alias명
    IN p_order_dir VARCHAR(4)    -- 'asc', 'desc'
)
BEGIN
    DECLARE date_condition VARCHAR(255);
    DECLARE order_clause VARCHAR(255);

    -- 1년치 필터 조건 설정
    SET date_condition = CONCAT('YEAR(report_date) = YEAR(''', p_start_date, ''')');

    -- order by CASE WHEN 매핑
    IF p_order_by IS NULL OR p_order_by = '' THEN
        SET order_clause = CONCAT('ORDER BY DATE_FORMAT(ss.report_date, "%Y-%m") ', p_order_dir);
    ELSEIF p_order_by = '카드_매출' THEN
        SET order_clause = CONCAT('ORDER BY SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''card'') THEN ss.card_sales ELSE 0 END) ', p_order_dir);
    ELSEIF p_order_by = '현금_매출' THEN
        SET order_clause = CONCAT('ORDER BY SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''cash'') THEN ss.cash_sales ELSE 0 END) ', p_order_dir);
    ELSEIF p_order_by = '총_매출' THEN
        SET order_clause = CONCAT('ORDER BY SUM(CASE WHEN ''', p_sales_type, ''' = ''total'' THEN ss.total_sales ELSE 0 END) ', p_order_dir);
    ELSEIF p_order_by = '포인트_사용_금액' THEN
        SET order_clause = CONCAT('ORDER BY SUM(ss.point_used) ', p_order_dir);
    ELSEIF p_order_by = '할인_금액' THEN
        SET order_clause = CONCAT('ORDER BY SUM(ss.discount_amount) ', p_order_dir);
    ELSEIF p_order_by = '순수_매출' THEN
        SET order_clause = CONCAT('ORDER BY SUM(ss.net_sales) ', p_order_dir);
    ELSE
        SET order_clause = CONCAT('ORDER BY DATE_FORMAT(ss.report_date, "%Y-%m") ', p_order_dir);
    END IF;

    -- 동적 쿼리 생성 (월별로 그룹핑)
    SET @query = CONCAT(
        'SELECT 
            s.name AS 매장명,
            DATE_FORMAT(ss.report_date, "%Y-%m") AS 결제월, ',

        'FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''card'') THEN ss.card_sales ELSE 0 END), 0) AS 카드_매출, ',

        'FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' IN (''total'', ''cash'') THEN ss.cash_sales ELSE 0 END), 0) AS 현금_매출, ',

        'FORMAT(SUM(CASE WHEN ''', p_sales_type, ''' = ''total'' THEN ss.total_sales ELSE 0 END), 0) AS 총_매출, ',

        'FORMAT(SUM(ss.point_used), 0) AS 포인트_사용_금액, ',

        'FORMAT(SUM(ss.discount_amount), 0) AS 할인_금액, ',

        'FORMAT(SUM(ss.net_sales), 0) AS 순수_매출 ',

        'FROM Store_Sales_Summary ss ',
        'JOIN Stores s ON ss.store_id = s.store_id ',
        'WHERE ss.store_id = ', p_store_id, ' AND ', date_condition, ' ',
        'GROUP BY s.name, DATE_FORMAT(ss.report_date, "%Y-%m") ',
        order_clause
    );

    -- 쿼리 실행
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

END //

DELIMITER ;

-- 카드
-- 📅 하루 (day)
CALL sp_get_sales_summary_range(3, 'day', '2025-03-20', NULL, 'card', 'report_date', 'desc');

-- 📅 한달 (month)
CALL sp_get_sales_summary_range(3, 'month', '2025-03-01', NULL, 'card', 'report_date', 'desc');

-- 📅 1년 (year)
CALL sp_get_sales_summary_year(3, '2024-01-01', 'card', '', 'desc');

-- 📅 커스텀 기간 (custom)
CALL sp_get_sales_summary_range(3, 'custom', '2025-01-01', '2025-03-20', 'card', 'report_date', 'desc');

-- 현금
-- 📅 하루 (day)
CALL sp_get_sales_summary_range(3, 'day', '2025-03-20', NULL, 'cash', 'report_date', 'desc');

-- 📅 한달 (month)
CALL sp_get_sales_summary_range(3, 'month', '2025-03-01', NULL, 'cash', 'report_date', 'desc');

-- 📅 1년 (year)
CALL sp_get_sales_summary_year(3, '2025-01-01', 'cash', '', 'desc');

-- 📅 커스텀 기간 (custom)
CALL sp_get_sales_summary_range(3, 'custom', '2025-01-01', '2025-03-20', 'cash', 'report_date', 'desc');

-- 전체 매출
-- 📅 하루 (day)
CALL sp_get_sales_summary_range(3, 'day', '2025-03-20', NULL, 'total', 'report_date', 'desc');

-- 📅 한달 (month)
CALL sp_get_sales_summary_range(3, 'month', '2025-03-01', NULL, 'total', 'report_date', 'desc');

-- 📅 1년 (year)
CALL sp_get_sales_summary_year(3, '2025-01-01', 'total', '', 'asc');

-- 📅 커스텀 기간 (custom)
CALL sp_get_sales_summary_range(3, 'custom', '2025-01-01', '2025-03-20', 'total', 'report_date', 'asc');

ALTER EVENT daily_store_sales_summary DISABLE;
ALTER EVENT daily_store_sales_summary ENABLE;

show triggers;
DROP TRIGGER IF EXISTS trg_offline_payment_status_update;
DROP TRIGGER IF EXISTS trg_warehouse_order_status_update;
DROP TRIGGER IF EXISTS trg_store_order_status_update;
DROP TRIGGER IF EXISTS trg_order_cancel_sync;
DROP TRIGGER IF EXISTS trg_validate_employee_role_update;

SELECT 
    esa.employee_id,
    e.name AS employee_name,
    e.role,
    esa.store_id,
    s.name AS store_name,
    esa.assigned_at,
    DATEDIFF(CURDATE(), esa.assigned_at) AS days_worked
FROM Employee_Store_Assignments esa
JOIN Employees e ON esa.employee_id = e.employee_id
JOIN Stores s ON esa.store_id = s.store_id
WHERE esa.status = '근무 중'
ORDER BY days_worked DESC;

SELECT 
    esa.store_id,
    s.name AS store_name,
    COUNT(*) AS 직원수,
    ROUND(AVG(
        DATEDIFF(
            IFNULL(esa.ended_at, CURDATE()),
            esa.assigned_at
        )
    )) AS 평균_근속일
FROM Employee_Store_Assignments esa
JOIN Stores s ON esa.store_id = s.store_id
GROUP BY esa.store_id, s.name
ORDER BY 평균_근속일 DESC;

DROP PROCEDURE sp_insight_assignment_diff;
-- 특정 정책 도입 전후 인력 분포 비교
DELIMITER //

CREATE PROCEDURE sp_insight_assignment_diff (
    IN p_store_id BIGINT,
    IN p_ref_date DATE
)
BEGIN
    IF p_store_id IS NULL THEN
        -- ✅ 모든 매장 조회
        SELECT
            s.store_id AS `매장 ID`,
            s.name AS `매장명`,

            COUNT(CASE 
                WHEN esa.assigned_at <= p_ref_date 
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date) 
                THEN 1 END) AS `기준일 당시 재직 인원`,

            COUNT(CASE 
                WHEN esa.assigned_at > p_ref_date 
                THEN 1 END) AS `기준일 이후 신규 배정 인원`,

            COUNT(CASE 
                WHEN esa.ended_at IS NOT NULL AND esa.ended_at > p_ref_date 
                THEN 1 END) AS `기준일 이후 퇴직 인원`,

            (
                COUNT(CASE 
                    WHEN esa.assigned_at > p_ref_date THEN 1 END)
                -
                COUNT(CASE 
                    WHEN esa.ended_at IS NOT NULL AND esa.ended_at > p_ref_date THEN 1 END)
            ) AS `순 인원 변화`

        FROM Stores s
        LEFT JOIN Employee_Store_Assignments esa ON s.store_id = esa.store_id
        GROUP BY s.store_id, s.name;

    ELSE
        -- ✅ 특정 매장만 조회
        SELECT
            s.store_id AS `매장 ID`,
            s.name AS `매장명`,

            COUNT(CASE 
                WHEN esa.assigned_at <= p_ref_date 
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date) 
                THEN 1 END) AS `기준일 당시 재직 인원`,

            COUNT(CASE 
                WHEN esa.assigned_at > p_ref_date 
                THEN 1 END) AS `기준일 이후 신규 배정 인원`,

            COUNT(CASE 
                WHEN esa.ended_at IS NOT NULL AND esa.ended_at > p_ref_date 
                THEN 1 END) AS `기준일 이후 퇴직 인원`,

            (
                COUNT(CASE 
                    WHEN esa.assigned_at > p_ref_date THEN 1 END)
                -
                COUNT(CASE 
                    WHEN esa.ended_at IS NOT NULL AND esa.ended_at > p_ref_date THEN 1 END)
            ) AS `순 인원 변화`

        FROM Stores s
        LEFT JOIN Employee_Store_Assignments esa ON s.store_id = esa.store_id
        WHERE s.store_id = p_store_id
        GROUP BY s.store_id, s.name;
    END IF;
END //

DELIMITER ;


CALL sp_insight_assignment_diff(3, '2025-01-01');
CALL sp_insight_assignment_diff(null, '2025-01-01');

drop procedure sp_admin_assignment_summary;
-- 관리자별 인사관리 현황 비교
DELIMITER //

CREATE PROCEDURE sp_admin_assignment_summary (
    IN p_ref_date DATE
)
BEGIN
    SELECT
        e.employee_id AS supervisor_id,
        e.name AS supervisor_name,
        s.store_id,
        s.name AS store_name,
        COUNT(esa.assignment_id) AS total_assignments,
        SUM(CASE 
            WHEN esa.assigned_at <= p_ref_date AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date) 
            THEN 1 ELSE 0 END) AS current_employees,
        SUM(CASE 
            WHEN esa.ended_at <= p_ref_date THEN 1 ELSE 0 END) AS retired_employees,
        ROUND(AVG(
            DATEDIFF(
                IFNULL(esa.ended_at, p_ref_date),
                esa.assigned_at
            )
        )) AS avg_days_assigned
    FROM Stores s
    JOIN Employees e ON s.manager_id = e.employee_id AND e.is_supervisor = TRUE
    LEFT JOIN Employee_Store_Assignments esa ON esa.store_id = s.store_id
    GROUP BY e.employee_id, e.name, s.store_id, s.name
    ORDER BY current_employees DESC;
END //

DELIMITER ;

CALL sp_admin_assignment_summary('2025-04-01');

DROP PROCEDURE sp_insight_assignment_tenure;
-- 근속 기간 분포 통계
DELIMITER //

CREATE PROCEDURE sp_insight_assignment_tenure (
    IN p_store_id BIGINT,
    IN p_ref_date DATE
)
BEGIN
    IF p_store_id IS NULL THEN
        -- 전체 매장
        SELECT
            s.store_id AS `매장 ID`,
            s.name AS `매장명`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) < 1 
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date) 
                THEN 1 END) AS `0~1년 미만`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) >= 1 
                     AND TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) < 3
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date)
                THEN 1 END) AS `1~3년 미만`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) >= 3
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date)
                THEN 1 END) AS `3년 이상`
        FROM Stores s
        LEFT JOIN Employee_Store_Assignments esa ON s.store_id = esa.store_id
        GROUP BY s.store_id, s.name;

    ELSE
        -- 특정 매장
        SELECT
            s.store_id AS `매장 ID`,
            s.name AS `매장명`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) < 1 
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date) 
                THEN 1 END) AS `0~1년 미만`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) >= 1 
                     AND TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) < 3
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date)
                THEN 1 END) AS `1~3년 미만`,
            COUNT(CASE 
                WHEN TIMESTAMPDIFF(YEAR, esa.assigned_at, p_ref_date) >= 3
                     AND (esa.ended_at IS NULL OR esa.ended_at > p_ref_date)
                THEN 1 END) AS `3년 이상`
        FROM Stores s
        LEFT JOIN Employee_Store_Assignments esa ON s.store_id = esa.store_id
        WHERE s.store_id = p_store_id
        GROUP BY s.store_id, s.name;
    END IF;
END //

DELIMITER ;

-- 전체 매장 근속 통계 (2025년 3월 기준)
CALL sp_insight_assignment_tenure(NULL, '2025-03-01');

-- 특정 매장 근속 통계
CALL sp_insight_assignment_tenure(2, '2025-03-01');

-- 매장 발주 흐름 추적

DELIMITER //

CREATE PROCEDURE sp_get_order_flow_history (
    IN p_store_id BIGINT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        sor.request_id AS 요청ID,
        s.name AS 매장명,
        e1.name AS 요청자,
        e2.name AS 승인자,
        sor.reason AS 발주사유,
        sor.status AS 최종상태,
        sor.created_at AS 요청일자,
        sor.updated_at AS 수정일자,
        sol.status AS 상태이력,
        sol.changed_at AS 변경일자
    FROM store_order_requests sor
    JOIN store_order_logs sol ON sor.request_id = sol.request_id
    JOIN stores s ON sor.store_id = s.store_id
    LEFT JOIN employees e1 ON sor.requested_by = e1.employee_id
    LEFT JOIN employees e2 ON sor.approved_by = e2.employee_id
    WHERE (p_store_id IS NULL OR sor.store_id = p_store_id)
      AND sol.changed_at BETWEEN p_start_date AND p_end_date
    ORDER BY sol.changed_at ASC;
END //

DELIMITER ;

CALL sp_get_order_flow_history(NULL, '2024-11-01', '2025-04-05');
-- 전체 매장 발주 흐름 조회

CALL sp_get_order_flow_history(3, '2025-01-01', '2025-03-31');
-- 특정 매장 발주 흐름 조회