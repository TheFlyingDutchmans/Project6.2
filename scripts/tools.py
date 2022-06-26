import re

def sanitizeInput(input):
    input = str(input)
    filtered = re.sub('[^a-zA-Z0-9_\s]', '', input)
    return filtered