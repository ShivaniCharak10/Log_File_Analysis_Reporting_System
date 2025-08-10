CREATE DATABASE IF NOT EXISTS log_analyzer;
USE log_analyzer;

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    timestamp DATETIME,
    request_method VARCHAR(10),
    resource TEXT,
    status_code INT,
    response_size INT,
    request_time DATETIME,
    INDEX idx_ip_address (ip_address),
    INDEX idx_timestamp (timestamp),
    INDEX idx_status_code (status_code),
    INDEX idx_request_method (request_method)
);
