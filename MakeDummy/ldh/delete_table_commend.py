# ✅ (1) 기존 데이터 삭제 (TRUNCATE TABLE → AUTO_INCREMENT 초기화)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE Employees;")
cursor.execute("TRUNCATE TABLE Stores;")
cursor.execute("TRUNCATE TABLE Warehouses;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

print(" 기존 데이터 삭제 완료!")