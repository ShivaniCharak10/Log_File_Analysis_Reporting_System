# db_handler.py
import mysql.connector
from mysql.connector import Error
import configparser
import logging

class DBHandler:
    def __init__(self, config_path="config.ini"):
        self.connection = None
        self.cursor = None
        self._connect(config_path)

    def _connect(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)

        try:
            self.connection = mysql.connector.connect(
                host=config['mysql']['host'],
                user=config['mysql']['user'],
                password=config['mysql']['password'],
                database=config['mysql']['database'],
                port=int(config['mysql'].get('port', 3306))
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                logging.info("Connected to MySQL database")
        except Error as e:
            logging.error(f"MySQL connection error: {e}")
            raise

    def get_cursor(self):
        if self.cursor is None or not self.connection.is_connected():
            logging.error("Cursor is not connected")
            raise Error("Cursor is not connected")
        return self.cursor

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

