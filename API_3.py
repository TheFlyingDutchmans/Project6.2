import os
import time
from flask import Flask, jsonify, request
import xmlify
import configparser
from scripts import jsonTools, dbTools, AISencode, xmlTools, tools



secKey = configparser.ConfigParser() # Read the config file for the secret key
secKey.read('config/secretKey.ini')
apiConfig = configparser.ConfigParser() # Read the config file for the API
apiConfig.read('config/API.ini')

if not secKey.sections() or not apiConfig.sections(): # If the config file is empty
    print("Config file missing")
    exit()

app = Flask(__name__)  # Initialize Flask app
app.secret_key = secKey['secKey']['key']

sqlCursor, aisDB = dbTools.connectToDB() # Connect to the database
if aisDB is None or sqlCursor is None:
    print("Error connecting to database")
    exit()




@app.route('/apiv3/newShip', methods=['POST', 'PUT']) # Create a new ship
def newShip():
    if request.is_json: # If the request is JSON
        request_data = request.get_json() # Get the JSON data
        if jsonTools.validateJson(request_data, 'newShip') is False: # Validate the JSON data
            return jsonify({"error": "Invalid JSON"}), 400 # If the JSON data is invalid, return an error
        else:
            mmsi = tools.sanitizeInput(request_data['ship']['mmsi']) # Sanitize the input
            nameOfShip = tools.sanitizeInput(request_data['ship']['nameOfShip'])
            typeOfShip = tools.sanitizeInput(request_data['ship']['typeOfShip'])
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data # Get the XML data
        if xmlTools.validateXML(request_data, 'newShip') is False: # Validate the XML data
            return xmlTools.xmlResponse("error", "Invalid XML"), 400 # If the XML data is invalid, return an error
        else:
            mmsi = xmlTools.getValue(request_data, 'ship', 'mmsi', True) # Get the MMSI and sanitize the input
            nameOfShip = xmlTools.getValue(request_data, 'ship', 'nameOfShip', True)
            typeOfShip = xmlTools.getValue(request_data, 'ship', 'typeOfShip', True)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'


    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor) # Check if the API key is valid and if the API limit is not exceeded
    if isApiKeyValid is not None: # If the API key is not valid
        if returnType == 'json': # If the request is JSON
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2] # Return an error
        elif returnType == 'xml': # If the request is XML
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2] # Return an error
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB) # Decrease the API limit of the user

    shipID = dbTools.getShipByMMSI(mmsi, sqlCursor) # Get the ship ID
    if shipID is not None:
        if returnType == 'json':
            return jsonify({'error': 'MMSI already exists', 'shipID': shipID[0]}), 418
        elif returnType == 'xml':
            return xmlTools.xmlResponse('error', 'MMSI already exists'), 418

    if len(nameOfShip) > 20: # If the name of the ship is longer than 20 characters shorten it by Maritime standard
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

    sqlCursor.execute( # Insert the new ship into the database
        "INSERT INTO shipstatic (mmsi, nameOfShip, typeOfShip) VALUES ('" + mmsi + "', '" + nameOfShip + "', '" + typeOfShip + "');")
    aisDB.commit()

    if returnType == 'json':
        return jsonify({'success': 'Ship added', 'shipID': dbTools.getShipByMMSI(mmsi, sqlCursor)[0]}), 201 # Return the ship ID
    elif returnType == 'xml':
        shipID = dbTools.getShipByMMSI(mmsi, sqlCursor)[0] # Get the ship ID
        return xmlTools.xmlResponse(['success','shipID'], ['Ship added', str(shipID)]), 201 # Return the ship ID

