import os

from flask import Flask, jsonify, request
import mysql.connector
import re
import xmltodict
import json
import jsonschema
from jsonschema import validate
import textwrap

app = Flask(__name__)
app.secret_key = "zb#f8!_wj8aiwjpfh*w%=_!+*fkvvcki(3c9(18a+!4mxhdkd"  #Secret key for session - random string

try:
    aisDB = mysql.connector.connect(  #Connect to the database
    host="localhost",
    user="root",
    passwd="",
    database="theflyingdutchman",
    auth_plugin='mysql_native_password'
    )
    sqlcursor = aisDB.cursor()
except:
    print("Error connecting to database")
    exit()


encodeVocabulary = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVW`abcdefghijklmnopqrstuvw"  #Vocabulary for encoding of AIS messages


def decreaseLimit(apiKey):  #Function to decrease the API limit of specified user
    #SQL Procedure to decrease the API limit
    sqlcursor.execute("CALL decreaseApiLimit(%s)", (apiKey,))
    aisDB.commit()


def checkApiLimit(apiKey):  #Checks if the API limit is exceeded
    if apiKey == None:
        return jsonify({"error": "API Key not specified"})
    #Call SQL procedure to check if the API limit is exceeded
    sqlcursor.execute("CALL getApiLimitByApiKey(%s)", (apiKey,))
    aisDB.commit()
    apiLimit = sqlcursor.fetchone()
    if apiLimit is None:
        return jsonify({"error": "API Key not found"})
    elif apiLimit[0] <= 0:
        return jsonify({"error": "API Limit exceeded"})
    else:
        return None


def sanitizeInput(input):  #Sanitize input strings
    filtered = re.sub('[^a-zA-Z0-9_\s]', '', input)
    return filtered


def get_json_schema(request):  #Loads in the JSON scheme against which the request data is validated
    with open(request + '.json', 'r') as file:
        schema = json.load(file)
    return schema


def validate_json(json_data, request):  #Validates the JSON against the JSON scheme
    execute_api_schema = get_json_schema(request)
    try:
        validate(instance=json_data, schema=execute_api_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    except jsonschema.exceptions.SchemaError as err:
        print(err)
        return False
    return True


def encodeAISBinary_1(mmsi, status, speed, long, lat, course, true_heading, ts):  #Encodes type 1 AIS messages
    _type = '{0:b}'.format(1).rjust(6, '0')  # 18
    _repeat = "00"  # repeat     (directive to an AIS transceiver that this message should be rebroadcast.)
    _mmsi = '{0:b}'.format(mmsi).rjust(30, '0')  # 30 bits (247320162)
    _status = '{0:b}'.format(status).rjust(4,'0')  # navigation status e.g. 0=Under way using engine, 1-At anchor, 5=Moored, 8=Sailing,15=undefined
    _rot = '{0:b}'.format(1).rjust(8, '0')  # rate of turn not defined
    _speed = '{0:b}'.format(int(round(speed))).rjust(10,'0')  # Speed over ground is in 1 1/10th-knot resolution from 0 to 102 knots. value 1023 indicates speed is not available, value 1022 indicates 102.2 knots or higher.
    _accurancy = '0'  # > 10m
    _long = '{0:b}'.format(int(round(long * 600000)) & 0b1111111111111111111111111111).rjust(28, '0')   #-180 to 180, 181 is unavaliable
    _lat = '{0:b}'.format(int(round(lat * 600000)) & 0b111111111111111111111111111).rjust(27, '0')      #-90 to 90, 91 is unavailable
    _course = '{0:b}'.format(int(round(course))).rjust(12,'0')  # 1 resolution. Course over ground will be 3600 (0xE10) if that data is not available.
    _true_heading = '{0:b}'.format(int(round(true_heading))).rjust(9, '0')  # 511 (N/A)
    _ts = '{0:b}'.format(ts).rjust(6, '0')  # Second of UTC timestamp.
    _flags = '0' * 6
    # '00': manufactor NaN
    # '000':  spare
    # '0': Raim flag
    _rstatus = '0' * 19
    # '11100000000000000110' : Radio status
    return _type + _repeat + _mmsi + _status + _rot + _speed + _accurancy + _lat + _long + _course + _true_heading + _ts + _flags + _rstatus


@app.route('/api/newShip', methods=['POST'])  #API endpoint for adding a new ship to the database
def newShip():
    def getShipByMMSI(mmsi):
        sqlcursor.execute("CALL getShipIdByMmsi(%s)", (mmsi,))
        shipID = sqlcursor.fetchone()
        return shipID

    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'newShip'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None: #Checks the API limit for the user
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    mmsi = sanitizeInput(str(request_data['ship']['mmsi']))
    nameOfShip = sanitizeInput(str(request_data['ship']['nameOfShip']))
    typeOfShip = sanitizeInput(str(request_data['ship']['typeOfShip']))

    if getShipByMMSI(mmsi) is not None:
        return jsonify({"error": "Ship already exists", "shipID": getShipByMMSI(mmsi)[0]}), 200

    if len(nameOfShip) > 20:
        remainingLength = 20
        newName = ""
        nameOfShip = nameOfShip.split()
        lastWord = nameOfShip[-1]
        lastWord = "_" + lastWord
        remainingLength -= len(lastWord)
        for word in nameOfShip:
            if len(word) < remainingLength:
                newName += (word + " ")
                remainingLength -= len(word) + 1
        newName += lastWord
        nameOfShip = newName


    sqlcursor.execute("CALL insertShipStatic(%s, %s, %s)", (mmsi, nameOfShip, typeOfShip))
    aisDB.commit()

    return jsonify({"success": "Ship added", "shipID": getShipByMMSI(mmsi)[0]}), 200


@app.route('/api/getShip', methods=['GET'])
def getShip():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'getShip'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    if 'ship' in request_data and 'shipID' in request_data['ship']:
        shipID = sanitizeInput(str(request_data['ship']['shipID']))
        
        sqlcursor.execute("CALL getShipByShipId(%s)", (shipID,))
        ship = sqlcursor.fetchone()
        if ship is None:
            return jsonify({"error": "Ship not found"}), 200
        else:
            return jsonify({"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2], "typeOfShip": ship[3]}), 200
    else:
        sqlcursor.execute("SELECT * FROM shipstatic;")
        ships = sqlcursor.fetchall()
        return jsonify({"ships": [{"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2], "typeOfShip": ship[3]} for
                                  ship in ships]}), 200


@app.route('/api/getApiLimit', methods=['GET'])
def getApiLimit():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'getApiLimit'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data

    userID = sanitizeInput(str(request_data['user']['userID']))
    
    #SQL Procedure to get the API limit for the user and userID
    sqlcursor.execute("CALL selectUserIdAndApiLimit(%s)", userID)
    apiLimit = sqlcursor.fetchone()
    if apiLimit is None:
        return jsonify({"error": "User not found"}), 200
    return jsonify({"userID": apiLimit[0], "apiLimit": apiLimit[1]}), 200


@app.route('/api/encodeAIS', methods=['GET'])
def encodeAIS():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'encodeAIS'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    mmsi = request_data['ship']['mmsi']
    status = request_data['AIS']['status']
    speed = request_data['AIS']['speed']
    longitude = request_data['AIS']['longitude']
    latitude = request_data['AIS']['latitude']
    course = request_data['AIS']['course']
    trueHeading = request_data['AIS']['trueHeading']
    timestamp = request_data['AIS']['timestamp']

    aisBinary = encodeAISBinary_1(mmsi, status, speed, longitude, latitude, course, trueHeading, timestamp)

    binaryArray = textwrap.wrap(aisBinary, 6)
    payload = ""
    for binary6Bit in binaryArray:
        decimal = int(binary6Bit, 2)
        payload += encodeVocabulary[decimal]
    return jsonify({"AISMessage": payload, "AISMessageBinary": aisBinary}), 200


@app.route('/api/decodeAIS', methods=['GET'])
def decodeAIS():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'decodeAIS'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    aisBinary = None
    if 'AIVDM' in request_data['AIS']:
        aivdmMessage = request_data['AIS']['AIVDM']
        if aivdmMessage.startswith('!AIVDM'):
            aivdmMessage = aivdmMessage.split(',')[5:6][0]
        binary = ""
        for char in aivdmMessage:
            index = encodeVocabulary.find(char)
            binary6Bit = '{0:b}'.format(index).rjust(6, '0')
            binary += binary6Bit
        aisBinary = binary
    else:
        aisBinary = request_data['AIS']['binary']

    type = int(aisBinary[0:6], 2)
    repeat = int(aisBinary[6:8], 2)
    mmsi = int(aisBinary[8:38], 2)
    status = int(aisBinary[38:42], 2)
    rot = int(aisBinary[42:50], 2)
    speed = int(aisBinary[50:60], 2)
    accurancy = int(aisBinary[60:61], 2)
    long = int(aisBinary[61:89], 2) / 600000
    lat = int(aisBinary[89:116], 2) / 600000
    course = int(aisBinary[116:128], 2)
    true_heading = int(aisBinary[128:137], 2)
    ts = int(aisBinary[137:143], 2)
    smi = int(aisBinary[143:145], 2)
    spare = int(aisBinary[145:148], 2)
    raim = int(aisBinary[148:149], 2)
    rstatus = int(aisBinary[149:], 2)
    response = [str(type), str(repeat), str(mmsi), str(status), str(rot), str(speed), str(accurancy), str(long),
                str(lat), str(course), str(true_heading), str(ts), str(smi), str(spare), str(raim), str(rstatus)]
    return jsonify({"AISMessage": {"Type": response[0], "Repeat": response[1], "MMSI": response[2],
                                   "Status": response[3], "RateOfTurn": response[4], "Speed": response[5],
                                   "Accuracy": response[6], "Longitude": response[7], "Latitude": response[8],
                                   "Course": response[9], "TrueHeading": response[10], "Timestamp": response[11],
                                   "SMI": response[12], "Spare": response[13], "Raim": response[14],
                                   "RStatus": response[15]}}), 200


@app.route('/api/getSpoofData', methods=['GET'])
def getSpoofData():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'getSpoofData'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    if 'request' in request_data and 'spoofID' in request_data['request']:
        spoofID = sanitizeInput(str(request_data['request']['spoofID']))
        sqlcursor.execute("CALL getRequestByRequestId(%s)", spoofID)
        spoofData = sqlcursor.fetchone()
        if spoofData is None:
            return jsonify({"error": "Spoof ID not found"}), 200
        else:
            return jsonify({"spoofData": {"requestID": spoofData[0], "userID": spoofData[1], "shipID": spoofData[2],
                                          "locationEPFS": spoofData[3], "longitude": spoofData[4],
                                          "latitude": spoofData[5], "timestamp": spoofData[6], "cog": spoofData[7],
                                          "sog": spoofData[8], "heading": spoofData[9], "rot": spoofData[10],
                                          "status": spoofData[11], "currentTime": spoofData[12]}}), 200
    else:
        sqlcursor.execute("SELECT * FROM requests;")
        spoofData = sqlcursor.fetchall()
        if spoofData is None:
            return jsonify({"error": "No spoof data found"}), 400
        else:
            return jsonify({"spoofData": [
                {"request_No": spoofData[i][0], "userID": spoofData[i][1], "shipID": spoofData[i][2],
                 "locationEPFS": spoofData[i][3], "longitude": spoofData[i][4], "latitude": spoofData[i][5],
                 "timestamp": spoofData[i][6], "cog": spoofData[i][7], "sog": spoofData[i][8],
                 "heading": spoofData[i][9], "rot": spoofData[i][10], "status": spoofData[i][11],
                 "currentTime": spoofData[i][12]} for i in range(len(spoofData))]}), 200


@app.route('/api/spoofShip', methods=['POST'])
def spoofShip():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'getSpoofData'):
        return jsonify({"error": "Invalid Request"}), 400

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))
    if checkApiLimit(apiKey) is not None:
        return checkApiLimit(apiKey).data
    else:
        decreaseLimit(apiKey)

    shipID = sanitizeInput(str(request_data['ship']['shipID']))
    longitude = sanitizeInput(str(request_data['AIS']['longitude']))
    latitude = sanitizeInput(str(request_data['AIS']['latitude']))
    timestamp = sanitizeInput(str(request_data['AIS']['timestamp']))
    course = sanitizeInput(str(request_data['AIS']['course']))
    speed = sanitizeInput(str(request_data['AIS']['speed']))
    heading = sanitizeInput(str(request_data['AIS']['heading']))
    rot = sanitizeInput(str(request_data['AIS']['rot']))
    status = sanitizeInput(str(request_data['AIS']['status']))

    sqlcursor.execute("CALL getMmsiByShipId(%s)", shipID)
    shipData = sqlcursor.fetchone()
    if shipData is None:
        return jsonify({"error": "Ship ID not found"}), 200
    else:
        mmsi = shipData[0]

    sqlcursor.execute("CALL getUserIdByApiKey(%s)", apiKey)
    userData = sqlcursor.fetchone()
    if userData is None:
        return jsonify({"error": "User not found"}), 200
    else:
        userID = userData[0]

    aisPayload = encodeAISBinary_1(mmsi, status, speed, longitude, latitude, course, heading, timestamp)

    try:
        os.system("AISTX.py -p " + str(aisPayload))
    except:
        return jsonify({"error": "AIS transmission failed"}), 500
    
    sqlcursor.execute("CALL insertRequest(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (userID, shipID, longitude, latitude, timestamp, course, speed, heading, rot, status))


app.run(host='127.0.0.1', port=1234)  # TODO: change this
