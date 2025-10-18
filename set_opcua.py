from opcua import Client, ua
from json import load as j_load
import sys

##————————————————————————————————————————————————————————————————————————————##
## Loading configuration file

config_file = "_config_opcua.json"
with open(config_file) as file:
    credentials = j_load(file)

##————————————————————————————————————————————————————————————————————————————##
## Setting up server URL and connecting to it

url = credentials["server_url"]
client = Client(url)
client.session_timeout = 30000
print(f'Trying to connect to "{url}"...')
try:
    client.connect()
except ConnectionRefusedError:
    print("Could not connect, closing program...")
    sys.exit(1)

print(f"Connected !")

##————————————————————————————————————————————————————————————————————————————##
## Reading/Writing values of the server

nodeBool = client.get_node('ns=2;s=Local HMI.Tags.test_bool')
nodeString = client.get_node('ns=2;s=Local HMI.Tags.test_string')

switch = nodeBool.get_value()
if switch:
    nodeBool.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
    nodeString.set_value(ua.DataValue(ua.Variant("Maintenant c'est faux", ua.VariantType.String)))
else :
    nodeBool.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
    nodeString.set_value(ua.DataValue(ua.Variant("Maintenant c'est vrai", ua.VariantType.String)))
print(nodeString.get_value())

##————————————————————————————————————————————————————————————————————————————##
## Disconnecting from the server

client.disconnect()
print("Disconnected")