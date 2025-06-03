import os
from fastapi import HTTPException
import mysql.connector
from dotenv import load_dotenv
import time
import logging
from typing import Optional
from mysql.connector import Error
import uuid
import random 

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures"""
    pass

# Database connection settings
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "port": os.getenv("MYSQL_PORT"),
    # "ssl_ca": os.getenv('MYSQL_SSL_CA'),
    # "ssl_verify_identity": True
}


def generate_serial_number() -> str:
    """Generate a unique serial number."""
    return f"MH-{uuid.uuid4().hex[:8].upper()}"

def get_db_connection(
    max_retries: int = 12,  # 12 retries = 1 minute total (12 * 5 seconds)
    retry_delay: int = 5,  # 5 seconds between retries
) -> mysql.connector.MySQLConnection:
    """Create database connection with retry mechanism."""
    connection: Optional[mysql.connector.MySQLConnection] = None
    attempt = 1
    last_error = None

    while attempt <= max_retries:
        try:
            connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                port=DB_CONFIG["port"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                # ssl_ca=DB_CONFIG["ssl_ca"],
                # ssl_verify_identity=True
            )

            # Test the connection
            connection.ping(reconnect=True, attempts=1, delay=0)
            logger.info("Database connection established successfully")
            return connection

        except Error as err:
            last_error = err
            logger.warning(
                f"Connection attempt {attempt}/{max_retries} failed: {err}. "
                f"Retrying in {retry_delay} seconds..."
            )

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

            if attempt == max_retries:
                break

            time.sleep(retry_delay)
            attempt += 1

    raise DatabaseConnectionError(
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
    
async def setup_database(initial_users: dict = None, initial_user_devices: dict = None, initial_devices: dict = None, initial_data: dict = None):
    """Creates user and session tables and populates initial user data if provided."""
    connection = None
    cursor = None

    # Define table schemas
    table_schemas = {
        "users": """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                serial_num VARCHAR(255) UNIQUE DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "sessions": """
            CREATE TABLE sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        "devices": """
            CREATE TABLE devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) DEFAULT NULL,
                serial_num VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        """,
        "data": """
            CREATE TABLE data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                serial_num VARCHAR(255) NOT NULL,
                avgHR INT DEFAULT NULL,
                avgSpO2 INT DEFAULT NULL,
                weight INT DEFAULT NULL,
                bpS INT DEFAULT NULL,
                bpD INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    }

    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if tables already exist and clear sessions only if they do
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        if all(table in existing_tables for table in table_schemas.keys()):
            logger.info("Tables already exist. Clearing sessions table...")
            cursor.execute("DELETE FROM sessions")
            connection.commit()
            return
        else:
            logger.info("Tables do not exist. Proceeding to drop and recreate tables...")
            
        # Recreate tables one by one
        for table_name, create_query in table_schemas.items():
            try:
                # Create table
                logger.info(f"Creating table {table_name}...")
                cursor.execute(create_query)
                connection.commit()
                logger.info(f"Table {table_name} created successfully")

            except Error as e:
                logger.error(f"Error creating table {table_name}: {e}")
                raise

        # Insert initial users if provided
        if initial_users:
            try:
                insert_query = "INSERT INTO users (first_name, last_name, email, username, password, serial_num) VALUES (%s, %s, %s, %s, %s, %s)"
                for username, (first_name, last_name, email, username, password, serial_num) in initial_users.items():
                    cursor.execute(insert_query, (first_name, last_name, email, username, password, serial_num))
                connection.commit()
                logger.info(f"Inserted {len(initial_users)} initial users")
            except Error as e:
                logger.error(f"Error inserting initial users: {e}")
                raise
        
        if initial_user_devices:
            try:
                insert_query = "INSERT INTO devices (username, serial_num) VALUES (%s, %s)"
                for username, serial in initial_user_devices:
                    cursor.execute(insert_query, (username, serial))
                connection.commit()
                logger.info(f"Inserted {len(initial_user_devices)} preloaded devices with users")
            except Error as e:
                logger.error(f"Error inserting initial devices: {e}")
                raise
            
        if initial_devices:
            try:
                insert_query = "INSERT INTO devices (serial_num) VALUES (%s)"
                for serial in initial_devices:
                    cursor.execute(insert_query, (serial,))
                connection.commit()
                logger.info(f"Inserted {len(initial_devices)} preloaded devices without users")
            except Error as e:
                logger.error(f"Error inserting initial devices: {e}")
                raise
        
        initial_data = True; 
        if initial_data: 
            try:
                print("Adding data !"); 
                insert_query = """
                INSERT INTO data (username, serial_num, avgHR, avgSpO2, weight, bpS, bpD) VALUES ("alice", "MH-830B35DF", %s, %s, %s, %s, %s); 
                """; 

                for i in range(7): 
                    rand_avgHR = random.randrange(60, 100); 
                    rand_avgSpO2 = random.randrange(95, 100); 
                    rand_weight = random.randrange(150, 155); 
                    rand_bpS = random.randrange(115, 120); 
                    rand_bpD = random.randrange(75, 80); 
                    
                    cursor.execute(insert_query, (rand_avgHR, rand_avgSpO2, rand_weight, rand_bpS, rand_bpD)); 
            
                connection.commit(); 

            except Error as e:
                logger.error(f"Error inserting initial data: {e}")
                raise


    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")

