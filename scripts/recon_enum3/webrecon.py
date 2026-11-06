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
from urllib.parse import urlparse

# Más información: https://github.com/nmap/nmap/tree/master/scripts

# Documentación de Scripts NSE
# En ejecución:
# http-apache-negotiation: comprueba mod_negotiation en Apache (comportamiento al solicitar index sin extensión)
# http-apache-server-status: intenta obtener /server-status si mod_status está habilitado
# http-aspnet-debug: determina si ASP.NET tiene depuración activada mediante HTTP DEBUG
# http-auth-finder: rastrea el sitio buscando páginas que requieran autenticación por formularios o HTTP básica
# http-auth: obtiene el esquema y dominio (realm) de autenticación de servicios web protegidos
# http-backup-finder: busca copias de seguridad de archivos descubiertos (.bak, ~, 'copy of...', etc.)
# http-bigip-cookie: decodifica cookies no cifradas de F5 BIG-IP en respuestas HTTP
# http-cakephp-version: detecta versión de CakePHP mediante archivos conocidos
# http-cisco-anyconnect: conecta como cliente AnyConnect a Cisco SSL VPN y obtiene versión e información de túnel
# http-comments-displayer: extrae y muestra comentarios HTML y JavaScript de las respuestas
# http-config-backup: busca copias de seguridad y archivos swap de CMS y configuraciones web comunes
# http-cookie-flags: examina atributos y rutas de cookies (Secure, HttpOnly, etc.)
# http-cors: comprueba cabeceras CORS enviando Access-Control-Request-Method
# http-cross-domain-policy: comprueba archivos /crossdomain.xml y /clientaccesspolicy.xml
# http-default-accounts: prueba credenciales predeterminadas comunes en aplicaciones y dispositivos web
# http-drupal-enum: enumera módulos y temas instalados en Drupal mediante lista de conocidos
# http-favicon: obtiene el favicon, calcula su hash y compara con aplicaciones conocidas
# http-gen: muestra el contenido de la etiqueta meta generator
# http-git: comprueba presencia de directorio .git e intenta extraer información del repositorio
# http-grep: rastrea y busca coincidencias con patrones de texto (por defecto busca correos e IPs)
# http-headers: realiza petición HEAD y muestra las cabeceras HTTP
# http-jsonp-detection: intenta descubrir endpoints JSONP (útil para evadir Same Origin Policy)
# http-ls: muestra el contenido de páginas con listado de directorios ("index of")
# http-mcmp: comprueba si el servidor permite métodos de gestión mod_cluster (MCMP)
# http-method-tamper: prueba manipulación de verbos HTTP para acceder a recursos protegidos
# http-methods: identifica métodos HTTP soportados mediante peticiones OPTIONS
# http-mobileversion-checker: comprueba si un User-Agent móvil es redirigido a una versión web móvil
# http-ntlm-info: envía petición de autenticación NTLM con dominio nulo para obtener NetBIOS, DNS y versión de SO
# http-passwd: comprueba vulnerabilidad de directory traversal
# http-php-version: intenta determinar la versión de PHP mediante consultas especiales
# http-robots.txt: examina rutas no permitidas en robots.txt
# http-title: muestra el título de la página principal del servidor web
# http-traceroute: detecta la presencia de proxies reversos
# http-unsafe-output-escaping: prueba parámetros para verificar si se reflejan sin escapar
# http-useragent-tester: prueba diferentes User-Agents para verificar si están bloqueados o permitidos
# http-userdir-enum: intenta enumerar usuarios válidos en servidores con mod_userdir activo (~usuario)
# http-vhosts: busca hosts virtuales enviando peticiones HEAD con diferentes cabeceras Host
# http-vlcstreamer-ls: se conecta a VLC Streamer y lista contenido de directorios
# http-waf-detect: intenta detectar presencia de IPS/IDS/WAF
# http-waf-fingerprint: intenta identificar la huella específica del WAF
# http-webdav-scan: detecta instalaciones WebDAV mediante métodos OPTIONS y PROPFIND

