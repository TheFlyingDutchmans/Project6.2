import os
from flask import Flask, request
import configparser
from scripts import dbTools
from endpoints import decodeAIS1, encodeAIS1, getApiLimit, getShip, getSpoofData, newShip, spoofShip

cd = os.path.dirname(os.path.abspath(__file__))
secKey = configparser.ConfigParser() # Read the config file for the secret key
secKey.read(cd + '/config/secretKey.ini')
apiConfig = configparser.ConfigParser() # Read the config file for the API
apiConfig.read(cd + '/config/API.ini')

if not secKey.sections() or not apiConfig.sections():
    print('Missing or empty config file(s) for API')
    exit()

app = Flask(__name__)  # Initialize Flask app
app.secret_key = secKey['secKey']['key']

sqlCursor, aisDB = dbTools.connectToDB() # Connect to the database


if aisDB is None or sqlCursor is None:
    print("Error connecting to database")
    exit()

@app.route('/apiv3/ship', methods=['GET', 'POST', 'PUT'])
def ship():
    if request.method == 'GET':
        return getShip.getShip(request, sqlCursor, aisDB)
    elif request.method == 'POST' or request.method == 'PUT':
        return newShip.newShip(request, sqlCursor, aisDB)

@app.route('/apiv3/apiLimit', methods=['GET'])
def apiLimit():
    if request.method == 'GET':
        return getApiLimit.getApiLimit(request, sqlCursor, aisDB)

@app.route('/apiv3/encodeAIS', methods=['GET'])
def encodeAIS():
    if request.method == 'GET':
        return encodeAIS1.encode(request, sqlCursor, aisDB)

@app.route('/apiv3/decodeAIS', methods=['GET'])
def decodeAIS():
    if request.method == 'GET':
        return decodeAIS1.decode(request, sqlCursor, aisDB)

@app.route('/apiv3/spoof', methods=['GET', 'POST'])
def spoof():
    if request.method == 'GET':
        return getSpoofData.getSpoofData(request, sqlCursor, aisDB)
    elif request.method == 'POST':
        return spoofShip.spoofShip(request, sqlCursor, aisDB)

app.run(host=apiConfig['API']['host'], port=apiConfig['API']['port'], debug=apiConfig['API']['debug'])

