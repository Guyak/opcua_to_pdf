from opcua import Client, ua
from json import load as j_load
import time
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
    print(f"Could not connect, closing program...")
    sys.exit(1)

print(f"Connected !")

##————————————————————————————————————————————————————————————————————————————##
## Reading/Writing values of the server


# nodeBool = client.get_node(f'ns=2;s=Local HMI.Tags.test_bool')
# nodeString = client.get_node(f'ns=2;s=Local HMI.Tags.test_string')

# switch = nodeBool.get_value()
# if switch:
    # nodeBool.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
    # nodeString.set_value(ua.DataValue(ua.Variant(f'Mis à faux - Date : {time.strftime("%Y-%m-%d_%H-%M-%S")}', ua.VariantType.String)))
# else :
    # nodeBool.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
    # nodeString.set_value(ua.DataValue(ua.Variant(f"Mis à vrai - Date : {time.strftime("%Y-%m-%d_%H-%M-%S")}", ua.VariantType.String)))
# print(nodeString.get_value())

nodeInt16 = client.get_node(f'ns=2;s=API_425056.Tags.Recette.GEN.Limite_Couple')
print(f'Limite_Couple à {time.strftime("%Y-%m-%d_%H-%M-%S")} : {nodeInt16.get_value()}')

nodeUInt16 = client.get_node(f'ns=2;s=API_425056.Tags.Recette.VIDE.Tension_Accept_1')
print(f'Tension_Accept_1 à {time.strftime("%Y-%m-%d_%H-%M-%S")} : {nodeUInt16.get_value()/10}')

##————————————————————————————————————————————————————————————————————————————##
## Disconnecting from the server

client.disconnect()
print(f"Disconnected")
