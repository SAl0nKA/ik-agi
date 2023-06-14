import configparser
import sys
from asterisk.agi import AGI
import mysql.connector
from mysql.connector import Error

CONFIG_NAME = 'db_config.ini'

def createconfigfile():
    file = open(CONFIG_NAME, 'w')
    file.write("[Database]\n"
               "host = localhost\n"
               "port = 3306\n"
               "user = myuser\n"
               "password = mypassword\n"
               "database = mydatabase\n")
    file.close()
    print("Config template created")


def loadconfig():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(CONFIG_NAME)

    # Retrieve values from the 'Database' section
    return {
            'host': config.get('Database', 'host'), 
            'port': config.get('Database', 'port'), 
            'user': config.get('Database', 'user'),
            'password': config.get('Database', 'password'),
            'database': config.get('Database', 'database')
            }


#potrebna kniznica
#pip install mysql-connector-python
def main():
    if len(sys.argv) < 2:
        print("Not enough arguments")
        return 
    
    if sys.argv[1] == "create":
        createconfigfile()
        return
    
    # Create an AGI instance
    agi = AGI()

    #connect to db
    try:
        # config = loadconfig()
        connection = mysql.connector.connect(
            **loadconfig()
            # host=config['host'],
            # database='your_database',
            # user='your_username',
            # password='your_password'
        )

        #db is not connected
        if not connection.is_connected():
            print('Not connected to MySQL database')
            agi.set_variable("MENO", sys.argv[1])
            return
        
        # Create a cursor
        cursor = connection.cursor()

        number = sys.argv[1]
        # Execute a SELECT query
        query = f"SELECT meno,priezvisko,izba FROM users where phone_number like '%{number[3:]}'"
        cursor.execute(query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        #nic sa nenaslo, ako meno sa pouzije caller id
        if len(rows) == 0:
            agi.set_variable("MENO", sys.argv[1])
            return

        meno = rows[0][0]
        priezvisko = rows[0][1]
        izba = rows[0][2]

        agi.set_variable("MENO", "{meno} {priezvisko}")
        agi.set_variable("IZBA", izba)
    except Error as e:
        print(f'Error connecting to MySQL database: {e}')
        agi.set_variable("MENO", sys.argv[1])
    finally:
        cursor.close()
        # Close the database connection
        if connection.is_connected():
            connection.close()
            print('Connection closed')

if __name__ == "__main__":
    main()