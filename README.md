The API currently only runs on Python 3.9. Make sure to run the API using this version of Python as some packages used will not work with other versions of Python.  

Configure `config/dbConn.ini` file according to your database. 

remark: `theflyingdutchman.sql` file only adds the tables, not the database itself



Run API: `API_3.py`

remark: Endpoint SpoofShip won't work without the transmit-receive setup configured and actively running



For the data visualisation:

1. Ensure API is running
2. Database is set-up
3. Run `datavisualisation/dv.py`



Schemas -> Hold the JSON and XML Schemas used to verify the request data  
    JSON -> Has the JSON Schemas for all requests  
    XML -> Has the XSD files for all requests  
config -> The config files for secret key, db connection and API IP and port  
scripts -> Tools and functions used by the API for JSON XML etc  
AIS_TX.py -> The Python code that runs GNURadio and accepts a binary payload  
API_3 -> Holds the actual API 
