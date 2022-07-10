The API currently only runs on Python 3.9. Make sure to run the API using this version of Python as some packages used will not work with other versions of Python.

The following instructions assume that you use this project on an Ubuntu machine.  
If you don't already have the pip3 package manager installed, you can install it with the following command:

```sudo apt-get install python3-pip```

The required pip packages can be installed using the following command:  
`pip3 install jsonschema mysql-connector flask textwrap3 configparser mysql-connector re101 lxml Xmlify`  


Configure `config/dbConn.ini` file according to your database. 

remark: `theflyingdutchman.sql` file only adds the tables, not the database itself  

Run API: `API_3.py`

Remark: Endpoint SpoofShip won't work without the transmit-receive setup configured and actively running

The API documentation can be found <a href="https://documenter.getpostman.com/view/15601673/Uz5KjtTz">here</a>.

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
