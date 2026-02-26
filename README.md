# opcua_to_pdf
Get values from an OPCUA server  and convert these to a PDF file

## Run
The following steps are used to run the program with **Windows 10 or 11** command bash

### Install the lastest python version
- Install the last version on [Python website](https://www.python.org/downloads/)
- Run the installer 
- Check the correct installation by looking at the installed version
```bash
py --version
> Python 3.13.5
```

### Install needed libraries
- General purpose libraries
```bash
py -m pip install rich
```
- For the OPCUA client
```bash
py -m pip install opcua
py -m pip install cryptography
```
- For the PDF generator
```bash
py -m pip install fpdf
```
Update the library via Git repository (needs git installed on the computer)
```bash
py -m pip install git+https://github.com/py-pdf/fpdf2.git@master
```
Remove a discontinued library to avoid having a warning every time the program starts
```
C:\Users\*USERNAME*\AppData\Local\Programs\Python\Python313\Lib\site-packages\fpdf\ttfonts.py
```
- For the CSV generation
```bash
py -m pip install pandas
```

### Complete the configuration file
- Fill the fields of _configEXAMPLE.json with needed informations
- Remove EXAMPLE in the file names to get *_config.json*

### Run the program
- Run **encryption_MDP.py** to generate the *_config.enc* file that will contain the password for your OPCUA session (see *_configEXAMPLE.enc*)
- Run **main.py** to run the program that will call needed sub-programs to create the different test reports with [FPDF](https://py-pdf.github.io/fpdf2/index.html)
```bash
py ./main.py
```
- It is also possible to double-click on **run_prog.bat** to start the program without entering the terminal