# No en ejecución:
# http-affiliate-id: extrae IDs de redes de afiliados (AdSense, Analytics, Amazon, etc.)
# http-avaya-ipoffice-users: enumera usuarios en sistemas Avaya IP Office
# http-brute: fuerza bruta contra autenticación básica, digest y NTLM
# http-chrono: mide tiempos de respuesta del sitio web
# http-date: obtiene fecha del servicio y compara desfases
# http-devframework: intenta identificar frameworks de desarrollo
# http-enum: enumera directorios comunes de aplicaciones web
# http-errors: rastrea y reporta páginas de error
# http-exif-spider: rastrea imágenes en busca de metadatos EXIF
# http-feed: rastrea canales RSS o Atom
# http-fetch: descarga archivos del servidor
# http-fileupload-exploiter: prueba métodos para explotar formularios de subida
# http-form-brute: fuerza bruta contra autenticación basada en formularios
# http-form-fuzzer: fuzzer para campos de formularios
# http-gitweb-projects-enum: enumera proyectos y propietarios desde gitweb
# http-google-malware: comprueba si el host figura en listas negras de Google
# http-icloud-findmyiphone: obtiene ubicación de dispositivos iOS (requiere autenticación)
# http-icloud-sendmsg: envía mensaje a iOS mediante MobileMe
# http-internal-ip-disclosure: petición HTTP/1.0 sin cabecera Host para verificar si revela la IP interna
# http-joomla-brute: fuerza bruta contra Joomla
# http-malware-host: busca firmas de servidores comprometidos
# http-open-proxy: intenta conexión a través del proxy
# http-proxy-brute: fuerza bruta contra servidores proxy
# http-put: subida de archivos mediante método HTTP PUT
# http-qnap-nas-info: obtiene modelo, firmware y servicios de NAS QNAP
# http-referer-checker: analiza inclusión cruzada de scripts
# http-rfi-spider: rastrea vulnerabilidades de inclusión remota de archivos (RFI)
# http-robtex-reverse-ip: obtiene resoluciones inversas desde Robtex
# http-robtex-shared-ns: obtiene nombres de dominio que comparten NS desde Robtex
# http-security-headers: comprueba cabeceras de seguridad HTTP
# http-server-header: examina cabecera Server
# http-sitemap-generator: genera estructura del sitio web
# http-svn-enum: enumera usuarios de repositorios Subversion
# http-svn-info: solicita información del repositorio SVN
# http-trace: comprueba si TRACE está habilitado
# http-trane-info: obtiene información de controladores HVAC
# http-virustotal: consulta reputación en VirusTotal
# http-wordpress-brute: fuerza bruta contra WordPress
# http-wordpress-enum: enumeración de temas y plugins de WordPress
# http-wordpress-users: enumeración de usuarios de WordPress
# http-xssed: busca en la base de datos de xssed.com
# https-redirect: comprueba redirección automática de HTTP a HTTPS
def doNmap():
    print("INFO: Iniciando webrecon con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','banner,http-apache-negotiation,http-apache-server-status,http-aspnet-debug,http-auth-finder,http-auth,http-backup-finder,http-bigip-cookie,http-cakephp-version,http-cisco-anyconnect,http-comments-displayer,http-config-backup,http-cookie-flags,http-cors,http-cross-domain-policy,http-default-accounts,http-drupal-enum,http-favicon,http-generator,http-git,http-grep,http-headers,http-jsonp-detection,http-ls,http-mcmp,http-method-tamper,http-methods,http-mobileversion-checker,http-ntlm-info,http-passwd,http-php-version,http-robots.txt,http-title,http-traceroute,http-unsafe-output-escaping,http-useragent-tester,http-userdir-enum,http-vhosts,http-vlcstreamer-ls,http-waf-detect,http-waf-fingerprint,http-webdav-scan','--script-args', "http.useragent=%s,http-waf-detect.aggro,http-waf-detect.detectBodyChanges,http-waf-fingerprint.intensive=1" % userAgent,'-oA','%s/%s_%s_http' % (BASE,ip_address, port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error inesperado en doNmap en webrecon")
    print("INFO: Finalizado webrecon con nmap para %s:%s" % (ip_address, port))
    return

