import os
from io import StringIO
from lxml import etree
import xml.etree.ElementTree as ET
import scripts.tools as tools


def validateXML(xmlDataInBytes, XSDData): # Validates XML against XSD
    cd = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    with open(cd + "/Schemas/XML/" + XSDData + ".xsd", 'r') as xsd:
        xmlschema_doc = etree.parse(xsd)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xmlDataInBytes = xmlDataInBytes.decode('utf-8')
    xmlData = StringIO(xmlDataInBytes)
    xml = etree.parse(xmlData)
    return xmlschema.validate(xml)

def xmlResponse(node, response): # Creates an XML response
    root = ET.Element("root")
    if isinstance(node, list):
        for i in range (len(node)):
            answer = ET.SubElement(root, node[i])
            answer.text = response[i]
    else:
        answer = ET.SubElement(root, node)
        answer.text = response
    xml_string = ET.tostring(root)
    return xml_string


def getValue(request, parent, node, sanitize): # Gets the value of a node
    xmlData = request.decode('utf-8')
    tree = ET.parse(StringIO(xmlData))
    root = tree.getroot()
    try:
        if sanitize:
            return tools.sanitizeInput(root.find(parent).find(node).text)
        return (root.find(parent).find(node).text)
    except:
        return None
