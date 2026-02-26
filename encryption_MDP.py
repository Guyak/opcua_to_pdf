from cryptography.fernet import Fernet
from getpass import getpass
import json
from util_pyinstaller import *

# Charger la clé
key_file = resource_path("_key.bin")
with open(key_file, "rb") as f:
    key = f.read()

cipher = Fernet(key)

password = getpass("Nouveau mot de passe OPC UA : ")

enc_pwd = cipher.encrypt(password.encode()).decode()

data = {"password_enc": enc_pwd}

with open("_config.enc", "w") as f:
    json.dump(data, f, indent=2)

print("Mot de passe chiffré et enregistré.")
