import base64
import json
import logging
from datetime import datetime
import requests
import random
import sys

def test_login(host, password):
    print(f"Tentativo di connessione al Tenda i29 su http://{host} ...")
    
    password_bytes = password.encode('utf-8')
    base64_password = base64.b64encode(password_bytes).decode('utf-8')

    now = datetime.now()
    time_str = f"{now.year};{now.month};{now.day};{now.hour};{now.minute};{now.second}"

    payload = {
        "sysLogin": {
            "username": "admin",
            "password": base64_password,
            "logoff": False,
            "timeZone": 12,
            "time": time_str
        }
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        rand_param = f"{random.random()}"
        response = requests.post(
            f"http://{host}/goform/modules?{rand_param}",
            headers=headers,
            json=payload,
            verify=False,
            allow_redirects=False,
            timeout=10
        )
        
        print("\n--- RISPOSTA DEL ROUTER ---")
        print(f"Status Code: {response.status_code}")
        print(f"Headers Risposta: {response.headers}")
        print(f"Cookie Ricevuti: {response.cookies.get_dict()}")
        print(f"Corpo della Risposta: {response.text[:500]}")
        print("---------------------------\n")

        if response.cookies:
            print("SUCCESSO! Il login funziona e ha restituito i cookie.")
        else:
            print("FALLIMENTO! Nessun cookie restituito.")
            
    except Exception as e:
        print(f"ERRORE DI CONNESSIONE: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python test_tenda.py <IP_ROUTER> <PASSWORD>")
    else:
        test_login(sys.argv[1], sys.argv[2])