@app.route('/apiv3/getShip', methods=['GET'])
def getShip():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'getShip') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            if 'ship' in request_data and 'shipID' in request_data['ship']:
                shipID = tools.sanitizeInput(request_data['ship']['shipID'])
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'getShip') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            shipID = xmlTools.getValue(request_data, 'ship', 'shipID', True)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'


    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)


    if 'shipID' in locals() and shipID is not None: # If the ship ID is given
        sqlCursor.execute("SELECT * FROM shipstatic WHERE shipID = " + shipID + ";") # Get the ship from the database
        ship = sqlCursor.fetchone()
        if ship is not None: # If the ship exists
            if returnType == 'json': # If the request is JSON
                return jsonify({"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2],
                                "typeOfShip": ship[3]}), 200 # Return the ship
            elif returnType == 'xml':
                shipID, mmsi, nameOfShip, typeOfShip = str(ship[0]), str(ship[1]), str(ship[2]), str(ship[3]) # Get the ship data
                return xmlTools.xmlResponse(['shipID','mmsi', 'nameOfShip', 'typeOfShip'], [shipID, mmsi, nameOfShip, typeOfShip]), 200 # Return the ship
        else:
            if returnType == 'json':
                return jsonify({'error': 'Ship not found'}), 404 # Return an error
            elif returnType == 'xml':
                return xmlTools.xmlResponse('error', 'Ship not found'), 404 # Return an error
    else: # If the ship ID is not given
        sqlCursor.execute("SELECT * FROM shipstatic;") # Get all the ships from the database
        ships = sqlCursor.fetchall() # Get all the ships
        if ships is not None: # If there are ships
            if returnType == 'json':
                return jsonify(
                    {"ships": [{"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2], "typeOfShip": ship[3]} for
                               ship in ships]}), 200 # Return all the ships
            elif returnType == 'xml':
                response ={
                    "ships": [{"shipID": ship[0], "mmsi": ship[1], "nameOfShip": ship[2], "typeOfShip": ship[3]} for
                               ship in ships] # Get all the ships
                }
                return xmlify.dumps(response, 'root'), 200 # Return all the ships

@app.route('/apiv3/getApiLimit', methods=['GET'])
def getApiLimit():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'getApiLimit') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            userID = tools.sanitizeInput(request_data['user']['userID'])
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'getApiLimit') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            userID = xmlTools.getValue(request_data, 'user', 'userID', True)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'

    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)

    sqlCursor.execute("SELECT userID, apiLimit FROM users WHERE userID = " + userID + ";") # Get the user from the database
    apiLimit = sqlCursor.fetchone() # Get the user
    if apiLimit is not None:  # If the user exists
        if returnType == 'json':
            return jsonify({"userID": apiLimit[0], "apiLimit": apiLimit[1]}), 200 # Return the user
        elif returnType == 'xml':
            userId, api = str(apiLimit[0]), str(apiLimit[1])
            return xmlTools.xmlResponse(['userID', 'apiLimit'], [userId, api]), 200
    else:
        if returnType == 'json':
            return jsonify({'error': 'User not found'}), 404
        elif returnType == 'xml':
            return xmlTools.xmlResponse('error', 'User not found'), 404

@app.route('/apiv3/encodeAIS', methods=['GET'])
def encodeAIS():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'encodeAIS') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            mmsi = request_data['ship']['mmsi']
            status = request_data['AIS']['status']
            speed = request_data['AIS']['speed']
            longitude = request_data['AIS']['longitude']
            latitude = request_data['AIS']['latitude']
            course = request_data['AIS']['course']
            trueHeading = request_data['AIS']['trueHeading']
            timestamp = request_data['AIS']['timestamp']
            apiKey = request_data['user']['apiKey']
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'encodeAIS') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            mmsi = int(xmlTools.getValue(request_data, 'ship', 'mmsi', False))
            status = int(xmlTools.getValue(request_data, 'AIS', 'status', False))
            speed = int(xmlTools.getValue(request_data, 'AIS', 'speed', False))
            longitude = int(xmlTools.getValue(request_data, 'AIS', 'longitude', False))
            latitude = int(xmlTools.getValue(request_data, 'AIS', 'latitude', False))
            course = int(xmlTools.getValue(request_data, 'AIS', 'course', False))
            trueHeading = int(xmlTools.getValue(request_data, 'AIS', 'trueHeading', False))
            timestamp =int( xmlTools.getValue(request_data, 'AIS', 'timestamp', False))
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'


    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)

    aisBinary = AISencode.encodeAISBinary1(mmsi, status, speed, latitude, longitude, course, trueHeading, timestamp) # Encode the AIS message
    ascii = AISencode.binaryToASCII(aisBinary) # Convert the binary to ASCII
    if returnType == 'json':
        return jsonify({"AISMessage": ascii,
                        "AISMessageBinary": aisBinary}), 200
    elif returnType == 'xml':
        return xmlTools.xmlResponse(['AISMessage', 'AISMessageBinary'], [ascii, aisBinary]), 200

