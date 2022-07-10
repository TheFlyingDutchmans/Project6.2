from flask import jsonify

from scripts import dbTools, AISencode, xmlTools, jsonTools


def encode(request, sqlCursor, aisDB):
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