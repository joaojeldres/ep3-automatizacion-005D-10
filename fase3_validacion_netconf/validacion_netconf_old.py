#!/usr/bin/env python3
import os
import socket
import yaml
from datetime import datetime
from lxml import etree
from ncclient import manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VARS_FILE = os.path.join(BASE_DIR, "../vars/vars_005D-10.yaml")
EVID_DIR = os.path.join(BASE_DIR, "evidencias")
RAW_XML = os.path.join(EVID_DIR, "rpc_reply_raw.xml")

os.makedirs(EVID_DIR, exist_ok=True)

def load_vars():
    with open(VARS_FILE, "r") as f:
        return yaml.safe_load(f)

def local_name(element):
    return etree.QName(element).localname

def find_child_text(parent, child_name):
    for child in parent:
        if local_name(child) == child_name and child.text:
            return child.text.strip()
    return None

def find_interface(root, interface_type, interface_id):
    for elem in root.iter():
        if local_name(elem) == interface_type:
            name = find_child_text(elem, "name")
            if name == str(interface_id):
                return elem
    return None

def find_any_text(root, expected):
    for elem in root.iter():
        if elem.text and elem.text.strip() == str(expected):
            return elem.text.strip()
    return None

def find_first_text_by_name(parent, wanted_name):
    for elem in parent.iter():
        if local_name(elem) == wanted_name and elem.text:
            return elem.text.strip()
    return None

def print_result(label, actual, expected):
    ok = str(actual) == str(expected)
    status = "OK" if ok else "FAIL"
    print(f"[{status}] {label}: esperado='{expected}' obtenido='{actual}'")
    return ok

def main():
    data = load_vars()
    router = data["router"]
    cliente = data["cliente"]

    print("=== VALIDACION NETCONF EP3 ===")
    print(f"Script : validacion_netconf.py")
    print(f"Alumno : {data['alumno']['codigo']} - {data['alumno']['nombre']}")
    print(f"Fecha  : {datetime.now()}")
    print(f"HostVM : {socket.gethostname()}")
    print("==============================")

    filter_xml = """
    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>
    </filter>
    """

    with manager.connect(
        host=router["ip"],
        port=830,
        username=router["usuario"],
        password=router["password"],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        device_params={"name": "csr"}
    ) as m:
        reply = m.get_config(source="running", filter=("subtree", filter_xml))

    raw = str(reply)
    with open(RAW_XML, "w") as f:
        f.write(raw)

    root = etree.fromstring(raw.encode())

    hostname = find_first_text_by_name(root, "hostname")

    loopback = find_interface(root, "Loopback", router["loopback_id"])
    loopback_ip = find_any_text(loopback, router["loopback_ip"]) if loopback is not None else None
    loopback_mask = find_any_text(loopback, router["loopback_mask"]) if loopback is not None else None

    gigabit = find_interface(root, "GigabitEthernet", "1")
    descripcion_wan = find_any_text(gigabit, router["descripcion_wan"]) if gigabit is not None else None

    ntp_server = find_any_text(root, router["ntp_server"])

    checks = []
    checks.append(print_result("Hostname corporativo", hostname, cliente["hostname"]))
    checks.append(print_result("IP Loopback", loopback_ip, router["loopback_ip"]))
    checks.append(print_result("Mascara Loopback", loopback_mask, router["loopback_mask"]))
    checks.append(print_result("Descripcion WAN", descripcion_wan, router["descripcion_wan"]))
    checks.append(print_result("Servidor NTP", ntp_server, router["ntp_server"]))

    total_ok = sum(checks)
    print(f"\nResultado NETCONF: {total_ok}/5 criterios OK")
    print("CONFORME" if total_ok == 5 else "NO CONFORME")
    print(f"XML guardado en: {RAW_XML}")

if __name__ == "__main__":
    main()