@app.route('/apiv3/decodeAIS', methods=['GET'])
def decodeAIS():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'decodeAIS') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            if 'AIVDM' in request_data['AIS']:
                aivdmMessage = request_data['AIS']['AIVDM']
            elif 'binary' in request_data['AIS']:
                binaryMessage = request_data['AIS']['binary']
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'decodeAIS') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            aivdmMessage = xmlTools.getValue(request_data, 'AIS', 'AIVDM', False)
            if aivdmMessage is None:
                binaryMessage = xmlTools.getValue(request_data, 'AIS', 'binary', False)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'

    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)

    if 'aivdmMessage' in locals() and aivdmMessage is not None: # If the request contains a AIVDM message
        binaryMessage =AISencode.ASCIIToBinary(aivdmMessage) # Convert the ASCII to binary
    response = AISencode.binaryDecoder(binaryMessage) # Decode the binary message

    if returnType == 'json':
        return jsonify({"AISMessage": {"Type": response[0], "Repeat": response[1], "MMSI": response[2],
                                       "Status": response[3], "RateOfTurn": response[4], "Speed": response[5],
                                       "Accuracy": response[6], "Longitude": response[7], "Latitude": response[8],
                                       "Course": response[9], "TrueHeading": response[10], "Timestamp": response[11],
                                       "SMI": response[12], "Spare": response[13], "Raim": response[14],
                                       "RStatus": response[15]}}), 200 # Return the decoded message
    elif returnType == 'xml':
        return xmlTools.xmlResponse(['Type', 'Repeat', 'MMSI', 'Status', 'RateOfTurn', 'Speed', 'Accuracy',
                                     'Longitude', 'Latitude', 'Course', 'TrueHeading', 'Timestamp', 'SMI', 'Spare', 'Raim',
                                     'RStatus'], [response[0], response[1], response[2], response[3], response[4],
                                                 response[5], response[6], response[7], response[8], response[9],
                                                 response[10], response[11], response[12], response[13], response[14],
                                                 response[15]]), 200 # Return the decoded message

@app.route('/apiv3/getSpoofData', methods=['GET'])
def getSpoofData():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'getSpoofData') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            if 'request' in request_data and 'spoofID' in request_data['request']:
                spoofID = str(request_data['request']['spoofID'])
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'getSpoofData') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            spoofID = xmlTools.getValue(request_data, 'request', 'spoofID', True)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'

    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)

    if 'spoofID' in locals() and spoofID is not None: # If the request contains a spoofID
        sqlCursor.execute(
            "SELECT * FROM requests WHERE requestID = '" + spoofID + "';") # Get the spoof data
        spoofData = sqlCursor.fetchone()
        if spoofData is None: # If the spoofID is not found
            if returnType == 'json':
                return jsonify({"error": "Spoof ID not found"}), 404 # Return an error
            elif returnType == 'xml':
                return xmlTools.xmlResponse("error", "Spoof ID not found"), 404
        else:
            if returnType == 'json':
                return jsonify({"spoofData": {"requestID": spoofData[0], "userID": spoofData[1], "shipID": spoofData[2],
                                              "longitude": spoofData[3],
                                              "latitude": spoofData[4], "timestamp": spoofData[5], "cog": spoofData[6],
                                              "sog": spoofData[7], "heading": spoofData[8], "rot": spoofData[9],
                                              "status": spoofData[10],
                                              "currentTime": spoofData[11]}}), 200  # Return the spoof data as JSON
            elif returnType == 'xml':
                response = {
                    "spoofData": {"requestID": spoofData[0], "userID": spoofData[1], "shipID": spoofData[2],
                                   "longitude": spoofData[3], "latitude": spoofData[4], "timestamp": spoofData[5],
                                   "cog": spoofData[6], "sog": spoofData[7], "heading": spoofData[8],
                                   "rot": spoofData[9], "status": spoofData[10], "currentTime": spoofData[11]}}
                return xmlify.dumps(response, 'root'), 200 # Return the spoof data as XML


    else: # If the request does not contain a spoofID
        sqlCursor.execute("SELECT * FROM requests;") # Get all the spoof data
        spoofData = sqlCursor.fetchall()
        if spoofData is None:
            if returnType == 'json':
                return jsonify({"error": "No spoof data found"}), 404
            elif returnType == 'xml':
                return xmlTools.xmlResponse("error", "No spoof data found"), 404
        else:
            if returnType == 'json':
                return jsonify({"spoofData": [
                    {"requestID": spoofdata[0], "userID": spoofdata[1], "shipID": spoofdata[2],
                     "longitude": spoofdata[3], "latitude": spoofdata[4],
                     "timestamp": spoofdata[5], "cog": spoofdata[6], "sog": spoofdata[7],
                     "heading": spoofdata[8], "rot": spoofdata[9], "status": spoofdata[10],
                     "currentTime": spoofdata[11]} for spoofdata in spoofData]}), 200 # Return the spoof data as JSON
            elif returnType == 'xml':
                response = {
                    "spoofData": [{"requestID": data[0], "userID": data[1], "shipID": data[2],
                                      "longitude": data[3], "latitude": data[4], "timestamp": data[5],
                                        "cog": data[6], "sog": data[7], "heading": data[8],
                                        "rot": data[9], "status": data[10], "currentTime": data[11]}
                                    for data in spoofData]}
                return xmlify.dumps(response, 'root'), 200 # Return the spoof data as XML