def doSSLRecon():
    print("INFO: Iniciando sslrecon con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['./sslrecon.py', ip_address, port],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error inesperado en doSslRecon en webrecon")
    print("INFO: Finalizado sslrecon con nmap para %s:%s" % (ip_address, port))
    return

def doNikto():
    print("INFO: Iniciando nikto webRecon para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nikto','-host',ip_address,'-port',port,'-nolookup','-ask','auto','-output'," %s/%s_%s_nikto.xml" % (NIKTO_BASE,ip_address,port)],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error inesperado en doNikto en webrecon")
    print("INFO: Finalizado nikto webRecon para %s:%s" % (ip_address, port))
    return

# Opciones de VHostScan:
# -t TARGET_HOSTS   host objetivo
# -b BASE_HOST      host base para sustitución en la lista de palabras
# -w WORDLISTS      lista de palabras a utilizar
# -p PORT           puerto a utilizar (por defecto 80)
# -r REAL_PORT      puerto real del servidor web en cabeceras si difiere de 80
# --ignore-http-codes lista de códigos HTTP a ignorar (por defecto 404)
# --prefix / --suffix prefijo o sufijo para cada elemento de la lista
# --user-agent      User-Agent personalizado
# --ssl             conexión mediante HTTPS
def doVHostScan():
    # https://github.com/codingo/VHostScan
    print("INFO: Iniciando VHostScan webRecon para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['VHostScan','-v','-t',ip_address,'-p',port,'-w','/root/lists/Web/virtual_host_scanning.txt','--no-lookups','--user-agent',userAgent,'-oN',VHOST_OUT],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error inesperado en doVHostScan en webrecon")
    print("INFO: Finalizado VHostScan webRecon para %s:%s" % (ip_address, port))
    return

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar enumeración web, fingerprinting y escaneos base. Uso: webrecon.py {} <http(s)://url_objetivo:puerto>')
    parser.add_argument('-n', '--nmap', default='true', help="Ejecutar scripts seguros de nmap orientados a HTTP")
    parser.add_argument('-k', '--nikto', default='true', help="Ejecutar nikto contra el sitio")
    parser.add_argument('-v', '--vhost', default='true', help="Ejecutar VHostScan contra el sitio")
    parser.add_argument('-a', '--user-agent', dest='userAgent', default="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", help="User-Agent a emplear")
    parser.add_argument('url', help="URL objetivo con formato http(s)://IP:PUERTO")

    args = parser.parse_args()

    parsed_url = urlparse(args.url)
    userAgent = args.userAgent

    # Obtener puerto o asignar por defecto
    if not parsed_url.port:
        if parsed_url.scheme == 'http':
            port = '80'
            print("INFO: [webrecon] no se especificó puerto exacto, http asigna puerto 80 por defecto")
        elif parsed_url.scheme == 'https':
            port = '443'
            print("INFO: [webrecon] no se especificó puerto exacto, https asigna puerto 443 por defecto")
        else:
            print("ERROR: [webrecon] esquema desconocido")
            sys.exit(1)
    else:
        port = parsed_url.port

    if ":" in parsed_url.scheme:
        ip_address = parsed_url.scheme.split(':')[0]
    else:
        ip_address = parsed_url.scheme

    BASE = "/root/scripts/recon_enum/results/exam/http/%s/%s" % (ip_address,port)
    NIKTO_BASE = "/root/scripts/recon_enum/results/exam/nikto/%s/%s" % (ip_address,port)
    VHOST_OUT = "%s/%s_%s_vhost" % (BASE, ip_address, port)

    # Asegurar que las rutas existan
    mkdir_p(BASE)
    mkdir_p(NIKTO_BASE)

    if args.nmap:
        doNmap()
        doSSLRecon()
    if args.nikto:
        doNikto()
    if args.vhost:
        doVHostScan()
