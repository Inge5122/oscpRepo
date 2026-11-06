#!/usr/bin/env python
import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import pathlib
import argparse

# Documentación de Scripts NSE
# En ejecución:
# broadcast-ataoe-discover: descubre servidores compatibles con ATA sobre Ethernet. Requiere "-e <interfaz>"
# broadcast-bjnp-discover: descubre impresoras/escáneres Canon compatibles con BJNP
# broadcast-db2-discover: intenta descubrir servidores DB2 en la red enviando broadcast a UDP 523
# broadcast-dhcp-discover: envía solicitud DHCP a la dirección broadcast y reporta los resultados
# broadcast-dhcp6-discover: envía solicitud DHCPv6 a multicast e imprime la dirección con sus opciones
# broadcast-dns-service-discovery: descubre servicios de hosts usando el protocolo DNS Service Discovery
# broadcast-dropbox-listener: escucha transmisiones de sincronización LAN de clientes Dropbox (ya cubierto por broadcast-listener)
# broadcast-eigrp-discovery: descubre mediante EIGRP de CISCO; requiere valor de AS o se pondrá a la escucha
# broadcast-igmp-discovery: descubre objetivos con membresías IGMP Multicast y obtiene información de interés
# broadcast-listener: captura tráfico broadcast e intenta decodificar paquetes recibidos: CDP, HSRP, Spotify, DropBox, DHCP, ARP y más
# broadcast-ms-sql-discover: versión broadcast que utiliza descubrimiento únicamente mediante SQL Server Browser service
# broadcast-netbios-master-browser: intenta descubrir el master browser y los dominios que gestiona
# broadcast-networker-discover: descubre servidores de respaldo EMC Networker mediante consulta broadcast
# broadcast-novell-locate: intenta usar Service Location Protocol para descubrir servidores Novell NetWare Core Protocol (NCP)
# broadcast-ospf2-discover: descubre redes IPv4 usando OSPFv2, capturando paquetes OSPF Hello y respondiendo
# broadcast-pc-anywhere: envía un broadcast especial para comprobar hosts PC Anywhere
# broadcast-pc-duo: descubre hosts de control remoto y pasarelas PC-DUO enviando sondeo broadcast
# broadcast-pim-discovery: descubre enrutadores que ejecutan PIM (Protocol Independent Multicast)
# broadcast-ping: envía pings broadcast y muestra las direcciones IP y MAC de los equipos que responden
# broadcast-pppoe-discover: descubre servidores PPPoE mediante el protocolo PPPoE Discovery
# broadcast-rip-discover: descubre hosts y enrutamiento usando RIPv2. Envía solicitud RIPv2 y recopila respuestas
# broadcast-ripng-discover: descubre hosts e información de enrutamiento de dispositivos que ejecutan RIPng
# broadcast-sonicwall-discover: descubre firewalls Sonicwall usando el mismo método que SetupTool del fabricante
# broadcast-sybase-asa-discover: descubre servidores Sybase Anywhere en la red local
# broadcast-tellstick-discover: descubre dispositivos Telldus Technologies TellStickNet
# broadcast-upnp-info: intenta extraer información del sistema desde el servicio UPnP enviando multicast y recolectando
# broadcast-versant-locate: descubre bases de datos orientadas a objetos Versant usando broadcast srvloc
# broadcast-wake-on-lan: despierta un sistema remoto mediante paquete WoL
# broadcast-wpad-discover: recupera una lista de servidores proxy en la LAN mediante WPAD por métodos DHCP y DNS
# broadcast-wsdd-discover: descubrimiento multicast compatible con el protocolo Web Services Dynamic Discovery
# broadcast-xdmcp-discover: descubre servidores que ejecutan XDMCP
# url-snarf: captura tráfico HTTP en la interfaz y extrae URLs
# targets-sniffer: analiza la interfaz en busca de direcciones IP
# lltd-discovery: utiliza el protocolo LLTD de Microsoft para descubrir hosts en la red local

# No en ejecución:
# broadcast-avahi-dos: explota denegación de servicio (DoS)
# broadcast-jenkins-discover:  #### NO EXISTE EN KALI #### Descubre Jenkins en una LAN mediante sondeo broadcast
# broadcast-hid-discoveryd:  #### NO EXISTE EN KALI #### Descubre dispositivos HID mediante sondeo broadcast discoveryd
# llmnr-resolve: resuelve un nombre de host usando LLMNR. Requiere -script-arg llmnr-resolve.hostname=nombre_ejemplo
def doNmap(interface):
    print("INFO: Realizando descubrimiento broadcast con nmap en la interfaz: %s" % (interface))
    subprocess.check_output(['nmap','-vv','--script=broadcast-ataoe-discover,broadcast-bjnp-discover,broadcast-db2-discover,broadcast-dhcp-discover,broadcast-dhcp6-discover,broadcast-dns-service-discovery,broadcast-dropbox-listener,broadcast-eigrp-discovery,broadcast-igmp-discovery,broadcast-listener,broadcast-ms-sql-discover,broadcast-netbios-master-browser,broadcast-networker-discover,broadcast-novell-locate,broadcast-ospf2-discover,broadcast-pc-anywhere,broadcast-pc-duo,broadcast-pim-discovery,broadcast-ping,broadcast-pppoe-discover,broadcast-rip-discover,broadcast-ripng-discover,broadcast-sonicwall-discover,broadcast-sybase-asa-discover,broadcast-tellstick-discover,broadcast-upnp-info,broadcast-versant-locate,broadcast-wake-on-lan,broadcast-wpad-discover,broadcast-wsdd-discover,broadcast-xdmcp-discover,url-snarf,targets-sniffer,lltd-discovery','-oA','%s/%s_broadcast' % (BASE,interface),'-e',interface])
    print("INFO: Descubrimiento broadcast con nmap completado en la interfaz: %s" % (interface))
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar scripts de reconocimiento broadcast en Nmap. Uso: broadcastrecon.py interfaz')
    parser.add_argument('interface', help="Interfaz sobre la cual enumerar o escuchar")

    args = parser.parse_args()

    interface = args.interface

    BASE = '/root/scripts/recon_enum/results/exam/nmap'
    mkdir_p(BASE)

    doNmap(interface)
