# EP3 - Implementación de Automatización de Red con Compliance Auditado

## 1. Objetivo del proyecto

El objetivo del proyecto fue incorporar y estandarizar un router Cisco CSR1000v para la empresa Agricola Central SA, aplicando configuración corporativa mediante automatización de red y dejando evidencia auditable en GitHub.

## 2. Alcance

El trabajo considera la documentación del estado inicial del router, aprovisionamiento automatizado con Ansible, validación independiente mediante NETCONF, validación mediante RESTCONF y generación de un certificado final de compliance.

El alcance técnico incluye hostname corporativo, banner de acceso, servidor NTP, descripción de interfaz WAN, interfaz Loopback de gestión, habilitación de NETCONF, habilitación de RESTCONF y servidor HTTP seguro.

## 3. Infraestructura utilizada

| Elemento | Descripción |
|---|---|
| DEVASC VM | Estación de trabajo usada para ejecutar scripts, Ansible, Genie, NETCONF y RESTCONF |
| CSR1000v | Router virtual configurado y validado |
| IP CSR1000v | 192.168.56.101 |
| Usuario | cisco |
| Repositorio | ep3-automatizacion-005D-10 |

## 4. Tecnologías empleadas

| Tecnología | Uso |
|---|---|
| Git / GitHub | Control de versiones y auditoría |
| pyATS / Genie | Captura de baseline, snapshot final y diff |
| Ansible | Aprovisionamiento automatizado e idempotente |
| NETCONF / ncclient | Validación independiente en XML |
| RESTCONF / requests | Validación independiente en JSON/HTTPS |
| Python | Automatización de validaciones y certificado |

## 5. Configuración aplicada

| Parámetro | Valor |
|---|---|
| Código alumno | 005D-10 |
| Alumno | Jeldres Molinett Joao Franco |
| Empresa cliente | Agricola Central SA |
| Hostname corporativo | RTR-AGRICEN |
| IP de gestión CSR | 192.168.56.101 |
| Loopback de gestión | Loopback10 |
| IP Loopback | 10.5.10.1 |
| Máscara Loopback | 255.255.255.0 |
| Descripción WAN | Enlace-WAN-Talca |
| Banner | ACCESO RESTRINGIDO - AGRICEN |
| Servidor NTP | 8.8.8.8 |
| NETCONF | Habilitado |
| RESTCONF | Habilitado |
| HTTP seguro | Habilitado |

## 6. Resultados de validación

| Validación | Resultado |
|---|---|
| Baseline inicial pyATS/Genie | Generado |
| Aprovisionamiento Ansible | Ejecutado correctamente |
| Segunda ejecución Ansible | Idempotente |
| NETCONF | 5/5 criterios OK - CONFORME |
| RESTCONF | 4/4 criterios OK - CONFORME |
| Snapshot final Genie | Generado |
| Diff baseline vs final | Generado con diferencias detectadas |
| Certificado compliance | CONFORME |

## 7. Conclusiones

El router CSR1000v fue configurado correctamente con los parámetros corporativos asignados para Agricola Central SA. La configuración fue aplicada mediante Ansible y validada de forma independiente mediante NETCONF y RESTCONF.

El resultado final del proceso es CONFORME, por lo que el equipo queda listo para ser entregado a operación. Todas las evidencias del proceso quedaron registradas en el repositorio GitHub para auditoría.
