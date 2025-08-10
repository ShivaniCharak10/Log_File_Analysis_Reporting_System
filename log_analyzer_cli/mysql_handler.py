import mysql.connector
from mysql.connector import Error
from configparser import ConfigParser
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)

class MySQLHandler:
    def __init__(self, config_dict=None):
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
        
        if config_dict:
            self.config_dict = config_dict
        else:
            self.config_dict = self.load_config()
    
    def load_config(self):
        """Load database configuration from config.ini"""
        config = ConfigParser()
        config.read('config.ini')
        return {
            'host': config['mysql']['host'],
            'user': config['mysql']['user'],
            'password': config['mysql']['password'],
            'database': config['mysql']['database']
        }
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**self.config_dict)
            self.cursor = self.connection.cursor(dictionary=True)
            self.logger.info("Successfully connected to MySQL database")
            return True
        except Error as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("MySQL connection closed")
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Create database if it doesn't exist
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS log_analyzer")
            self.cursor.execute("USE log_analyzer")
            
            # Create logs table
            create_table_query = """
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
            )
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
            self.logger.info("Tables created successfully")
            
            # Create user_agents table
            create_user_agents_table_query = """
            CREATE TABLE IF NOT EXISTS user_agents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_agent_string TEXT,
                os VARCHAR(50),
                browser VARCHAR(50),
                device_type VARCHAR(50)
            )
            """
            self.cursor.execute(create_user_agents_table_query)
            self.connection.commit()
            self.logger.info("User agents table created successfully")
            
        except Error as e:
            self.logger.error(f"Error creating tables: {e}")
    
    def insert_log_entry(self, log_data):
        """Insert a single log entry into the database"""
        try:
            query = """
                INSERT INTO logs (ip_address, timestamp, request_method, resource, 
                                status_code, response_size, request_time)
                VALUES (%(ip_address)s, %(timestamp)s, %(request_method)s, %(resource)s,
                        %(status_code)s, %(response_size)s, %(request_time)s)
            """
            self.cursor.execute(query, log_data)
            self.connection.commit()
            self.logger.info("Log entry inserted successfully")
            return True
        except Error as e:
            self.logger.error(f"Error inserting log entry: {e}")
            return False
    
    def insert_log_entries_batch(self, log_entries):
        """Insert multiple log entries in batch"""
        try:
            query = """
                INSERT INTO logs (ip_address, timestamp, request_method, resource, 
                                status_code, response_size, request_time)
                VALUES (%(ip_address)s, %(timestamp)s, %(request_method)s, %(resource)s,
                        %(status_code)s, %(response_size)s, %(request_time)s)
            """
            self.cursor.executemany(query, log_entries)
            self.connection.commit()
            self.logger.info(f"Inserted {len(log_entries)} log entries")
            return True
        except Error as e:
            self.logger.error(f"Error inserting batch log entries: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_top_n_ips(self, n=10):
        """Get top N IP addresses by request count"""
        try:
            query = """
                SELECT ip_address, COUNT(*) as request_count
                FROM logs
                GROUP BY ip_address
                ORDER BY request_count DESC
                LIMIT %s
            """
            self.cursor.execute(query, (n,))
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching top IPs: {e}")
            return []
    
    def get_status_code_distribution(self):
        """Get distribution of HTTP status codes"""
        try:
            query = """
                SELECT status_code, COUNT(*) as count,
                       ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM logs)), 2) as percentage
                FROM logs
                GROUP BY status_code
                ORDER BY count DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching status code distribution: {e}")
            return []
    
    def get_hourly_traffic(self):
        """Get hourly traffic distribution"""
        try:
            query = """
                SELECT HOUR(timestamp) as hour, COUNT(*) as request_count
                FROM logs
                GROUP BY hour
                ORDER BY hour
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching hourly traffic: {e}")
            return []
    
    def get_daily_traffic(self, days=30):
        """Get daily traffic for the last N days"""
        try:
            query = """
                SELECT DATE(timestamp) as date, COUNT(*) as request_count
                FROM logs
                WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY date
                ORDER BY date
            """
            self.cursor.execute(query, (days,))
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching daily traffic: {e}")
            return []
    
    def get_resource_analysis(self, n=10):
        """Get top N requested resources"""
        try:
            query = """
                SELECT resource, COUNT(*) as request_count,
                       AVG(response_size) as avg_size
                FROM logs
                GROUP BY resource
                ORDER BY request_count DESC
                LIMIT %s
            """
            self.cursor.execute(query, (n,))
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching resource analysis: {e}")
            return []
    
    def get_error_analysis(self):
        """Get analysis of error status codes (4xx and 5xx)"""
        try:
            query = """
                SELECT status_code, COUNT(*) as error_count,
                       GROUP_CONCAT(DISTINCT resource LIMIT 3) as sample_resources
                FROM logs
                WHERE status_code >= 400
                GROUP BY status_code
                ORDER BY error_count DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching error analysis: {e}")
            return []
    
    def get_traffic_heatmap_data(self):
        """Get data for traffic heatmap (day of week vs hour)"""
        try:
            query = """
                SELECT DAYOFWEEK(timestamp) as day_of_week,
                       HOUR(timestamp) as hour,
                       COUNT(*) as request_count
                FROM logs
                GROUP BY day_of_week, hour
                ORDER BY day_of_week, hour
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error fetching heatmap data: {e}")
            return []
    
    def get_database_stats(self):
        """Get general database statistics"""
        try:
            stats = {}
            
            # Total records
            self.cursor.execute("SELECT COUNT(*) as total FROM logs")
            result = self.cursor.fetchone()
            stats['total_records'] = result['total'] if result else 0
            
            # Unique IPs
            self.cursor.execute("SELECT COUNT(DISTINCT ip_address) as unique_ips FROM logs")
            result = self.cursor.fetchone()
            stats['unique_ips'] = result['unique_ips'] if result else 0
            
            # Date range
            self.cursor.execute("SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM logs")
            result = self.cursor.fetchone()
            if result:
                stats['earliest_log'] = result['earliest']
                stats['latest_log'] = result['latest']
            
            return stats
        except Error as e:
            self.logger.error(f"Error fetching database stats: {e}")
            return {}
    
    # --- Internal helpers ---
    
    def _normalize_ts(self, dt: datetime) -> datetime:
        """
        Convert timezone-aware datetime to naive UTC for MySQL DATETIME.
        MySQL DATETIME has no timezone; we store UTC without tzinfo.
        """
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    
    def _get_or_insert_user_agent(self, ua: str | None):
        if not ua:
            return None

        self.cursor.execute(
            "SELECT id FROM user_agents WHERE user_agent_string = %s",
            (ua,)
        )
        row = self.cursor.fetchone()
        if row:
            return row['id']

        # very lightweight UA parsing (keep it simple; avoids extra deps)
        os_name = "Unknown OS"
        browser = "Unknown Browser"
        device = "Desktop"

        ua_lc = ua.lower()
        if "windows" in ua_lc:
            os_name = "Windows"
        elif "mac os" in ua_lc or "macintosh" in ua_lc:
            os_name = "macOS"
        elif "linux" in ua_lc:
            os_name = "Linux"
        elif "android" in ua_lc:
            os_name = "Android"
        elif "iphone" in ua_lc or "ios" in ua_lc:
            os_name = "iOS"

        if "chrome" in ua_lc and "safari" in ua_lc:
            browser = "Chrome"
        elif "firefox" in ua_lc:
            browser = "Firefox"
        elif "safari" in ua_lc and "chrome" not in ua_lc:
            browser = "Safari"
        elif "edge" in ua_lc:
            browser = "Edge"

        if "mobile" in ua_lc:
            device = "Mobile"
        elif "tablet" in ua_lc or "ipad" in ua_lc:
            device = "Tablet"

        self.cursor.execute(
            """
            INSERT INTO user_agents (user_agent_string, os, browser, device_type)
            VALUES (%s, %s, %s, %s)
            """,
            (ua, os_name, browser, device)
        )
        self.connection.commit()
        return self.cursor.lastrowid
