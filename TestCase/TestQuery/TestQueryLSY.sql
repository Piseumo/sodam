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
        SET wi.quantity = wi.quantity + (NEW.total_amount - NEW.balance_amount) / ocp.price
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

CREATE VIEW Store_Sales_Report AS
SELECT 
    si.store_id AS 매장_ID,
    s.name AS 매장명,
    DATE(op.paid_at) AS 결제_일자,
    DATE_FORMAT(op.paid_at, '%Y-%m') AS 결제_월,
    YEAR(op.paid_at) AS 결제_연도,
    SUM(op.amount) AS 총_매출액,
    COUNT(DISTINCT oo.order_id) AS 총_판매_건수,
    SUM(CASE WHEN op.pay_method = '카드 결제' THEN op.amount ELSE 0 END) AS 카드_결제_매출,
    SUM(CASE WHEN op.pay_method = '현금 결제' THEN op.amount ELSE 0 END) AS 현금_결제_매출
FROM Offline_Payment op
JOIN Offline_Order oo ON op.order_id = oo.order_id
JOIN Offline_Cart oc ON oo.offline_cart_id = oc.offline_cart_id
JOIN Offline_Cart_Product ocp ON oc.offline_cart_id = ocp.offline_cart_id
JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
JOIN Stores s ON si.store_id = s.store_id
WHERE op.status = '결제 완료'
GROUP BY si.store_id, s.name, 결제_일자, 결제_월, 결제_연도;

-- 특정 매장 일별 매출 보고서 조회
SELECT * FROM Store_Sales_Report 
WHERE 결제_일자 = '2025-03-05' 
AND 매장_ID = 2;

-- 특정 매장 월별 매출 보고서 조회
SELECT * FROM Store_Sales_Report 
WHERE 결제_월 = '2025-03' 
AND 매장_ID = 2;

-- 특정 매장 연도별 매출 보고서 조회
SELECT * FROM Store_Sales_Report
WHERE 결제_연도 = '2025'
AND 매장_ID = 2;
