CREATE DATABASE IF NOT EXISTS soft_test_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE soft_test_db;

CREATE TABLE IF NOT EXISTS test_case_main (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_type VARCHAR(50) NOT NULL,
    group_num INT NOT NULL,
    case_title VARCHAR(200),
    case_content TEXT,
    generate_type INT DEFAULT 2,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS test_case_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    main_id INT NOT NULL,
    case_no VARCHAR(50),
    field_values JSON,
    scene_desc VARCHAR(500),
    case_type VARCHAR(50),
    expected_result VARCHAR(500),
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_main_id (main_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    operation_type VARCHAR(50),
    operation_desc VARCHAR(500),
    related_id INT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


TRUNCATE TABLE test_case_detail;
TRUNCATE TABLE test_case_main;
