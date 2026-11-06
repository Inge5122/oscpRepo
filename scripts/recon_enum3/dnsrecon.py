#!/usr/bin/env python
import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import time
import argparse
import pathlib

# Documentación de Scripts NSE
# En ejecución:
# dns-cache-snoop: Realiza espionaje de caché DNS (cache snooping)            dns-cache-snoop.mode=timed,dns-cache-snoop.domains={host1,host2,host3}
# dns-check-zone: Comprueba la configuración de zona DNS frente a buenas prácticas dns-check-zone.domain=ejemplo.com
# dns-ip6-arpa-scan: Realiza búsqueda inversa de IPv6 mediante técnica especial  prefix=2001:0DB8::/48
# dns-nsec-enum: Enumera DNS mediante la técnica de recorrido DNSSEC NSEC        dns-nsec-enum.domains=ejemplo.com
# dns-nsec3-enum: Intenta enumerar nombres de dominio en servidores compatibles con DNSSEC NSEC3 dns-nsec3-enum.domains=ejemplo.com
# dns-nsid: Obtiene información de DNS solicitando ID de nameserver y sus valores id.server y version.bind
# dns-random-srcport: Comprueba si el DNS tiene vulnerabilidad de recursión por puerto predecible
# dns-random-txid: Comprueba si el DNS tiene vulnerabilidad de recursión por TXID predecible
# dns-recursion: Comprueba si el DNS permite consultas recursivas para terceros
# dns-service-discovery: Intenta descubrir servicios del host objetivo mediante DNS
# dns-srv-enum: Enumera registros SRV comunes para un dominio dado               dns-srv-enum.domain='ejemplo.com'
# dns-update: Realiza actualización dinámica de DNS sin autenticación            dns-update.hostname=foo.ejemplo.com,dns-update.ip=192.0.2.1
# dns-zone-transfer: Solicita transferencia de zona desde servidor DNS           dns-zone-transfer.domain, dns-zone-transfer.server, dns-zone-transfer.port
# whois-domain: Consulta whois.iana.org

# No en ejecución:
# dns-blacklist: Comprueba IPs objetivo contra listas negras anti-spam de DNS
# dns-brute: Enumera subdominios por fuerza bruta
# dns-client-subnet-scan: Realiza búsqueda de dominios usando la opción edns-client-subnet
# dns-fuzz: Ataque de fuzzing contra DNS
# dns-zeustracker: Comprueba si el rango IP forma parte de la botnet Zeus

def doDNSNmapTCP():
    print("INFO: Iniciando dnsrecon con nmap para %s y TCP %s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-sT','-p',port,'--script','dns-cache-snoop,dns-check-zone,dns-ip6-arpa-scan,dns-nsec-enum,dns-nsec3-enum,dns-nsid,dns-random-srcport,dns-random-txid,dns-recursion,dns-service-discovery,dns-srv-enum,dns-update,dns-zone-transfer,whois-domain','--script-args','dns-check-zone.domain=%s,dns-nsec-enum.domains=%s,dns-nsec3-enum-domains=%s,dns-srv-enum.domain=%s,dns-zone-transfer.domain=%s' % (domain, domain, domain, domain, domain),'-oA','%s/%s_dns_TCP' % (BASE, ip_address),ip_address],encoding='utf8')
    print("INFO: Finalizado dnsrecon con nmap para %s y TCP %s" % (ip_address, port))
    return

def doDNSNmapUDP():
    print("INFO: Iniciando dnsrecon con nmap para %s y UDP %s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-sU','-p',port,'--script','dns-cache-snoop,dns-check-zone,dns-ip6-arpa-scan,dns-nsec-enum,dns-nsec3-enum,dns-nsid,dns-random-srcport,dns-random-txid,dns-recursion,dns-service-discovery,dns-srv-enum,dns-update,dns-zone-transfer,whois-domain','--script-args','dns-check-zone.domain=%s,dns-nsec-enum.domains=%s,dns-nsec3-enum-domains=%s,dns-srv-enum.domain=%s,dns-zone-transfer.domain=%s' % (domain, domain, domain, domain, domain),'-oA','%s/%s_dns_UDP' % (BASE, ip_address),ip_address],encoding='utf8')
    print("INFO: Finalizado dnsrecon con nmap para %s y UDP %s" % (ip_address, port))
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar enumeración básica de DNS. Uso: dnsrecon.py {--domain} target')
    parser.add_argument('target', help="IP objetivo")
    parser.add_argument('-d','--domain',help="Dominio objetivo")
    parser.add_argument('--port', default='53', help="Puerto, por defecto 53")

    args = parser.parse_args()

    ip_address = args.target
    port = args.port
    domain = args.domain

    BASE = '/root/scripts/recon_enum/results/exam/dns'
    mkdir_p(BASE)

    doDNSNmapTCP()
    doDNSNmapUDP()
