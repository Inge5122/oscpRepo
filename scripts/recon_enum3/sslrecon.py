#!/usr/bin/python

import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import time
import argparse
import pathlib

# Más información: https://github.com/nmap/nmap/tree/master/scripts

# Documentación de Scripts NSE
# En ejecución:
# ssl-cert-intaddr: Reporta direcciones IPv4 privadas encontradas en el certificado
# ssl-cert: Obtiene el certificado SSL del servidor. El nivel de detalle depende de -v o -vv
# ssl-heartbleed: Detección de OpenSSL Heartbleed (CVE-2014-0160) basada en ssltest.py
# ssl-poodle: Comprueba cifrados CBC en SSLv3 (POODLE CVE-2014-3566)
# sslv2-drown: Comprueba SSLv2, CVE-2015-3197, CVE-2016-0703, CVE-2016-0800 (DROWN)
# tls-nextprotoneg: Enumera los protocolos compatibles en un servidor TLS
# tls-alpn: Enumera protocolos de capa de aplicación compatibles mediante ALPN

# No en ejecución:
# ssl-ccs-injection: Requiere tls.lua. Comprueba vulnerabilidad CCS CVE-2014-0224 (MitM)
# ssl-date: Obtiene fecha y hora del host objetivo mediante TLS ServerHello
# ssl-dh-params: Detección de parámetros Diffie-Hellman débiles
# ssl-enum-ciphers: Inicia repetidamente conexiones SSLv3/TLS probando diferentes suites de cifrado
# ssl-known-key: Comprueba si la huella del certificado figura en listas de claves comprometidas
# sslv2: Comprueba si soporta SSLv2 y qué cifrados
# sstp-discover: Comprueba si soporta Secure Socket Tunneling Protocol

def doNmap():
    print("INFO: Iniciando sslrecon con nmap para %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','banner,ssl-cert-intaddr,ssl-cert,ssl-heartbleed,ssl-poodle,sslv2-drown,tls-nextprotoneg,tls-alpn','-oA','%s/%s_%s_ssl' % (BASE, ip_address, port),ip_address],encoding='utf8')
    print("INFO: Finalizado sslrecon con nmap para %s:%s" % (ip_address, port))
    return

# --xml_out=XML_FILE        escribe resultados en documento XML
# --targets_in=TARGETS_IN   lee lista de objetivos: host:puerto por línea
# --https_tunnel            túnel a través de proxy: http://USER:PW@HOST:PORT
# --starttls                ejecuta StartTLS: smtp, xmpp, xmpp_server, pop3, ftp, imap, ldap, rdp, postgres, auto
# --quiet                   oculta salida estándar
# --regular                 atajo para --slv2 --sslv3 --tlsv1 --tlsv1_1 --tlsv1_2 --regen --resum --certinfo=basic --http_get --hide_rejected_ciphers --compression -heartbleed
# --certinfo                no requiere valor
def doSslyze():
    print("INFO: Iniciando sslyze para %s:%s" % (ip_address, port))
    sslyze_outfile = "%s/%s_%s_sslyze" % (BASE,ip_address,port)
    try:
        subprocess.run(['sslyze','--regular','--certinfo','%s:%s' % (ip_address,port)],encoding='utf8',stdout=sslyze_outfile)
    except Exception as e:
        print(type(e))
        print("Error inesperado en doSslyze en SSLrecon")
    print("INFO: Finalizado sslyze para %s:%s" % (ip_address, port))
    return

# --targets=<archivo>
# --show-certificate
def doSslscan():
    print("INFO: Iniciando sslscan para %s:%s" % (ip_address, port))
    sslscan_outfile = "%s/%s_%s_sslscan" % (BASE,ip_address,port)
    try:
        subprocess.run(['sslscan','--show-certificate','--no-color','%s:%s' % (ip_address,port)],encoding='utf8',stdout=sslscan_outfile)
    except Exception as e:
        print(type(e))
        print("Error inesperado en doSslscan en SSLRecon")
    print("INFO: Finalizado sslscan para %s:%s" % (ip_address, port))
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para gestionar enumeración SSL, obtención de certificados, cifrados, etc. Uso: sslrecon.py {--nosslyze} ip_address port')
    parser.add_argument('ip_address', help="IP objetivo")
    parser.add_argument('port', help="Puerto contra el cual ejecutar los scripts")
    parser.add_argument('--nosslyze', default=False, help="Pasar --nosslyze True para NO ejecutar sslyze. Se ejecuta por defecto")
    parser.add_argument('--nosslscan', default=False, help="Pasar --nosslscan True para NO ejecutar sslscan. Se ejecuta por defecto")

    args = parser.parse_args()
    ip_address = args.ip_address
    port = args.port

    BASE = "/root/scripts/recon_enum/results/exam/ssl"

    # Asegurar que la ruta esté creada
    mkdir_p(BASE)

    doNmap()
    if not args.nosslyze:
        doSslyze()
    if not args.nosslscan:
        doSslscan()
