#!/usr/bin/env python3
import os
import socket
import yaml
from datetime import datetime
from ncclient import manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VARS_FILE = os.path.join(BASE_DIR, "../vars/vars_005D-10.yaml")
EVID_DIR = os.path.join(BASE_DIR, "evidencias")
RAW_XML = os.path.join(EVID_DIR, "rpc_reply_raw.xml")

os.makedirs(EVID_DIR, exist_ok=True)

def load_vars():
    with open(VARS_FILE, "r") as f:
        return yaml.safe_load(f)

def check(label, raw_xml, expected):
    ok = str(expected) in raw_xml
    estado = "OK" if ok else "FAIL"
    obtenido = expected if ok else "None"
    print(f"[{estado}] {label}: esperado='{expected}' obtenido='{obtenido}'")
    return ok

def main():
    data = load_vars()
    router = data["router"]
    cliente = data["cliente"]

    print("=== VALIDACION NETCONF EP3 ===")
    print("Script : validacion_netconf.py")
    print(f"Alumno : {data['alumno']['codigo']} - {data['alumno']['nombre']}")
    print(f"Fecha  : {datetime.now()}")
    print(f"HostVM : {socket.gethostname()}")
    print("==============================")

    # OJO: aquí NO va el tag <filter>, ncclient lo agrega solo.
    native_filter = """
    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>
    """

    with manager.connect(
        host=router["ip"],
        port=830,
        username=router["usuario"],
        password=router["password"],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        device_params={"name": "csr"},
        timeout=60
    ) as m:
        reply = m.get_config(source="running", filter=("subtree", native_filter))

    raw = str(reply)

    with open(RAW_XML, "w") as f:
        f.write(raw)

    checks = []
    checks.append(check("Hostname corporativo", raw, cliente["hostname"]))
    checks.append(check("IP Loopback", raw, router["loopback_ip"]))
    checks.append(check("Mascara Loopback", raw, router["loopback_mask"]))
    checks.append(check("Descripcion WAN", raw, router["descripcion_wan"]))
    checks.append(check("Servidor NTP", raw, router["ntp_server"]))

    total_ok = sum(checks)

    print(f"\nResultado NETCONF: {total_ok}/5 criterios OK")
    print("CONFORME" if total_ok == 5 else "NO CONFORME")
    print(f"XML guardado en: {RAW_XML}")

if __name__ == "__main__":
    main()
