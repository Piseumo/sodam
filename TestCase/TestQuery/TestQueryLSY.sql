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
    IN store_id BIGINT, 
    IN product_id BIGINT, 
    IN request_quantity INT
)
BEGIN
    DECLARE available_stock INT;
    DECLARE max_request INT;
    
    -- 해당 상품의 물류센터 총 재고량 조회
    SELECT quantity INTO available_stock
    FROM Warehouse_Inventory
    WHERE product_id = product_id;
    
    -- 신청 가능 최대 수량 (물류센터 재고의 10%)
    SET max_request = available_stock / 10;

    -- 신청 수량이 10% 제한을 초과하는지 확인
    IF request_quantity > max_request THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '신청 수량이 물류센터 재고의 10%를 초과할 수 없습니다.';
    ELSE
        -- Store_Order_Requests 테이블에 요청 삽입
        INSERT INTO Store_Order_Requests (store_id, status, created_at)
        VALUES (store_id, '요청', NOW());
        
        -- 방금 삽입된 request_id 가져오기
        SET @request_id = LAST_INSERT_ID();
        
        -- Store_Order_Details 테이블에 발주 상품 목록 삽입
        INSERT INTO Store_Order_Details (request_id, product_id, quantity, created_at)
        VALUES (@request_id, product_id, request_quantity, NOW());

        -- Store_Order_Logs 테이블에 기록 추가
        INSERT INTO Store_Order_Logs (request_id, status, changed_at)
        VALUES (@request_id, '요청', NOW());

        -- Warehouse_Orders_Requests 테이블에 출고 요청 삽입 (자동 처리)
        INSERT INTO Warehouse_Orders_Requests (warehouse_id, type, source, status, created_at)
        VALUES (1, '출고', '매장발주', '요청', NOW());

        -- 방금 삽입된 warehouse request_id 가져오기
        SET @warehouse_request_id = LAST_INSERT_ID();

        -- Warehouse_Orders_Log 테이블에 출고 요청 기록 추가
        INSERT INTO Warehouse_Orders_Log (request_id, status, changed_at)
        VALUES (@warehouse_request_id, '요청', NOW());

        -- Warehouse_Orders_Details 테이블에 제품 목록 추가
        INSERT INTO Warehouse_Orders_Details (request_id, product_id, quantity, created_at)
        VALUES (@warehouse_request_id, product_id, request_quantity, NOW());
    END IF;
END //

DELIMITER ;

CALL sp_request_store_order(2, 5, 15); -- store_id, product_id, quantity
