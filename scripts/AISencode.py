import textwrap

encodeVocabulary = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVW`abcdefghijklmnopqrstuvw"


def encodeAISBinary1(mmsi, status, speed, lat, long, course, true_heading, ts):
    # Encodes type 1 AIS messages using int type variables
    _type = '{0:b}'.format(1).rjust(6, '0')  # 18
    _repeat = "00"  # repeat     (directive to an AIS transceiver that this message should be rebroadcast.)
    _mmsi = '{0:b}'.format(mmsi).rjust(30, '0')  # 30 bits (247320162)
    _status = '{0:b}'.format(status).rjust(4,
                                           '0')  # navigation status e.g. 0=Under way using engine, 1-At anchor,
    # 5=Moored, 8=Sailing,15=undefined
    _rot = '{0:b}'.format(1).rjust(8, '0')  # rate of turn not defined
    _speed = '{0:b}'.format(int(round(speed))).rjust(10,
                                                     '0')  # Speed over ground is in 1 1/10th-knot resolution from 0
    # to 102 knots. value 1023 indicates speed is not available, value 1022 indicates 102.2 knots or higher.
    _accurancy = '0'  # > 10m
    _long = '{0:b}'.format(int(round(long * 600000)) & 0b1111111111111111111111111111).rjust(28,
                                                                                             '0')  # -180 to 180, 181
    # is unavaliable
    _lat = '{0:b}'.format(int(round(lat * 600000)) & 0b111111111111111111111111111).rjust(27,
                                                                                          '0')  # -90 to 90, 91 is
    # unavailable
    _course = '{0:b}'.format(int(round(course))).rjust(12,
                                                       '0')  # 1 resolution. Course over ground will be 3600 (0xE10)
    # if that data is not available.
    _true_heading = '{0:b}'.format(int(round(true_heading))).rjust(9, '0')  # 511 (N/A)
    _ts = '{0:b}'.format(ts).rjust(6, '0')  # Second of UTC timestamp.
    _flags = '0' * 6
    # '00': manufactor NaN
    # '000':  spare
    # '0': Raim flag
    _rstatus = '0' * 19
    # '11100000000000000110' : Radio status

    return _type + _repeat + _mmsi + _status + _rot + _speed + _accurancy + _long + _lat + _course + _true_heading + _ts + _flags + _rstatus

def binaryToASCII(binary):
    binaryArray = textwrap.wrap(binary, 6)  # Split the binary data into an array of 6-bit binary strings
    payload = ""
    for binary6Bit in binaryArray:  # Loop through the 6-bit binary strings
        decimal = int(binary6Bit, 2)  # Convert the 6-bit binary string to a decimal number
        payload += encodeVocabulary[decimal]  # Add the encoded character to the payload
    return payload

def ASCIIToBinary(ascii):
    if ascii.startswith('!AIVDM'):  # Check if the AIS message starts with the correct prefix
        ascii = ascii.split(',')[5:6][0]  # Remove the prefix from the AIS message
    binaryArray = ""  # Initialize the binary string
    for char in ascii:  # Loop through the characters in the AIS message
        index = encodeVocabulary.find(char)  # Get the index of the character in the vocabulary
        binary6Bit = '{0:b}'.format(index).rjust(6, '0')  # Convert the index to a 6-bit binary string
        binaryArray += binary6Bit  # Add the 6-bit binary string to the binary string
    aisBinary = binaryArray  # Set the AIS binary string to the binary string
    return aisBinary

def binaryDecoder(aisBinary):
    type = int(aisBinary[0:6], 2)  # Get the type of the AIS message from the binary string
    repeat = int(aisBinary[6:8], 2)
    mmsi = int(aisBinary[8:38], 2)
    status = int(aisBinary[38:42], 2)
    rot = int(aisBinary[42:50], 2)
    speed = int(aisBinary[50:60], 2)
    accurancy = int(aisBinary[60:61], 2)
    long = int(aisBinary[61:89], 2) / 600000
    lat = int(aisBinary[89:116], 2) / 600000
    course = int(aisBinary[116:128], 2)
    true_heading = int(aisBinary[128:137], 2)
    ts = int(aisBinary[137:143], 2)
    smi = int(aisBinary[143:145], 2)
    spare = int(aisBinary[145:148], 2)
    raim = int(aisBinary[148:149], 2)
    rstatus = int(aisBinary[149:], 2)
    response = [str(type), str(repeat), str(mmsi), str(status), str(rot), str(speed), str(accurancy), str(long),
                str(lat), str(course), str(true_heading), str(ts), str(smi), str(spare), str(raim), str(rstatus)]
    return response