#!/usr/bin/python

import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import pathlib
import argparse

# El ping de nmap envía 0 datos por defecto (fácilmente detectable)
# POR HACER (TODO): añadir opciones para --data <cadena hex>, --data-string <cadena>, o --data-length <número>

def alive_hosts(target_hosts):
    print("INFO: Realizando barrido de ping sobre %s" % (target_hosts))
    output_file = "/root/scripts/recon_enum/results/exam/targets.txt"
    f = open(output_file, 'w')
    if not os.path.isdir('/root/scripts/recon_enum/results/exam/nmap'):
        os.makedirs('/root/scripts/recon_enum/results/exam/nmap')
    lines = subprocess.check_output(['nmap','-n','-sn',target_hosts,'-oA','%s/%s_HOST_DISCOVERY' % (BASE,target_hosts)],encoding='utf8').split("\n")
    live_hosts = 0
    for line in lines:
        line = line.strip()
        line = line.rstrip()
        if ("Nmap scan report for" in line):
            ip_address = line.split(" ")[4]
            if (live_hosts > 0):
                f.write('\n')
            f.write("%s" % (ip_address))
            live_hosts += 1
    print("INFO: Escaneo de hosts completado. Objetivos adquiridos.")
    f.close()
    return

# Documentación de Scripts NSE
# En ejecución:
# targets-ipv6-multicast-echo: Envía eco ICMPv6 a la dirección link-local de todos los nodos ff02::1 --script-args newtargets,interface=, puede requerir -sL
# targets-ipv6-multicast-invalid-dst: Envía ICMPv6 con extensión inválida a link-local (ff02::1) para provocar respuestas en Windows. --script-args 'newtargets,interface=', puede requerir -sP
# targets-ipv6-multicast-mld: Envía consulta MLD a link-local (ff02::1) con tiempo de respuesta 1 para provocar respuesta inmediata. --script-args 'newtargets,interface='

# No en ejecución:
# targets-asn: Lista de prefijos IP para un número AS de enrutamiento dado --script-args targets-asn.asn=
# targets-ipv6-map4to6: Se ejecuta en pre-escaneo para mapear IPv4 a IPv6 y añadirlos al escaneo. Los 4 bytes inferiores de IPv6 se reemplazan con la dirección IPv4. --script-args targets-ipv6-map4to6.IPv4Hosts={},targets-ipv6-subnet={}
# targets-ipv6-multicast-slaac: Envía anuncio de router ICMPv6 con prefijo aleatorio para que hosts inicien SLAAC. --script-args 'newtargets,interface='
# targets-ipv6-wordlist: Añade direcciones IPv6 a la cola de escaneo usando lista de 'palabras' hexadecimales que forman direcciones en una subred dada. --script-args targets-ipv6-wordlist.wordlist,targets-ipv6-wordlists.nsegments,targets-ipv6-wordliss.fillright,targets-ipv6-subnet
def alive_hosts6(interface):
    print("INFO: Realizando pings y multicast IPv6")
    subprocess.check_output(['nmap','-6','-n','--script','targets-ipv6-multicast-echo,targets-ipv6-multicast-invalid-dst,targets-ipv6-multicast-mld','--script-args','interface=%s' % interface,'-oA','%s/%s_HOST_DISCOVERY_IPv6' % (BASE,interface)],encoding='utf8')
    print("INFO: Pings y multicast IPv6 completados. ¡Añade los hosts a targets manualmente!")
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para la adquisición inicial de objetivos. Si se especifica interfaz, también se realizará nmap IPv6. Uso: aliverecon.py {-i interfaz} rango_ip')
    parser.add_argument('ip_range', help="Rango de IPs objetivo. Comúnmente el último octeto: 10.10.10.0-255")
    parser.add_argument('-i', dest='interface', default="", help="Interfaz sobre la cual enumerar IPv6")

    args = parser.parse_args()

    target_hosts = args.ip_range
    interface = args.interface

    BASE = '/root/scripts/recon_enum/results/exam/nmap'
    mkdir_p(BASE)

    alive_hosts(target_hosts)
    if interface != "":
        alive_hosts6(interface)
