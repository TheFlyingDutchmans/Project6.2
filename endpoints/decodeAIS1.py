from flask import jsonify

from scripts import AISencode, xmlTools, tools, dbTools, jsonTools


def decode(request, sqlCursor, aisDB):
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

    if 'aivdmMessage' in locals() and aivdmMessage is not None:  # If the request contains a AIVDM message
        binaryMessage = AISencode.ASCIIToBinary(aivdmMessage)  # Convert the ASCII to binary
    response = AISencode.binaryDecoder(binaryMessage)  # Decode the binary message

    if returnType == 'json':
        return jsonify({"AISMessage": {"Type": response[0], "Repeat": response[1], "MMSI": response[2],
                                       "Status": response[3], "RateOfTurn": response[4], "Speed": response[5],
                                       "Accuracy": response[6], "Longitude": response[7], "Latitude": response[8],
                                       "Course": response[9], "TrueHeading": response[10], "Timestamp": response[11],
                                       "SMI": response[12], "Spare": response[13], "Raim": response[14],
                                       "RStatus": response[15]}}), 200  # Return the decoded message
    elif returnType == 'xml':
        return xmlTools.xmlResponse(['Type', 'Repeat', 'MMSI', 'Status', 'RateOfTurn', 'Speed', 'Accuracy',
                                     'Longitude', 'Latitude', 'Course', 'TrueHeading', 'Timestamp', 'SMI', 'Spare',
                                     'Raim',
                                     'RStatus'], [response[0], response[1], response[2], response[3], response[4],
                                                  response[5], response[6], response[7], response[8], response[9],
                                                  response[10], response[11], response[12], response[13], response[14],
                                                  response[15]]), 200  # Return the decoded message


def tester(request):
    return jsonify({"test": request}), 200
