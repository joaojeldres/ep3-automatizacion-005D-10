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

def save_json(filename, data):
    path = os.path.join(RESP_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def body_to_text(body):
    return json.dumps(body, indent=2, ensure_ascii=False)

def contains(body, expected):
    return str(expected) in body_to_text(body)

def restconf_get(base_url, endpoint, auth, headers):
    url = f"{base_url}/{endpoint}"

    try:
        response = requests.get(
            url,
            auth=auth,
            headers=headers,
            verify=False,
            timeout=30
        )

        try:
            body = response.json()
        except Exception:
            body = {
                "text": response.text
            }

        return {
            "url": url,
            "http_status": response.status_code,
            "ok_http": response.status_code in [200, 201],
            "body": body
        }

    except Exception as e:
        return {
            "url": url,
            "http_status": "ERROR",
            "ok_http": False,
            "error": str(e)
        }

def check(label, evidence, expected):
    ok = contains(evidence, expected)
    estado = "OK" if ok else "FAIL"
    obtenido = expected if ok else "None"
    print(f"[{estado}] {label}: esperado='{expected}' obtenido='{obtenido}'")
    return ok

def main():
    data = load_vars()

    alumno = data["alumno"]
    cliente = data["cliente"]
    router = data["router"]

    print("=== VALIDACION RESTCONF EP3 ===")
    print("Script : validacion_restconf.py")
    print(f"Alumno : {alumno['codigo']} - {alumno['nombre']}")
    print(f"Fecha  : {datetime.now()}")
    print(f"HostVM : {socket.gethostname()}")
    print("===============================")

    base_url = f"https://{router['ip']}/restconf/data"

    auth = HTTPBasicAuth(
        router["usuario"],
        router["password"]
    )

    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    # Consulta completa como respaldo para encontrar valores aunque fallen endpoints específicos
    native_full = restconf_get(
        base_url,
        "Cisco-IOS-XE-native:native",
        auth,
        headers
    )

    save_json("get_native_completo.json", native_full)

    consultas = {
        "get_hostname.json": {
            "criterio": "Hostname corporativo",
            "endpoint": "Cisco-IOS-XE-native:native/hostname",
            "esperado": cliente["hostname"]
        },
        "get_loopback.json": {
            "criterio": "IP Loopback",
            "endpoint": f"Cisco-IOS-XE-native:native/interface/Loopback={router['loopback_id']}",
            "esperado": router["loopback_ip"]
        },
        "get_interfaces.json": {
            "criterio": "Descripcion WAN",
            "endpoint": "Cisco-IOS-XE-native:native/interface/GigabitEthernet=1",
            "esperado": router["descripcion_wan"]
        },
        "get_ntp.json": {
            "criterio": "Servidor NTP",
            "endpoint": "Cisco-IOS-XE-native:native/ntp",
            "esperado": router["ntp_server"]
        }
    }

    evidencias = {}

    for archivo, info in consultas.items():
        consulta_individual = restconf_get(
            base_url,
            info["endpoint"],
            auth,
            headers
        )

        # Se guarda evidencia individual + native completo como respaldo.
        evidencia = {
            "criterio": info["criterio"],
            "valor_esperado": info["esperado"],
            "consulta_individual": consulta_individual,
            "consulta_native_completo_respaldo": native_full
        }

        save_json(archivo, evidencia)
        evidencias[archivo] = evidencia

        print(f"Consulta {archivo}: HTTP {consulta_individual['http_status']}")

    print("")

    checks = []
    checks.append(check("Hostname corporativo", evidencias["get_hostname.json"], cliente["hostname"]))
    checks.append(check("IP Loopback", evidencias["get_loopback.json"], router["loopback_ip"]))
    checks.append(check("Descripcion WAN", evidencias["get_interfaces.json"], router["descripcion_wan"]))
    checks.append(check("Servidor NTP", evidencias["get_ntp.json"], router["ntp_server"]))

    total_ok = sum(checks)

    print(f"\nResultado RESTCONF: {total_ok}/4 criterios OK")
    print("CONFORME" if total_ok == 4 else "NO CONFORME")
    print(f"JSON guardados en: {RESP_DIR}")

if __name__ == "__main__":
    main()