# Database utility functions for user and session management
async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Retrieve user from database by username.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Retrieve user from database by ID.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_user_by_serial_num(serial_num: str) -> Optional[dict]:
    """
    Retrieve user from database by device serial number.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE serial_num = %s", (serial_num,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_device_by_username(username: str) -> Optional[dict]:
    """
    Retrieve device from database by username.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE username = %s", (username,))
        print("success")
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close() 

async def get_device_by_serial_num(serial_num: str) -> Optional[dict]:        
    """
    Retrieve device from database by device mac.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE serial_num = %s", (serial_num,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
def get_unassigned_serial(cursor) -> Optional[str]:
    cursor.execute("SELECT serial_num FROM devices WHERE username IS NULL LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else None

async def create_user(username: str, first_name: str, last_name: str, email: str, password: str) -> Optional[int]:
    """
    Create a new user in the database and assign an available device serial number if available.

    Returns:
        int: The ID of the newly created user
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch an available unassigned serial number
        cursor.execute("SELECT serial_num FROM devices WHERE username IS NULL LIMIT 1")
        serial_result = cursor.fetchone()
        serial_num = serial_result[0] if serial_result else None
        
        if not serial_num:
            raise HTTPException(status_code=500, detail="No available device to assign.")

        # Insert the user with the serial number if available
        insert_query = """
            INSERT INTO users (first_name, last_name, email, username, password, serial_num)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (first_name, last_name, email, username, password, serial_num))
        connection.commit()
        user_id = cursor.lastrowid
        logger.info(f"User {username} created successfully with serial number {serial_num}")

        # Update the devices table to assign the serial number to the user
        if serial_num:
            cursor.execute(
                "UPDATE devices SET username = %s WHERE serial_num = %s", (username, serial_num)
            )
            connection.commit()

        return user_id

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
async def create_device(username: str, serial_num: str) -> Optional[int]:
    """
    Create a new device in the database.

    Args:
        username (str): The username of the user registered with the device
        serial_num (str): The mac address of the new device

    Returns:
        int: The ID of the newly registered device
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO devices (username, serial_num) VALUES (%s, %s)", (username, serial_num)
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
async def delete_device(device_id: int) -> None:
    """
    Delete a device from the database given the device id.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM devices WHERE id = %s", (device_id,)
        )
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def create_session(user_id: int, session_id: str) -> bool:
    """
    Create a new session in the database.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id) VALUES (%s, %s)", (session_id, user_id)
        )
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve session from database.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT *
            FROM sessions s
            WHERE s.id = %s
            
        """,
            (session_id,),
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def delete_session(session_id: str) -> bool:
    """
    Delete a session from the database.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

async def add_data_to_user(username: str, data: dict) -> bool:
    """
    Add additional data to a user in the database.
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO data (user_name, serial_num, avgHR, avgSpO2, weight, bpS, bpD)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                username,
                data.get("serial_num"),
                data.get("avgHR"),
                data.get("avgSpO2"),
                data.get("weight"),
                data.get("bpS"),
                data.get("bpD"),
            ),
        )
        connection.commit()
        return True
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def get_data_from_user(username: str):
    """
    Get data for a user from the database 
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection(); 
        cursor = connection.cursor(); 
        cursor.execute("SELECT avgHR, avgSpO2, weight, bpS, bpD from data where username = %s;", (username,)); 

        return cursor.fetchall(); 

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
