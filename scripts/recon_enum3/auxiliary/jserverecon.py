#!/usr/bin/python

import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import argparse
from urllib.parse import urlparse
import pathlib

# Más información: https://github.com/nmap/nmap/tree/master/scripts

# Documentación de Scripts NSE
# En ejecución:
# ajp-auth: obtiene esquema y dominio (realm) de autenticación del servicio AJP --script-args ajp-auth.path=/login
# ajp-headers: petición HEAD o GET contra la raíz y retorna cabeceras de respuesta
# ajp-methods: descubre qué opciones HTTP soporta AJP
# ajp-request: solicita una URI y muestra resultados

# No en ejecución:
# ajp-brute: fuerza bruta contra AJP

def doNmap():
    print("INFO: Iniciando jserverecon con nmap para %s:%s" % (ip_address, port))
    try:
       subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','banner,ajp-auth,ajp-headers,ajp-methods,ajp-request,vulners','--script-args', "http.useragent=%s" % userAgent,'-oA','%s/%s_%s_jserve' % (BASE,ip_address, port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error inesperado en doNmap en jserverecon")
    print("INFO: Finalizado jserverecon con nmap para %s:%s" % (ip_address, port))
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':

   parser = argparse.ArgumentParser(description='Script para gestionar la enumeración de Apache Jserve. Uso: jserverecon.py {} ip puerto')
   parser.add_argument('-a', '--user-agent', dest="userAgent", default="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", help="User-Agent a emplear")
   parser.add_argument('ip', help="Dirección IP objetivo")
   parser.add_argument('port', default="8009", help="Puerto objetivo (por defecto 8009)")

   args = parser.parse_args()

   userAgent = args.userAgent

   parsed_url = urlparse(args.url)

   # Obtener puerto o asignar por defecto
   if not parsed_url.port:
      port = '8009' # puerto por defecto de jserve
   else:
      port = parsed_url.port

   if ":" in parsed_url.scheme:
      ip_address = parsed_url.scheme.split(':')[0]
   else:
      ip_address = parsed_url.scheme

   BASE = "/root/scripts/recon_enum/results/exam/http"
   mkdir_p(BASE)

   doNmap()
