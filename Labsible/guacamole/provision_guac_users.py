import os
from dotenv import load_dotenv
import mysql.connector
import csv

## Creates users and connections based on csv file of the format
## username,password,connection,hostname

# Load environment variables from a .env file
load_dotenv()

def get_db_config():
    """Read database config from environment variables."""
    return {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }

def connect_to_db():
    """Establishes a database connection and returns the connection object."""
    db_config = get_db_config()

    try:
        # Attempt to establish a connection
        conn = mysql.connector.connect(**db_config)

        if conn.is_connected():
            print("Database connection successful.")
            return conn
        else:
            print("Database connection failed.")
            return None

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def guacamole_user_exists(conn, username):
    """Checks if a Guacamole user exists in the database.

    Args:
        conn (mysql.connector.connection.MySQLConnection): Active database connection.
        username (str): The username to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    try:
        cursor = conn.cursor()

        # Query to check if the user exists in guacamole_entity
        cursor.execute("""
            SELECT COUNT(*) FROM guacamole_entity 
            WHERE name = %s AND type = 'USER'
        """, (username,))

        result = cursor.fetchone()[0]

        return result > 0  # True if user exists, False otherwise

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False  # Assume the user doesn't exist in case of an error

    finally:
        cursor.close()  # Ensure the cursor is closed

def create_guacamole_user(conn, username, password):
    """Creates a new Guacamole user if they do not already exist."""
    try:
        cursor = conn.cursor()

        # Check if the user already exists
        if guacamole_user_exists(conn, username):
            print(f"User '{username}' already exists. Skipping creation.")
            return False

        # Generate salt and create user
        cursor.execute("SET @salt = UNHEX(SHA2(UUID(), 256));")

        cursor.execute("""
            INSERT INTO guacamole_entity (name, type)
            VALUES (%s, 'USER')
        """, (username,))

        cursor.execute("""
            INSERT INTO guacamole_user (
                entity_id,
                password_salt,
                password_hash,
                password_date
            )
            SELECT
                entity_id,
                @salt,
                UNHEX(SHA2(CONCAT(%s, HEX(@salt)), 256)),
                CURRENT_TIMESTAMP
            FROM guacamole_entity
            WHERE
                name = %s
                AND type = 'USER'
        """, (password, username))

        conn.commit()
        print(f"User '{username}' successfully created.")
        return True

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        conn.rollback()
        return False

    finally:
        cursor.close()

def create_guacamole_connection(conn, username, connection_name, hostname, protocol="rdp", port="3389"):
    """Creates a Guacamole connection for a user if the user exists.

    Args:
        conn (mysql.connector.connection.MySQLConnection): Active database connection.
        username (str): The username to associate with the connection.
        connection_name (str): Name of the Guacamole connection.
        hostname (str): The remote server hostname.
        protocol (str, optional): The protocol type (default: 'rdp').
        port (str, optional): The connection port (default: '3389').

    Returns:
        bool: True if the connection was created, False if the user does not exist or an error occurred.
    """
    try:
        cursor = conn.cursor()

        # Check if the user exists
        if not guacamole_user_exists(conn, username):
            print(f"User '{username}' does not exist. Cannot create connection.")
            return False

        # Get the entity_id of the user
        cursor.execute("""
            SELECT entity_id FROM guacamole_entity WHERE name = %s AND type = 'USER'
        """, (username,))
        entity_id = cursor.fetchone()[0]

        # Insert connection into guacamole_connection
        cursor.execute("""
            INSERT INTO guacamole_connection (connection_name, protocol)
            VALUES (%s, %s)
        """, (connection_name, protocol))

        # Retrieve connection_id of the newly created connection
        cursor.execute("""
            SELECT connection_id FROM guacamole_connection 
            WHERE connection_name = %s AND parent_id IS NULL
        """, (connection_name,))
        connection_id = cursor.fetchone()[0]

        # Insert connection parameters (hostname and port)
        cursor.execute("""
            INSERT INTO guacamole_connection_parameter (connection_id, parameter_name, parameter_value)
            VALUES (%s, 'hostname', %s), (%s, 'port', %s)
        """, (connection_id, hostname, connection_id, port))

        # Assign connection to the user (READ permission)
        cursor.execute("""
            INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
            VALUES (%s, %s, 'READ')
        """, (entity_id, connection_id))

        # Commit changes
        conn.commit()
        print(f"Connection '{connection_name}' (protocol: {protocol}, port: {port}) created for user '{username}'.")
        return True

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        conn.rollback()  # Rollback changes on failure
        return False

    finally:
        cursor.close()  # Ensure cursor is closed

def read_csv(filename):
    """Read user and connection details from a CSV file."""
    data = []
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

## Main Program ##
conn = connect_to_db()

if conn:
    csv_file = "guacamole_users.csv"
    user_data = read_csv(csv_file)
    
    for entry in user_data:
        username = entry["username"]
        password = entry["password"]
        connection = entry["connection"]
        hostname = entry["hostname"]
        
        if create_guacamole_user(conn, username, password):
            print(f"User '{username}' created.")
        else:
            print(f"User '{username}' create error!")
        
        if create_guacamole_connection(conn, username, connection, hostname):
            print(f"Connection '{connection}' created.")   
        else:
            print(f"Connection '{connection}' create error!")
    
conn.close()  # Close the database connection
conn.disconnect()
