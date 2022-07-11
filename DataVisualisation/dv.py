import os
import time
import webbrowser

import requests
import json
import folium
import xml.etree.ElementTree as ET

opn = True

title_json = '''
<h3 align="center" style="font-size:16px">JSON map</h3>
'''

title_xml = '''
<h3 align="center" style="font-size:16px">XML map</h3>
'''

reload = "<script>setTimeout(function(){window.location.reload(1);}, 10000);</script>"

url = "http://127.0.0.1:5000/apiv3/spoof"

headers_json = {
    'Content-Type': 'application/json'
}

headers_xml = {
    'Content-Type': 'application/xml'
}

def createMap():
    m = folium.Map(
        location=[34.825830, 18.359418],
        zoom_start=2,
        max_bounds=True,
        min_zoom=2,
        width='100%',
        height='100%'
    )
    return m

def getAllSpoofData():
    get_spoof_data_payload_xml = "<root>\r\n    " \
                                 "<user>\r\n        " \
                                 "<apiKey>admin</apiKey>\r\n    " \
                                 "</user>\r\n" \
                                 "</root>\r\n "
    response_xml = requests.request("GET", url, headers=headers_xml, data=get_spoof_data_payload_xml)
    # get xml from the response and
    response_info_xml = ET.fromstring(response_xml.text)

    get_spoof_data_payload_json = json.dumps({
        "request": {
        },
        "user": {
            "apiKey": "admin"
        }
    })
    response_json = requests.request("GET", url, headers=headers_json, data=get_spoof_data_payload_json)
    response_info_json = json.loads(response_json.text)
    return response_info_json, response_info_xml


def getSingleSpoofData(id):
    get_spoof_data_payload_xml = "<root>\r\n    " \
                                 "<request>\r\n        " \
                                 "<spoofID>" + str(id) + "</spoofID>\r\n    " \
                                                         "</request>\r\n" \
                                                         "<user>\r\n        " \
                                                         "<apiKey>admin</apiKey>\r\n    " \
                                                         "</user>\r\n" \
                                                         "</root>\r\n "
    response_xml = requests.request("GET", url, headers=headers_xml, data=get_spoof_data_payload_xml)
    response_info_xml = ET.fromstring(response_xml.text)
    print(response_xml.text)

    get_spoof_data_payload_json = json.dumps({
        "request": {
            "spoofID": id
        },
        "user": {
            "apiKey": "admin"
        }
    })
    response_json = requests.request("GET", url, headers=headers_json, data=get_spoof_data_payload_json)
    response_info_json = json.loads(response_json.text)

    return response_info_json, response_info_xml


def displaySingleShip(id):
    response_info_json, response_info_xml = getSingleSpoofData(id)
    addMarkerJson(response_info_json["spoofData"])

    lat = response_info_xml.find('spoofData').find('latitude').text
    long = response_info_xml.find('spoofData').find('longitude').text
    time = response_info_xml.find('spoofData').find('currentTime').text
    print(lat, long, time)
    addMarkerXml(lat, long, time)


def displayAllShips():
    response_info_json, response_info_xml = getAllSpoofData()
    # iterate over spoofData in JSON file and add it to a map
    for spoof in response_info_json["spoofData"]:
        addMarkerJson(spoof)

    # iterate over spoofData in XML file and add it to a map
    for spoof in response_info_xml.find('spoofData'):
        lat = spoof.find('latitude').text
        long = spoof.find('longitude').text
        time = spoof.find('currentTime').text
        addMarkerXml(lat, long, time)


def addMarkerJson(spoof):
    lat = spoof["latitude"]
    long = spoof["longitude"]
    time = spoof["currentTime"]
    folium.Marker(
        location=[lat, long],
        popup=str(time),
    ).add_to(json_map)


def addMarkerXml(lat, long, time):
    folium.Marker(
        location=[lat, long],
        popup=str(time),
    ).add_to(xml_map)


# Create a while loop that runs once every 10 seconds
while True:
    json_map = createMap()
    xml_map = createMap()
    displayAllShips()
    json_map.get_root().html.add_child(folium.Element(title_json))
    json_map.get_root().header.add_child(folium.Element(reload))
    json_map.save('json_map.html')
    xml_map.get_root().html.add_child(folium.Element(title_xml))
    xml_map.get_root().header.add_child(folium.Element(reload))
    xml_map.save('xml_map.html')
    print("Saved maps")
    # Execute the following code once then never again
    if opn:
        webbrowser.open('json_map.html')
        webbrowser.open('xml_map.html')
        opn = False
    time.sleep(10)
