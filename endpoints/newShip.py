from flask import jsonify
from scripts import dbTools, tools, jsonTools, xmlTools


def newShip(request, sqlCursor, aisDB):
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