@app.route('/apiv3/spoofShip', methods=['POST', 'PUT'])
def spoofShip():
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'spoofShip') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            shipID = tools.sanitizeInput(request_data['ship']['shipID'])
            longitude = tools.sanitizeInput(request_data['AIS']['longitude'])
            latitude = tools.sanitizeInput(request_data['AIS']['latitude'])
            timestamp = tools.sanitizeInput(request_data['AIS']['timestamp'])
            course = tools.sanitizeInput(request_data['AIS']['course'])
            speed = tools.sanitizeInput(request_data['AIS']['speed'])
            heading = tools.sanitizeInput(request_data['AIS']['heading'])
            rot = tools.sanitizeInput(request_data['AIS']['rot'])
            status = tools.sanitizeInput(request_data['AIS']['status'])
            apiKey = tools.sanitizeInput(request_data['user']['apiKey'])
            returnType = 'json'
    else:
        request_data = request.data
        if xmlTools.validateXML(request_data, 'spoofShip') is False:
            return xmlTools.xmlResponse("error", "Invalid XML"), 400
        else:
            shipID = xmlTools.getValue(request_data, 'ship', 'shipID', True)
            longitude = xmlTools.getValue(request_data, 'AIS', 'longitude', True)
            latitude = xmlTools.getValue(request_data, 'AIS', 'latitude', True)
            timestamp = xmlTools.getValue(request_data, 'AIS', 'timestamp', True)
            course = xmlTools.getValue(request_data, 'AIS', 'course', True)
            speed = xmlTools.getValue(request_data, 'AIS', 'speed', True)
            heading = xmlTools.getValue(request_data, 'AIS', 'heading', True)
            rot = xmlTools.getValue(request_data, 'AIS', 'rot', True)
            status = xmlTools.getValue(request_data, 'AIS', 'status', True)
            apiKey = xmlTools.getValue(request_data, 'user', 'apiKey', True)
            returnType = 'xml'

    isApiKeyValid = dbTools.checkApiLimit(apiKey, sqlCursor)
    if isApiKeyValid is not None:
        if returnType == 'json':
            return jsonify({isApiKeyValid[0]: isApiKeyValid[1]}), isApiKeyValid[2]
        elif returnType == 'xml':
            return xmlTools.xmlResponse(isApiKeyValid[0], isApiKeyValid[1]), isApiKeyValid[2]
    else:
        dbTools.decreaseApiLimit(apiKey, sqlCursor, aisDB)

    sqlCursor.execute("SELECT mmsi FROM shipstatic WHERE shipID = '" + shipID + "';") # Get the MMSI of the ship
    shipData = sqlCursor.fetchone()
    if shipData is None:
        if returnType == 'json':
            return jsonify({"error": "No ship found"}), 404
        elif returnType == 'xml':
            return xmlTools.xmlResponse("error", "No ship found"), 404
    else:
        mmsi = str(shipData[0])

    sqlCursor.execute("SELECT userID FROM users WHERE apiKey = '" + apiKey + "';") # Get the userID of the user
    userID = sqlCursor.fetchone()
    if userID is None:
        if returnType == 'json':
            return jsonify({"error": "No user found"}), 404
        elif returnType == 'xml':
            return xmlTools.xmlResponse("error", "No user found"), 404

    aisPayload = AISencode.encodeAISBinary1(int(mmsi), int(status), int(speed), int(latitude), int(longitude), int(course), int(heading), int(timestamp)) # Encode the AIS payload
    currentPath = os.getcwd()

    try:
        os.system("python3 " + currentPath + "/AIS_TX.py -p " + str(aisPayload)) # Send the AIS payload to the AIS transmitter
        time.sleep(5)
        os.system("killall python3") # TODO: Check if this ONLY kills the child process
    except:
        if returnType == 'json':
            return jsonify({"error": "Error sending AIS message"}), 500
        elif returnType == 'xml':
            return xmlTools.xmlResponse("error", "Error sending AIS message"), 500
        exit()

    sqlCursor.execute(
        "INSERT INTO requests (userID, shipID, longitude, latitude, timestamp, cog, sog, heading, rot, status) VALUES ('" + userID + "', '" + shipID + "', '" + longitude + "', '" + latitude + "', '" + timestamp + "', '" + course + "', '" + speed + "', '" + heading + "', '" + rot + "', '" + status + "');")  # Insert the spoof request into the database
    aisDB.commit() # Commit the changes to the database

    if returnType == 'json':
        return jsonify({"success": "Spoof request sent"}), 200
    elif returnType == 'xml':
        return xmlTools.xmlResponse("success", "Spoof request sent"), 200


app.run(host=apiConfig['API']['host'], port=apiConfig['API']['port'], debug=apiConfig['API']['debug'])

