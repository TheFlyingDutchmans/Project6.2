from flask import jsonify

from scripts import dbTools, jsonTools, tools, xmlTools


def getApiLimit(request, sqlCursor, aisDB):
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