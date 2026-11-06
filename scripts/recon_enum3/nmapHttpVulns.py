#!/usr/bin/env python

import sys
import os
import subprocess
import errno
import time
import multiprocessing
from multiprocessing import Process
import argparse

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# Documentación de Scripts NSE
# En ejecución:
# http-adobe-coldfusion-apsa1301: Omisión de autenticación en Coldfusion
# http-awstatstotals-exec: Ejecución remota de comandos en Awstats Totals 1-1.14
# http-axis2-dir-traversal: Vulnerabilidad de directory traversal en Apache Axis2 versión 1.4.1
# http-barracuda-dir-traversal: Intenta obtener archivos de configuración de Barracuda Networks Spam & Virus Firewall
# http-coldfusion-subzero: Obtiene versión y ruta absoluta del panel de administración en ColdFusion 9 y 10 vulnerables
# http-csrf: Detección de CSRF
# http-dombased-xss: Busca dónde la entrada en el DOM puede ser manipulada para inyectar JavaScript
# http-drupal-enum-users: Enumera usuarios de Drupal mediante divulgación de información
# http-frontpage-login: Comprueba acceso anónimo en Frontpage
# http-iis-webdav-vuln: Vulnerabilidad en IIS 5.1/6.0 con acceso a carpetas WebDAV protegidas
# http-litespeed-sourcecode-download: Explota envenenamiento por byte nulo en Litespeed 4-4.0.15
# http-majordomo2-dir-traversal: Explota directory traversal en Majordomo2
# http-open-redirect: Rastrea e intenta identificar redirecciones abiertas
# http-phpmyadmin-dir-traversal: Explota directory traversal en phpMyAdmin 2.6.4
# http-shellshock: Intenta explotar Shellshock (CVE-2014-6271 y CVE-2014-7169) en aplicaciones web http-shellshock.uri=/
# http-sql-injection: Comprobación básica para provocar errores SQL en formularios
# http-vmware-path-vuln: Comprueba directory traversal en VMWare ESX, ESXi y Server (2009)
# http-vuln-cve2006-3392: Divulgación de archivos en Webmin < 1.290 y Usermin < 1.220 usando %01
# http-vuln-cve2009-3960: Inyección XXE en Adobe. Lee archivos locales en BlazeDS <3.2, LiveCycle y ColdFusion
# http-vuln-cve2010-0738: Omisión de autenticación en consola JMX de JBoss mediante petición HEAD
# http-vuln-cve2010-2861: Directory traversal en ColdFusion para obtener hash de contraseña de admin
# http-vuln-cve2011-3368: Omisión de Proxy Reverso en Apache. Prueba de loopback, hosts internos y sitio externo
# http-vuln-cve2012-1823: Instalaciones PHP-CGI vulnerables para obtener código fuente y ejecutar comandos
# http-vuln-cve2013-0156: Inyección de objetos en Ruby on Rails, ejecución de comandos remotos y DoS
# http-vuln-cve2013-7091: Inclusión local de archivos (LFI) en Zimbra 7.2.6
# http-vuln-cve2014-2126: Escalada de privilegios en Cisco ASA ASDM
# http-vuln-cve2014-2127: Escalada de privilegios en Cisco ASA ASDM
# http-vuln-cve2014-2128: Omisión de autenticación en Cisco ASA SSL VPN
# http-vuln-cve2014-3704: Drupalgeddon < 7.32, inyecta nuevo usuario administrador e intenta inicio de sesión
# http-vuln-cve2014-8877: Inyección remota de código en plugin CM Download Manager <= 2.0.0 de Wordpress
# http-vuln-cve2015-1427: RCE en Elasticsearch 1.3.0-1.3.7 y 1.4.0-1.4.2 mediante motor Groovy
# http-vuln-cve2015-1635: RCE en sistemas Windows mediante HTTP.sys (Win 7, 8, 8.1 y Server 2012, 2012R2)
# http-vuln-cve2017-1001000: Escalada de privilegios en Wordpress 4.7.0 y 4.7.1
# http-vuln-cve2017-5638: RCE en Apache Struts
# http-vuln-cve2017-5689: Escalada de privilegios en Intel AMT
# http-vuln-cve2017-8917: SQLi en Joomla 3.7 - 3.7.1
# http-vuln-misfortune-cookie: RCE Misfortune Cookie en RomPager 4.07
# http-vuln-wnr1000-creds: Obtención de credenciales de admin en Netgear WNR1000

# No en ejecución:
# http-dlink-backdoor: Detección de puerta trasera en routers D-Link mediante User-Agent
# http-domino-enum-passwords: Enumera contraseñas hash de Domino (requiere autenticación previa)
# http-huawei-hg5xx-vuln: Detecta módems Huawei con divulgación de información
# http-iis-short-name-brute: (DoS) Fuerza bruta de nombres cortos 8.3 de archivos y directorios en IIS
# http-phpself-xss: Rastrea PHP y prueba XSS mediante PHP_SELF
# http-slowloris-check: (DoS) Comprueba vulnerabilidad ante Slowloris
# http-slowloris: (DoS) Ejecuta ataque Slowloris
# http-stored-xss: Rastrea formularios y prueba XSS almacenado
# http-tplink-dir-traversal: Directory traversal en routers inalámbricos TP-Link
# http-vuln-cve2011-3192: Denegación de servicio en Apache por manejo de rangos solapados
# http-vuln-cve2013-6786: Redirección y XSS reflejado en Allegro RomPager
# http-vuln-cve2014-2129: Denegación de servicio en Cisco ASA
# tls-ticketbleed: Detección de Ticketbleed en F5 (CVE-2016-9244)

