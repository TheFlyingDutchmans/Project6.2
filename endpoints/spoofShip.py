import os
import time

from flask import jsonify

from scripts import xmlTools, AISencode, dbTools, tools, jsonTools


def spoofShip(request, sqlCursor, aisDB):
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