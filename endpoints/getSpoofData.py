import xmlify
from flask import jsonify

from scripts import xmlTools, dbTools, tools, jsonTools


def getSpoofData(request, sqlCursor, aisDB):
    if request.is_json:
        request_data = request.get_json()
        if jsonTools.validateJson(request_data, 'getSpoofData') is False:
            return jsonify({"error": "Invalid JSON"}), 400
        else:
            if 'request' in request_data and 'spoofID' in request_data['request']:
                spoofID = tools.sanitizeInput(request_data['request']['spoofID'])
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