def standardNmapHTTP(ip_address, port):
    print("INFO: Realizando escaneos de script nmapHttpVulns para %s:%s" % (ip_address, port))
    subprocess.run(['nmap','-n','-sV','-Pn','-p',port,'--script=http-adobe-coldfusion-apsa1301,http-awstatstotals-exec,http-axis2-dir-traversal,http-barracuda-dir-traversal,http-coldfusion-subzero,http-csrf,http-dombased-xss,http-drupal-enum-users,http-frontpage-login,http-iis-webdav-vuln,http-litespeed-sourcecode-download,http-majordomo2-dir-traversal,http-open-redirect,http-phpmyadmin-dir-traversal,http-vmware-path-vuln,http-vuln-cve2006-3392,http-vuln-cve2009-3960,http-vuln-cve2010-0738,http-vuln-cve2010-2861,http-vuln-cve2011-3368,http-vuln-cve2012-1823,http-vuln-cve2013-0156,http-vuln-cve2013-7091,http-vuln-cve2014-2126,http-vuln-cve2014-2127,http-vuln-cve2014-2128,http-vuln-cve2014-3704,http-vuln-cve2014-8877,http-vuln-cve2015-1427,http-vuln-cve2015-1635,http-vuln-cve2017-1001000,http-vuln-cve2017-5638,http-vuln-cve2017-5689,http-vuln-cve2017-8917,http-vuln-misfortune-cookie,http-vuln-wnr1000-creds,vulners',ip_address,'-oA',outfile],encoding='utf8')
    return

# En ejecución:
# http-shellshock.nse: Comprueba Shellshock (CVE-2014-6271 y CVE-2014-7169) en endpoints http-shellshock.uri=/
# http-sql-injection.nse: Detección básica de errores SQL en formularios
# Para cada URL con estado 200 si el archivo existe
def shellshockSQL(ip_address, port):
    f = open(outfile2,'w')
    try:
        if os.path.isfile(STAT_200):
            g = open(STAT_200,'r')
    except Exception as e:
        print(type(e))
        print('shellshockSQL en nmapHttpVulns')
    for item in g:
        item = item.split(" ")[0] # la línea contiene URL [status ], dividimos
        if "\n" in item:
            item = item[:-1]
        nmapArg = item.split(port)[1]
        if nmapArg[0] != "/":
            nmapArg = "/" + nmapArg
        if '"' or "'" in nmapArg:
            continue # evitar caracteres que rompan el argumento del script
        results = subprocess.check_output(['nmap','-n','-sV','-Pn','-p',port,'--script=http-shellshock,http-sql-injection','--script-args',"http-sql-injection.url='%s',http-shellsock.uri='%s'" % (nmapArg,nmapArg),ip_address],encoding='utf8')
        f.write("URL " + nmapArg + "\n")
        f.write(results)
    g.close()
    return


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar la enumeración de vulnerabilidades web específicas. Se recomienda usar una lista de URLs válidas. Uso: nmapHttpVulns.py Lista_URLs <http(s)://url_objetivo:puerto>')
    parser.add_argument('URL_List',help='Archivo con URLs válidas (preferiblemente con código de respuesta 200)')
    parser.add_argument('url', help='URL objetivo en formato http(s)://URL:PUERTO')

    args=parser.parse_args()

    # Validar formato URL:PUERTO
    if len(args.url.split(":")) == 0 or len(args.url.split(":")) == 1:
        print("Se requiere especificar URL:PUERTO")
        sys.exit(1)
    elif ("https" in args.url):
        tmp = args.url.split("https://")
        if len(tmp) == 2:
            if len(tmp[1].split(":")) == 2:
                ip_address = tmp[1].split(":")[0]
                port = tmp[1].split(":")[1]
            else:
                print("Se requiere especificar URL:PUERTO")
                sys.exit(1)
    elif ("http" in args.url):
        tmp = args.url.split("http://")
        if len(tmp) == 2:
            if len(tmp[1].split(":")) == 2:
                ip_address = tmp[1].split(":")[0]
                port = tmp[1].split(":")[1]
            else:
                print("Se requiere especificar URL:PUERTO")
                sys.exit(1)
    else:
        tmp = args.url.split(":")
        if len(tmp) == 2:
            ip_address = tmp[0]
            port = tmp[1]

    BASE = "/root/scripts/recon_enum/results/exam/http"
    DIRB_BASE = "/root/scripts/recon_enum/results/exam/dirb/%s" % (port)
    STAT_200 = args.URL_List
    outfile = "%s/%s_%s_nmap_HttpVulns.txt" % (BASE, ip_address, port)
    outfile2 = "%s/%s_%s_nmap_HttpVulns_SS_SQL.txt" % (BASE, ip_address, port)

    standardNmapHTTP(ip_address, port)
    shellshockSQL(ip_address, port)
