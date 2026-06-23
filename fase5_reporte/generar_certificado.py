#!/usr/bin/env python3
import os
import socket
import yaml
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

VARS_FILE = os.path.join(ROOT_DIR, "vars", "vars_005D-10.yaml")

NETCONF_OUT = os.path.join(
    ROOT_DIR,
    "fase3_validacion_netconf",
    "evidencias",
    "output_validacion_netconf.txt"
)

RESTCONF_OUT = os.path.join(
    ROOT_DIR,
    "fase4_validacion_restconf",
    "evidencias",
    "output_validacion_restconf.txt"
)

DIFF_DIR = os.path.join(
    BASE_DIR,
    "evidencias",
    "diff_005D-10"
)

SNAPSHOT_DIR = os.path.join(
    BASE_DIR,
    "evidencias",
    "snapshot_final_005D-10"
)

CERT_FILE = os.path.join(
    BASE_DIR,
    "evidencias",
    "certificado_compliance_005D-10.txt"
)

DIFF_TXT = os.path.join(
    BASE_DIR,
    "evidencias",
    "diff_baseline_final.txt"
)


def leer_archivo(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", errors="ignore") as f:
        return f.read()


def cargar_vars():
    with open(VARS_FILE, "r") as f:
        return yaml.safe_load(f)


def carpeta_tiene_archivos(path):
    if not os.path.isdir(path):
        return False

    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.getsize(full_path) > 0:
                return True

    return False


def listar_archivos(path):
    encontrados = []
    if not os.path.isdir(path):
        return encontrados

    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            encontrados.append(os.path.relpath(full_path, BASE_DIR))

    return encontrados


def main():
    data = cargar_vars()

    alumno = data["alumno"]
    cliente = data["cliente"]
    router = data["router"]

    netconf_text = leer_archivo(NETCONF_OUT)
    restconf_text = leer_archivo(RESTCONF_OUT)

    netconf_ok = "5/5" in netconf_text and "CONFORME" in netconf_text
    restconf_ok = "4/4" in restconf_text and "CONFORME" in restconf_text
    snapshot_ok = carpeta_tiene_archivos(SNAPSHOT_DIR)
    diff_ok = carpeta_tiene_archivos(DIFF_DIR)

    compliance_ok = netconf_ok and restconf_ok and snapshot_ok and diff_ok

    estado_final = "CONFORME" if compliance_ok else "NO CONFORME"

    archivos_diff = listar_archivos(DIFF_DIR)

    with open(DIFF_TXT, "w") as f:
        f.write("DIFF BASELINE VS SNAPSHOT FINAL\n")
        f.write("===============================\n\n")
        f.write("Estado del diff: {}\n".format(
            "CON DIFERENCIAS DETECTADAS" if diff_ok else "SIN DIFERENCIAS O NO GENERADO"
        ))
        f.write("\nArchivos generados por Genie diff:\n")
        for archivo in archivos_diff:
            f.write(f"- {archivo}\n")

    certificado = f"""CERTIFICADO DE COMPLIANCE EP3
================================

Alumno:
  Codigo : {alumno['codigo']}
  Nombre : {alumno['nombre']}

Cliente:
  Empresa  : {cliente['empresa']}
  Hostname : {cliente['hostname']}

Router:
  IP de gestion        : {router['ip']}
  Usuario              : {router['usuario']}
  Loopback gestion     : Loopback{router['loopback_id']}
  IP Loopback          : {router['loopback_ip']}/{router['loopback_prefix']}
  Mascara Loopback     : {router['loopback_mask']}
  Descripcion WAN      : {router['descripcion_wan']}
  Banner de acceso     : {router['banner']}
  Servidor NTP         : {router['ntp_server']}

Validaciones:
  NETCONF              : {'CONFORME' if netconf_ok else 'NO CONFORME'}
  RESTCONF             : {'CONFORME' if restconf_ok else 'NO CONFORME'}
  Snapshot final Genie : {'CONFORME' if snapshot_ok else 'NO CONFORME'}
  Diff Genie           : {'CON DIFERENCIAS DETECTADAS' if diff_ok else 'NO CONFORME'}

Resultado final de compliance:
  {estado_final}

Metadatos:
  Fecha de ejecucion   : {datetime.now()}
  Host VM              : {socket.gethostname()}

Observacion:
  El router fue aprovisionado mediante Ansible y validado posteriormente mediante NETCONF y RESTCONF.
  El snapshot final y el diff de Genie permiten comparar el estado inicial contra el estado final del equipo.
"""

    with open(CERT_FILE, "w") as f:
        f.write(certificado)

    print(certificado)
    print(f"Certificado generado en: {CERT_FILE}")
    print(f"Resumen diff generado en: {DIFF_TXT}")


if __name__ == "__main__":
    main()
