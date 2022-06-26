import configparser
import mysql.connector
from flask import jsonify


def connectToDB(): # Connect to the database
    dbConfig = configparser.ConfigParser() # Read the config file
    dbConfig.read('config/dbConn.ini')

    if not dbConfig.sections(): # If the config file is empty
        print("Config file missing")
        exit()

    try:
        aisDB = mysql.connector.connect( # Connect to the database
            host=dbConfig['mysqlDB']['host'],
            user=dbConfig['mysqlDB']['user'],
            passwd=dbConfig['mysqlDB']['passwd'],
            database=dbConfig['mysqlDB']['db'],
            auth_plugin=dbConfig['mysqlDB']['auth_plugin']
        )
        sqlCursor = aisDB.cursor() # Create a cursor
        print('Connected to DB')
        return sqlCursor, aisDB
    except:
        print("Error connecting to database") # If the connection fails
        exit()


def decreaseApiLimit(apiKey, sqlCursor, aisDB): # Decrease the API limit of a specific user via API key by 1
    sqlCursor.execute(
        "UPDATE users SET apiLimit = apiLimit - 1 WHERE apiKey = '" + apiKey + "';")
    aisDB.commit()


def checkApiLimit(apiKey, sqlCursor): # Check if the API limit of a specific user via API key
    if apiKey == None:
        return jsonify({"error": "API Key not specified"})
    sqlCursor.execute(
        "SELECT apiLimit FROM users WHERE apiKey = '" + apiKey + "';")
    apiLimit = sqlCursor.fetchone()
    if apiLimit is None:
        return ['error', 'API key not found', '404']
    elif apiLimit[0] <= 0:
        return ['error', 'API limit exceeded', '429']
    else:
        return None


def getShipByMMSI(mmsi, sqlCursor):
    sqlCursor.execute("SELECT shipID FROM shipstatic WHERE mmsi = '" + mmsi + "';")
    shipID = sqlCursor.fetchone()
    return shipID
