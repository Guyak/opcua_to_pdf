# opcua_to_pdf
Get values from an OPCUA server  and convert these to a PDF file

## Run
The following steps are used to run the program with __**Windows 10**__ command bash

### Install the lastest python version
- Install the last version on (Python website)[https://www.python.org/downloads/]
- Run the installer 
- Check the correct installation by looking at the installed version
```bash
py --version
> Python 3.13.5
```

### Install needed libraries
- For the OPCUA client
```bash
py -m pip install opcua
```

### Complete the configuration file
- Fill the fields of _config_opcuaEXAMPLE.json with needed informations
- Remove EXAMPLE in the file names to get _config_opcua.json

### Run the program
- Run set_opcua.py to try writing/reading values from the server
```bash
py set_opcua.py
```
