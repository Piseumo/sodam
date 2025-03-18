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
    CONCAT(FORMAT(COALESCE(c.total_card_sales, 0), 0), '원') AS total_card_sales,
    CONCAT(FORMAT(COALESCE(ca.total_cash_sales, 0), 0), '원') AS total_cash_sales,
    CONCAT(FORMAT((COALESCE(c.total_card_sales, 0) + COALESCE(ca.total_cash_sales, 0)), 0), '원') AS total_sales,
    GREATEST(
        COALESCE(c.last_payment_date, '1900-01-01'),
        COALESCE(ca.last_payment_date, '1900-01-01')
    ) AS last_payment_date
FROM Stores s
LEFT JOIN (
    SELECT store_id, SUM(total_card_sales) AS total_card_sales, MAX(last_payment_date) AS last_payment_date
    FROM Store_Sales_Report_Card
    GROUP BY store_id
) c ON s.store_id = c.store_id
LEFT JOIN (
    SELECT store_id, SUM(total_cash_sales) AS total_cash_sales, MAX(last_payment_date) AS last_payment_date
    FROM Store_Sales_Report_Cash
    GROUP BY store_id
) ca ON s.store_id = ca.store_id;



drop procedure sp_store_sales;
-- ✅ 매장 매출 통계 프로시저 (카드 + 현금 + 순수 매출)
DELIMITER $$
CREATE PROCEDURE sp_store_sales(
    IN p_store_id BIGINT,
    IN p_search_type VARCHAR(10), -- day, month, year, custom
    IN p_payment_method VARCHAR(10), -- 'card', 'cash', 'all'
    IN p_start_date DATE,
    IN p_end_date DATE -- custom일 때만 사용, 나머지는 NULL 가능
)
BEGIN
    -- 날짜 포맷 지정
    DECLARE date_condition VARCHAR(100);

    -- 날짜 조건 생성
    IF p_search_type = 'day' THEN
        SET date_condition = CONCAT('DATE(pay_date) = "', p_start_date, '"');
    ELSEIF p_search_type = 'month' THEN
        SET date_condition = CONCAT('DATE_FORMAT(pay_date, "%Y-%m") = "', DATE_FORMAT(p_start_date, "%Y-%m"), '"');
    ELSEIF p_search_type = 'year' THEN
        SET date_condition = CONCAT('YEAR(pay_date) = "', YEAR(p_start_date), '"');
    ELSEIF p_search_type = 'custom' THEN
        SET date_condition = CONCAT('DATE(pay_date) BETWEEN "', p_start_date, '" AND "', p_end_date, '"');
    END IF;

  -- 메인 쿼리
SET @query = CONCAT(
    'SELECT 
        s.name AS 매장_이름,
        CASE WHEN ''', p_search_type, ''' = ''year'' THEN DATE_FORMAT(pay_date, "%Y-%m") ELSE DATE(pay_date) END AS 결제일,
        FORMAT(SUM(CASE WHEN method = ''card'' THEN amount ELSE 0 END), 0) AS 카드_매출,
        FORMAT(SUM(CASE WHEN method = ''cash'' THEN amount ELSE 0 END), 0) AS 현금_매출,
        FORMAT(SUM(amount), 0) AS 총_매출,
        FORMAT(SUM(point_used), 0) AS 포인트_사용_금액,
        FORMAT(SUM(discount_amount), 0) AS 할인_금액,
        FORMAT(SUM(amount) - SUM(point_used) - SUM(discount_amount), 0) AS 순수_매출
    FROM (
        SELECT 
            si.store_id, oc.pay_date, ''cash'' AS method, oc.amount, p.delta AS point_used, (ocp.price - pp.final_price) AS discount_amount
        FROM offline_cash oc
        JOIN Offline_Order oo ON oc.order_id = oo.order_id
        JOIN Point p ON oo.point_id = p.point_id
        JOIN Offline_Cart ocart ON oo.offline_cart_id = ocart.offline_cart_id
        JOIN Offline_Cart_Product ocp ON ocart.offline_cart_id = ocp.offline_cart_id
        JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
        JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
        WHERE oc.status = ''COMPLETE''

        UNION ALL

        SELECT 
            si.store_id, op.paid_at AS pay_date, ''card'' AS method, op.amount, p.delta AS point_used, (ocp.price - pp.final_price) AS discount_amount
        FROM Offline_Payment op
        JOIN Offline_Order oo ON op.order_id = oo.order_id
        JOIN Point p ON oo.point_id = p.point_id
        JOIN Offline_Cart ocart ON oo.offline_cart_id = ocart.offline_cart_id
        JOIN Offline_Cart_Product ocp ON ocart.offline_cart_id = ocp.offline_cart_id
        JOIN Store_Inventory si ON ocp.inventory_id = si.inventory_id
        JOIN Product_Price pp ON ocp.inventory_id = si.inventory_id
        WHERE op.status = ''paid''
    ) AS sales
    JOIN Stores s ON sales.store_id = s.store_id
    WHERE sales.store_id = ', p_store_id, 
    ' AND ', date_condition
);


    -- 결제수단 필터 추가
    IF p_payment_method <> 'all' THEN
        SET @query = CONCAT(@query, ' AND sales.method = "', p_payment_method, '"');
    END IF;

    -- 그룹화 및 정렬
    SET @query = CONCAT(@query, ' GROUP BY sales.store_id, 결제일 ORDER BY 결제일');

    -- 디버깅용 출력 (옵션)
    -- SELECT @query;

    -- 실행
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END $$
DELIMITER ;


CALL sp_store_sales(3, 'day', 'all', '2025-03-17', NULL);
CALL sp_store_sales(3, 'month', 'cash', '2025-03-01', NULL);
CALL sp_store_sales(3, 'custom', 'all', '2025-03-01', '2025-03-17');