#!/usr/bin/env python3
import os
import json
import socket
import yaml
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VARS_FILE = os.path.join(BASE_DIR, "../vars/vars_005D-10.yaml")
EVID_DIR = os.path.join(BASE_DIR, "evidencias")
RESP_DIR = os.path.join(EVID_DIR, "responses")

os.makedirs(EVID_DIR, exist_ok=True)
os.makedirs(RESP_DIR, exist_ok=True)

def load_vars():
    with open(VARS_FILE, "r") as f:
        return yaml.safe_load(f)

def save_response(filename, data):
    path = os.path.join(RESP_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def recursive_contains(obj, expected):
    expected = str(expected)
    if isinstance(obj, dict):
        return any(recursive_contains(v, expected) for v in obj.values())
    if isinstance(obj, list):
        return any(recursive_contains(v, expected) for v in obj)
    return expected in str(obj)

def get_restconf(base_url, endpoint, auth, headers):
    url = f"{base_url}/{endpoint}"
    response = requests.get(
        url,
        auth=auth,
        headers=headers,
        verify=False,
        timeout=20
    )

    try:
        body = response.json()
    except Exception:
        body = {
            "status_code": response.status_code,
            "text": response.text
        }

    return response.status_code, body

def check(label, body, expected):
    ok = recursive_contains(body, expected)
    estado = "OK" if ok else "FAIL"
    obtenido = expected if ok else "None"
    print(f"[{estado}] {label}: esperado='{expected}' obtenido='{obtenido}'")
    return ok

def main():
    data = load_vars()
    router = data["router"]
    cliente = data["cliente"]

    print("=== VALIDACION RESTCONF EP3 ===")
    print("Script : validacion_restconf.py")
    print(f"Alumno : {data['alumno']['codigo']} - {data['alumno']['nombre']}")
    print(f"Fecha  : {datetime.now()}")
    print(f"HostVM : {socket.gethostname()}")
    print("===============================")

    base_url = f"https://{router['ip']}/restconf/data"
    auth = HTTPBasicAuth(router["usuario"], router["password"])
    headers = {
        "Accept": "application/yang-data+json"
    }

    endpoints = {
        "hostname": "Cisco-IOS-XE-native:native/hostname",
        "loopback": f"ietf-interfaces:interfaces/interface=Loopback{router['loopback_id']}",
        "wan": "ietf-interfaces:interfaces/interface=GigabitEthernet1",
        "ntp": "Cisco-IOS-XE-native:native/ntp"
    }

    responses = {}

    for name, endpoint in endpoints.items():
        status_code, body = get_restconf(base_url, endpoint, auth, headers)
        responses[name] = body
        save_response(f"get_{name}.json", body)
        print(f"Consulta {name}: HTTP {status_code}")

    print("")

    checks = []
    checks.append(check("Hostname corporativo", responses["hostname"], cliente["hostname"]))
    checks.append(check("IP Loopback", responses["loopback"], router["loopback_ip"]))
    checks.append(check("Descripcion WAN", responses["wan"], router["descripcion_wan"]))
    checks.append(check("Servidor NTP", responses["ntp"], router["ntp_server"]))

    total_ok = sum(checks)

    print(f"\nResultado RESTCONF: {total_ok}/4 criterios OK")
    print("CONFORME" if total_ok == 4 else "NO CONFORME")
    print(f"JSON guardados en: {RESP_DIR}")

if __name__ == "__main__":
    main()
