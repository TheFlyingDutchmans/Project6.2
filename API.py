import os
from flask import Flask, jsonify, request
import mysql.connector
import re
import xmltodict
import json
import jsonschema
from jsonschema import validate
import textwrap
from os.path import exists

app = Flask(__name__)  # Initialize Flask app
app.secret_key = "zb#f8!_wj8aiwjpfh*w%=_!+*fkvvcki(3c9(18a+!4mxhdkd"  # Secret key for session - random string

try:
    aisDB = mysql.connector.connect(  # Connect to the database
        host="localhost",
        user="apiUser",
        passwd="securePassword",
        database="theflyingdutchman",
        auth_plugin='mysql_native_password'
    )
    sqlcursor = aisDB.cursor()  # Initialize cursor
except:
    print("Error connecting to database")  # Print error if database connection fails
    exit()  # Exit program if database connection fails

encodeVocabulary = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVW`abcdefghijklmnopqrstuvw"  # Vocabulary for encoding of AIS messages


def decreaseLimit(apiKey):  # Function to decrease the API limit of specified user
    sqlcursor.execute(
        "UPDATE users SET apiLimit = apiLimit - 1 WHERE apiKey = '" + apiKey + "';")  # Decrease the API limit of specified user
    aisDB.commit()


def checkApiLimit(apiKey):  # Checks if the API limit is exceeded
    if apiKey == None:
        return jsonify({"error": "API Key not specified"})
    sqlcursor.execute(
        "SELECT apiLimit FROM users WHERE apiKey = '" + apiKey + "';")  # Get apiLimit of user with specified apiKey
    apiLimit = sqlcursor.fetchone()  # Get the API limit of specified user
    if apiLimit is None:
        return jsonify({"error": "API Key not found"})  # Return error if API key is not found
    elif apiLimit[0] <= 0:
        return jsonify({"error": "API Limit exceeded"})  # Return error if API limit is exceeded
    else:
        return None  # Return None if API limit is not exceeded


def sanitizeInput(input):  # Sanitize input strings
    filtered = re.sub('[^a-zA-Z0-9_\s]', '', input)  # Remove all non-alphanumeric characters
    return filtered


def get_json_schema(request):  # Loads in the JSON scheme against which the request data is validated
    # Open the JSON schema file from JSON folder in same directory
    with open(request + '.json', 'r') as file:
        schema = json.load(file)
    return schema


def validate_json(json_data, request):  # Validates the JSON against the JSON scheme
    execute_api_schema = get_json_schema(
        request)  # Loads in the JSON scheme against which the request data is validated
    try:
        validate(instance=json_data, schema=execute_api_schema)  # Validates the JSON against the JSON scheme
    except jsonschema.exceptions.ValidationError as err:  # If the JSON is not valid, return error
        print(err)
        return False
    except jsonschema.exceptions.SchemaError as err:
        print(err)
        return False
    return True


def encodeAISBinary_1(mmsi, status, speed, lat, long, course, true_heading, ts):  # Encodes type 1 AIS messages
    _type = '{0:b}'.format(1).rjust(6, '0')  # 18
    _repeat = "00"  # repeat     (directive to an AIS transceiver that this message should be rebroadcast.)
    _mmsi = '{0:b}'.format(mmsi).rjust(30, '0')  # 30 bits (247320162)
    _status = '{0:b}'.format(status).rjust(4,
                                           '0')  # navigation status e.g. 0=Under way using engine, 1-At anchor, 5=Moored, 8=Sailing,15=undefined
    _rot = '{0:b}'.format(1).rjust(8, '0')  # rate of turn not defined
    _speed = '{0:b}'.format(int(round(speed))).rjust(10,
                                                     '0')  # Speed over ground is in 1 1/10th-knot resolution from 0 to 102 knots. value 1023 indicates speed is not available, value 1022 indicates 102.2 knots or higher.
    _accurancy = '0'  # > 10m
    _long = '{0:b}'.format(int(round(long * 600000)) & 0b1111111111111111111111111111).rjust(28,'0')  # -180 to 180, 181 is unavaliable
    _lat = '{0:b}'.format(int(round(lat *600000)) & 0b111111111111111111111111111).rjust(27,'0')  # -90 to 90, 91 is unavailable
    _course = '{0:b}'.format(int(round(course))).rjust(12,
                                                       '0')  # 1 resolution. Course over ground will be 3600 (0xE10) if that data is not available.
    _true_heading = '{0:b}'.format(int(round(true_heading))).rjust(9, '0')  # 511 (N/A)
    _ts = '{0:b}'.format(ts).rjust(6, '0')  # Second of UTC timestamp.
    _flags = '0' * 6
    # '00': manufactor NaN
    # '000':  spare
    # '0': Raim flag
    _rstatus = '0' * 19
    # '11100000000000000110' : Radio status

    return _type + _repeat + _mmsi + _status + _rot + _speed + _accurancy + _long + _lat + _course + _true_heading + _ts + _flags + _rstatus


@app.route('/api/newShip', methods=['POST'])  # API endpoint for adding a new ship to the database
def newShip():
    def getShipByMMSI(mmsi):  # Function to get the ship data from the database
        sqlcursor.execute("SELECT shipID FROM shipstatic WHERE mmsi = '" + mmsi + "';")
        shipID = sqlcursor.fetchone()
        return shipID

    if request.is_json:
        request_data = request.get_json()  # Get the request data
    else:
        request_data = xmltodict.parse(request.data)  # Parse the XML data into a dictionary
        request_data = request_data.popitem()[1]  # Remove the root element from the XML

    if not validate_json(request_data, 'newShip'):  # Validate the JSON against the JSON scheme
        return jsonify({"error": "Invalid Request"}), 400  # Return error if JSON is not valid

    apiKey = sanitizeInput(str(request_data['user']['apiKey']))  # Sanitize the API key
    if checkApiLimit(apiKey) is not None:  # Checks the API limit for the user
        return checkApiLimit(apiKey).data  # Return error if API limit is exceeded
    else:
        decreaseLimit(apiKey)  # Decrease the API limit for the user

    mmsi = sanitizeInput(str(request_data['ship']['mmsi']))  # Sanitize the MMSI
    nameOfShip = sanitizeInput(str(request_data['ship']['nameOfShip']))  # Sanitize the name of the ship
    typeOfShip = sanitizeInput(str(request_data['ship']['typeOfShip']))  # Sanitize the type of the ship

    if getShipByMMSI(mmsi) is not None:  # Check if the ship already exists in the database
        return jsonify({"error": "Ship already exists", "shipID": getShipByMMSI(mmsi)[
            0]}), 200  # Return error if ship already exists along with the ship ID

    if len(nameOfShip) > 20:  # Check if the name of the ship is too long - if so name is shortend to 20 characters according to Maritime standard
        remainingLength = 20
        newName = ""
        nameOfShip = nameOfShip.split()  # Split the name of the ship into words
        lastWord = nameOfShip[-1]  # Get the last word of the name of the ship
        lastWord = "_" + lastWord  # Add an underscore to the last word
        remainingLength -= len(lastWord)  # Decrease the remaining length by the length of the last word
        for word in nameOfShip:  # Loop through the words of the name of the ship
            if len(word) < remainingLength:  # If the length of the word is less than the remaining length
                newName += (word + " ")  # Add the word to the new name
                remainingLength -= len(word) + 1  # Decrease the remaining length by the length of the word plus 1
        newName += lastWord  # Add the last word to the new name
        nameOfShip = newName  # Set the name of the ship to the new name

    sqlcursor.execute(
        "INSERT INTO shipstatic (mmsi, nameOfShip, typeOfShip) VALUES ('" + mmsi + "', '" + nameOfShip + "', '" + typeOfShip + "');")  # Insert the ship into the database
    aisDB.commit()  # Commit the changes to the database

    return jsonify({"success": "Ship added",
                    "shipID": getShipByMMSI(mmsi)[0]}), 200  # Return success if ship was added along with the ship ID


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

    if 'ship' in request_data and 'shipID' in request_data[
        'ship']:  # Check if the ship ID is in the request as part of the ship
        shipID = sanitizeInput(str(request_data['ship']['shipID']))  # Sanitize the ship ID

        sqlcursor.execute(
            "SELECT * FROM shipstatic WHERE shipID = '" + shipID + "';")  # Get the ship data from the database
        ship = sqlcursor.fetchone()  # Get the ship data from the database
        if ship is None:  # Check if the ship exists in the database
            return jsonify({"error": "Ship not found"}), 200
        else:
            return jsonify({"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2],
                            "typeOfShip": ship[3]}), 200  # Return the ship data
    else:
        sqlcursor.execute("SELECT * FROM shipstatic;")  # Get all the ships from the database
        ships = sqlcursor.fetchall()  # Get all the ships from the database
        return jsonify({"ships": [{"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2], "typeOfShip": ship[3]} for
                                  ship in ships]}), 200  # Return all the ships using a loop to display a list of ships


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

    sqlcursor.execute(
        "SELECT userID, apiLimit FROM users WHERE userID = '" + userID + "';")  # Get the user ID and API limit from the database
    apiLimit = sqlcursor.fetchone()  # Get the user ID and API limit from the database
    if apiLimit is None:  # Check if the user exists in the database
        return jsonify({"error": "User not found"}), 200  # Return error if user does not exist
    return jsonify({"userID": apiLimit[0], "apiLimit": apiLimit[1]}), 200  # Return the user ID and API limit


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

    mmsi = int(request_data['ship']['mmsi'])
    status = int(request_data['AIS']['status'])
    speed =  int(request_data['AIS']['speed'])
    longitude =  float(request_data['AIS']['longitude'])
    latitude =  float(request_data['AIS']['latitude'])
    course =  int(request_data['AIS']['course'])
    trueHeading =  int(request_data['AIS']['trueHeading'])
    timestamp =  int(request_data['AIS']['timestamp'])

    aisBinary = encodeAISBinary_1(mmsi, status, speed, latitude, longitude, course, trueHeading,
                                  timestamp)  # Encode the AIS data into binary

    binaryArray = textwrap.wrap(aisBinary, 6)  # Split the binary data into an array of 6-bit binary strings
    payload = ""
    for binary6Bit in binaryArray:  # Loop through the 6-bit binary strings
        decimal = int(binary6Bit, 2)  # Convert the 6-bit binary string to a decimal number
        payload += encodeVocabulary[decimal]  # Add the encoded character to the payload
    print (payload)
    return jsonify({"AISMessage": payload,
                    "AISMessageBinary": aisBinary}), 200  # Return the AIS message and the AIS message binary


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

    aisBinary = None  # Initialize the AIS binary string
    if 'AIVDM' in request_data['AIS']:  # Check if the AIS message is in the request as part of the AIS
        aivdmMessage = request_data['AIS']['AIVDM']  # Get the AIS message from the request
        if aivdmMessage.startswith('!AIVDM'):  # Check if the AIS message starts with the correct prefix
            aivdmMessage = aivdmMessage.split(',')[5:6][0]  # Remove the prefix from the AIS message
        binary = ""  # Initialize the binary string
        for char in aivdmMessage:  # Loop through the characters in the AIS message
            index = encodeVocabulary.find(char)  # Get the index of the character in the vocabulary
            binary6Bit = '{0:b}'.format(index).rjust(6, '0')  # Convert the index to a 6-bit binary string
            binary += binary6Bit  # Add the 6-bit binary string to the binary string
        aisBinary = binary  # Set the AIS binary string to the binary string
    else:
        aisBinary = request_data['AIS']['binary']  # Get the AIS binary string from the request

    type = int(aisBinary[0:6], 2)  # Get the type of the AIS message from the binary string
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
                                   "RStatus": response[15]}}), 200  # Return the AIS message


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

    if 'request' in request_data and 'spoofID' in request_data['request']:  # Check if the request contains the spoof ID
        spoofID = sanitizeInput(str(request_data['request']['spoofID']))  # Get the spoof ID from the request
        sqlcursor.execute(
            "SELECT * FROM requests WHERE requestID = '" + spoofID + "';")  # Get the spoof request from the database
        spoofData = sqlcursor.fetchone()  # Get the spoof request from the database
        if spoofData is None:
            return jsonify({"error": "Spoof ID not found"}), 200  # Return the error if the spoof ID was not found
        else:
            return jsonify({"spoofData": {"requestID": spoofData[0], "userID": spoofData[1], "shipID": spoofData[2],
                                          "locationEPFS": spoofData[3], "longitude": spoofData[4],
                                          "latitude": spoofData[5], "timestamp": spoofData[6], "cog": spoofData[7],
                                          "sog": spoofData[8], "heading": spoofData[9], "rot": spoofData[10],
                                          "status": spoofData[11],
                                          "currentTime": spoofData[12]}}), 200  # Return the spoof data
    else:
        sqlcursor.execute("SELECT * FROM requests;")  # Get all the spoof requests from the database
        spoofData = sqlcursor.fetchall()  # Get all the spoof requests from the database
        if spoofData is None:
            return jsonify({"error": "No spoof data found"}), 400  # Return the error if no spoof data was found
        else:
            return jsonify({"spoofData": [
                {"requestID": spoofData[i][0], "userID": spoofData[i][1], "shipID": spoofData[i][2],
                 "longitude": spoofData[i][4], "latitude": spoofData[i][5],
                 "timestamp": spoofData[i][6], "cog": spoofData[i][7], "sog": spoofData[i][8],
                 "heading": spoofData[i][9], "rot": spoofData[i][10], "status": spoofData[i][11],
                 "currentTime": spoofData[i][12]} for i in range(len(spoofData))]}), 200  # Return the spoof data


@app.route('/api/spoofShip', methods=['POST'])
def spoofShip():
    if request.is_json:
        request_data = request.get_json()
    else:
        request_data = xmltodict.parse(request.data)
        request_data = request_data.popitem()[1]

    if not validate_json(request_data, 'spoofShip'):
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

    sqlcursor.execute("SELECT mmsi FROM shipstatic WHERE shipID = '" + shipID + "';")  # Get the MMSI from the database
    shipData = sqlcursor.fetchone()  # Get the MMSI from the database
    if shipData is None:  # Check if the MMSI was not found
        return jsonify({"error": "Ship ID not found"}), 200  # Return the error if the MMSI was not found
    else:
        mmsi = str(shipData[0]) # Get the MMSI from the database

    sqlcursor.execute("SELECT userID FROM users WHERE apiKey = '" + apiKey + "';")  # Get the user ID from the database
    userData = sqlcursor.fetchone()  # Get the user ID from the database
    if userData is None:  # Check if the user ID was not found
        return jsonify({"error": "User not found"}), 200  # Return the error if the user ID was not found
    else:
        userID = str(userData[0])  # Get the user ID from the database

    aisPayload = encodeAISBinary_1( int(mmsi),  int(status),  int(speed), float(latitude), float(longitude), int(course),  int(heading), int(timestamp)) # Encode the AIS message

    if exists('AIS_TX.py'):
        try:
            os.system("AIS_TX.py -p " + str(aisPayload)) # Send the AIS message
        except:
            return jsonify({"error": "Error sending AIS message"}), 400 
            exit()
    else:
        return jsonify({"error": "AIS_TX.py not found"}), 500

    sqlcursor.execute(
        "INSERT INTO requests (userID, shipID, longitude, latitude, timestamp, cog, sog, heading, rot, status) VALUES ('" + userID + "', '" + shipID + "', '" + longitude + "', '" + latitude + "', '" + timestamp + "', '" + course + "', '" + speed + "', '" + heading + "', '" + rot + "', '" + status + "');")  # Insert the spoof request into the database
    aisDB.commit()  # Commit the changes to the database

    return jsonify({"success": "Spoof request sent"}), 200  # Return the success message if the spoof request was sent

app.run(host='0.0.0.0', port=1234)  # TODO: change this
