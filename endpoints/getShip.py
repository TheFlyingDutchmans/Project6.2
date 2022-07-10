import xmlify
from flask import jsonify

from scripts import jsonTools, tools, xmlTools, dbTools


def getShip(request, sqlCursor, aisDB):
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