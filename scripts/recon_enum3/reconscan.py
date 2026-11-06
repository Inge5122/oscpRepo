#!/usr/bin/env python

###############################################################################################################
## [Título]: reconscan.py -- script de reconocimiento y enumeración
## [Autor]: Mike Czumak (T_v3rn1x) -- @SecuritySift
## [Actualizaciones]: Reward1
##-------------------------------------------------------------------------------------------------------------
## [Detalles]:
## Este script está diseñado para ejecutarse remotamente contra una lista de IPs para enumerar servicios
## descubiertos tales como smb, smtp, snmp, ftp y otros.
##
## El script requiere un archivo targets.txt que contenga los objetivos (uno por línea) ubicado en:
## /root/scripts/recon_enum/results/exam/targets.txt
##
## El script ejecutará nmap (tasa mínima muy rápida) contra todos los puertos, pasará los puertos abiertos
## a Nmap para su versión y luego ejecutará un escaneo completo de nmap contra todos los puertos.
##-------------------------------------------------------------------------------------------------------------
## [Ejecución]:
## Ejecuta setup.sh en la carpeta scripts
## /root/scripts/recon_enum/./reconscan.py
## o
## python /root/scripts/recon_enum/reconscan.py
##-------------------------------------------------------------------------------------------------------------
## [Advertencia]:
## Este script se entrega "tal cual" sin garantía de funcionalidad o exactitud. Fue escrito estrictamente
## para uso personal. No hay planes de mantener actualizaciones; no fue escrito para ser óptimo y en algunos
## casos las funciones pueden no producir los resultados esperados, por lo que su uso queda bajo tu propia
## responsabilidad y discreción. Este script fue diseñado para máquinas en entornos de laboratorio, ¡por favor
## utilízalo únicamente contra sistemas sobre los cuales tengas autorización explícita!
##-------------------------------------------------------------------------------------------------------------
## [Modificación, Distribución y Atribución]:
## Eres libre de modificar y/o distribuir este script como desees. Solo se solicita mantener la atribución al
## autor original y no intentar venderlo ni incorporarlo a ninguna oferta comercial.
##-------------------------------------------------------------------------------------------------------------
## [POR HACER / TODO]
## Ampliar: Script "Alive". Identificar hosts activos mediante técnicas avanzadas.
##      Enumeración Pre-Explotación > Activa > Mapeo de Infraestructura Interna > Identificar IPs Activas
## Ampliar: RDPenum con rdp-sec-check
## Ejecutar cada script individualmente no asegura que existan sus rutas de salida... mejora de usabilidad pendiente...
## Corregir DNSRecon
## Ampliar: DirbustEverything
##       : ¡más herramientas! DirBuster, Dirsearch... WFUZZ aún necesita extensiones
##       : Filtros PHP
##       : Eyewitness: capturas de pantalla de páginas web
##       : Photon, rastreador web eficiente. Asegura no pasar nada por alto (actualmente usa Cewl para rastreo y wordlists)
##       : capturar páginas (Status: 301) (generalizar función STAT200) y ejecutar gobust solo en ellas
## Ampliar: nmapHTTPVuln
##       : snallygaster https://github.com/hannob/snallygaster
## Ampliar FTP/TFTP: Utilizar escaneo DotDotPwn anónimo y autenticado
## Ampliar SMTPrecon
##       : actualmente solo escanea el 25. Pendiente: 25,110,143,465,587,993,995 (IMAP/POP/Exchange)
##       : Cambiar a ip_address, port. Pasar solo puertos específicos, actualmente fijos en 25,465,587
##       : Ruler para Exchange (posiblemente)
## Ampliar SMBRecon
##       : hydra o crackmapexec para spray/fuerza bruta #requiere especificar Dominio y cuidar bloqueos de cuenta
## Ampliar dirTrav:
##     Depurar todos los casos (vulnerabilidades page?= y Windows)
## Opción para ejecutar reconscan con un rango de IP para pasar a aliverecon
## Ampliar ReconScan:
##      Otras herramientas a considerar: WHOIS, DNSRecon, Sublist3r
##      Otras herramientas a considerar: WafW00f, WAFNinja, XSS Scanner, Arachni, Spaghetti, TheHarvester, Metagoofil,
##      Otras herramientas a considerar: A2SV
##      Separar CMSscannerrecon: WPscan, WPscanner, WPSeku, Droopescan,
##      Crear "AutoADPwn": Invocar múltiples módulos, reconocimiento AD, bloodhound, Empire/Deathstar
## Se requieren scripts para:
##       rsh, vnc
## Asegurar que todos los scripts tengan mensajes de inicio ("starting") y finalización ("Finished") y retirarlos de reconscan
##
## [REFLEXIONES]
## Organizar todo por dirección IP probablemente sería mucho mejor, pero requiere bastante trabajo reestructurarlo...
## Dividir scripts de nmap para http
##
## [NOTAS]
## vulners.nse requiere la bandera -sV
###############################################################################################################

import subprocess
import multiprocessing
from multiprocessing import Process, Queue
import os
import time
import errno
import shutil
from colorama import init, Fore, Style
import argparse
import pathlib
init()
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

def multProc(targetin, scanip, port):
    jobs = []
    p = multiprocessing.Process(target=targetin, args=(scanip,port))
    jobs.append(p)
    p.start()
    return

def jserveEnum(ip_address, port):
    print(Fore.GREEN + "INFO: Enumerando Apache Jserve en %s:%s" % (ip_address, port) + Style.RESET_ALL)
    print("INFO: Enumerando Apache Jserve en %s:%s" % (ip_address, port))
    subprocess.check_output(['auxiliary/./jserverecon.py',ip_address,port],encoding='utf8')
    return

def dnsEnum(ip_address, port):
    print("INFO: Enumerando DNS en %s:%s" % (ip_address, port))
    if port.strip() == "53":
       subprocess.check_output(['./dnsrecon.py',ip_address],encoding='utf8')
    return

def ftpEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    # POR HACER (TODO): permitir que ftprecon y reconscan pasen listas de usuario/contraseña a los submódulos
    print("INFO: Enumerando FTP en %s:%s" % (ip_address, port))
    # FTPRECON en subdirectorio por si ssh/telnet/mysql están presentes,
    # hydra tendrá archivos hydra.restore independientes
    subprocess.check_output(['ftp/./ftprecon.py',ip_address,port],encoding='utf8')
    return

def fingerEnum(ip_address, port):
    print("INFO: Enumerando Finger en %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','finger,vulners','-oA','/root/scripts/recon_enum/results/exam/finger/%s_%s_finger' % (ip_address,port),ip_address],encoding='utf8')
    return

def httpEnum(ip_address, port):
    # webRecon obtiene información típica de Nmap y nikto
    # dirbust solo -i 2 utiliza lista de palabras corta y extensiones reducidas
    # dirbust full -i 8 utiliza lista de palabras amplia, más extensiones y pasa a herramientas adicionales (cewl, parameth, whatweb, etc.)
    print("INFO: Realizando escaneo de script webRecon para %s:%s (paso 1/3)" % (ip_address, port))
    subprocess.check_output(['./webrecon.py','-a',userAgent,'http://%s:%s' % (ip_address, port)],encoding='utf8')
    print("INFO: Escaneo webRecon completado para %s:%s (paso 1/3)" % (ip_address, port))
    print("INFO: Escaneo dirbust con intensidad 2 iniciado en %s:%s (paso 2/3)" % (ip_address, port))
    subprocess.check_output(['./dirbustEVERYTHING.py','-a',userAgent,'-p','1','-i','2','http://%s:%s' % (ip_address,port)],encoding='utf8')
    print("INFO: Escaneo dirbust con intensidad 2 completado para %s:%s (paso 2/3)" % (ip_address, port))
    print("INFO: Escaneo dirbust con intensidad 8 iniciado en %s:%s (paso 3/3)" % (ip_address, port))
    subprocess.check_output(['./dirbustEVERYTHING.py','-a',userAgent,'-p','1','-i','8','http://%s:%s' % (ip_address,port)],encoding='utf8')
    print("INFO: Escaneo dirbust con intensidad 8 completado para %s:%s (paso 3/3)" % (ip_address, port))
    return

def httpsEnum(ip_address, port):
    # webRecon obtiene información típica de Nmap y nikto
    # dirbust solo -i 2 utiliza lista corta de palabras y extensiones reducidas
    # dirbust full -i 8 utiliza lista amplia, más extensiones y pasa a herramientas adicionales (cewl, parameth, whatweb, etc.)
    path = "/root/scripts/recon_enum/results/exam/dirb/%s" % (port)
    mkdir_p(path)
    print("INFO: Realizando escaneo de script webRecon para %s:%s (paso 1/3)" % (ip_address, port))
    subprocess.check_output(['./webRecon.py','-a',userAgent,'https://%s:%s' % (ip_address, port)],encoding='utf8')
    print("INFO: Escaneo webRecon completado para %s:%s (paso 1/3)" % (ip_address, port))
    print("INFO: Escaneo dirbust con intensidad 2 iniciado en %s:%s (paso 2/3)" % (ip_address, port))
    subprocess.check_output(['./dirbustEVERYTHING.py','-a',userAgent,'-p','1','-i','2','https://%s:%s' % (ip_address,port)],encoding='utf8')
    print("INFO: Escaneo dirbust con intensidad 2 completado para %s:%s (paso 2/3)" % (ip_address, port))
    print("INFO: Escaneo dirbust con intensidad 8 iniciado en %s:%s (paso 3/3)" % (ip_address, port))
    subprocess.check_output(['./dirbustEVERYTHING.py','-a',userAgent,'-p','1','-i','8','https://%s:%s' % (ip_address,port)],encoding='utf8')
    print("INFO: Escaneo dirbust con intensidad 8 completado para %s:%s (paso 3/3)" % (ip_address, port))
    return

def mssqlEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    # POR HACER (TODO): permitir que mssql y reconscan pasen listas de usuario/contraseña a los submódulos
    # MSSQLRECON en subdirectorio por si hay múltiples archivos hydra.restore. Por defecto, nmap realiza fuerza bruta.
    print("INFO: Enumerando MS-SQL en %s:%s" % (ip_address, port))
    subprocess.check_output(['mssql/./mssqlrecon.py',ip_address,port],encoding='utf8')
    return

def ldapEnum(ip_address, port):
    print("INFO: Enumerando LDAP en %s:%s" % (ip_address, port))
    subprocess.check_output(['./ldaprecon.py',ip_address,'--port',port],encoding='utf8')
    return

def mysqlEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    # POR HACER (TODO): permitir que mysql y reconscan pasen listas de usuario/contraseña a los submódulos
    # MYSQLRECON en subdirectorio por si ftp/ssh/telnet están presentes
    print("INFO: Enumerando MySQL en %s:%s" % (ip_address, port))
    subprocess.check_output(['mysql/./mysqlrecon.py',ip_address,port],encoding='utf8')
    return

def nfsEnum(ip_address, port):
    print("INFO: Enumerando NFS en %s:%s" % (ip_address, port))
    subprocess.check_output(['./nfsrecon.py',ip_address,port],encoding='utf8')
    return

def msrpcEnum(ip_address, port):
    print("INFO: Enumerando MSRPC en %s:%s" % (ip_address, port))
    # Paquetes RPC de Impacket
    subprocess.check_output(['./msrpcrecon.py',ip_address,port],encoding='utf8')
    return

#puerto 111 #apt-get install, nfs-common
#En ejecución:
#rpc-grind: Identifica la huella (fingerprint) del puerto RPC objetivo para extraer servicio, número rpc y versión
#rpcinfo: Se conecta al mapeador de puertos (portmapper) y obtiene la lista de todos los programas registrados

#No en ejecución:
#rpcap-brute: Fuerza bruta contra WinPcap Remote Capture
#rpcap-info: Recupera información de interfaces mediante el servicio rpcap
def rpcbindEnum(ip_address, port):
    print("INFO: Enumerando RPCBind en %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','rpc-grind,rpcinfo','-oA',"/root/scripts/recon_enum/results/exam/rpc/%s_%s_rpc" % (ip_address,port),ip_address],encoding='utf8')
    RPCINFOSCAN1 = "rpcinfo %s > /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt && echo -e '\n' >> /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt" % (ip_address, ip_address, ip_address)
    subprocess.check_output(RPCINFOSCAN1, shell=True)
    RPCINFOSCAN2 = "rpcinfo -p %s > /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt && echo -e '\n' >> /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt" % (ip_address, ip_address, ip_address)
    subprocess.check_output(RPCINFOSCAN2, shell=True)
    RPCINFOSCAN3 = "rpcinfo -m %s > /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt && echo -e '\n' >> /root/scripts/recon_enum/results/exam/rpc/%s_rpcinfo.txt" % (ip_address, ip_address, ip_address)
    subprocess.check_output(RPCINFOSCAN3, shell=True)
    return

def rdpEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    # POR HACER (TODO): permitir que mssql y reconscan pasen listas de usuario/contraseña a los submódulos
    # RDPRECON en subdirectorio por si hay múltiples archivos hydra.restore
    print("INFO: Enumerando RDP en %s:%s" % (ip_address, port))
    subprocess.check_output(['rdp/./rdprecon.py',ip_address,port],encoding='utf8')
    return

# POR HACER (TODO): Este debería ser un módulo independiente.
# POR HACER (TODO): Hacer que hydra sea una opción para reconscan y pasarla a los submódulos
# POR HACER (TODO): permitir que rLogin y reconscan pasen listas de usuario/contraseña a los submódulos
def rloginEnum(ip_address, port):
    # Típicamente solo puerto 513, así que comprobamos
    if port.strip() == "513":
        print("INFO: Enumerando RLogin en %s:%s" % (ip_address, port))
        hydra_outfile = '/root/scripts/recon_enum/results/exam/%s_rloginhydra' % (ip_address)
        try:
            subprocess.check_output(['hydra','-L','/root/lists/userlist.txt','-P','/root/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-u',ip_address,'rlogin'],encoding='utf8').split("\n")
            with open(hydra_outfile, 'r') as h:
                for res in h:
                   if "login:" in res:
                      print("[*] Credenciales válidas de rlogin encontradas: " + res)
        except subprocess.CalledProcessError as hydrerr:
            if hydrerr.returncode == 255:
                print("Hydra finalizó antes con estado 255, ¡debe haber encontrado algo! Revisa rloginhydra para ver la salida.")
                print("Nota: puede que necesites instalar rsh-client.")
            elif hydrerr.returncode != 0:
                print("Hydra falló:")
                print(hydrerr.returncode)
                print(hydrerr.output)
            else:
                print("INFO: No se encontraron credenciales válidas de rlogin")
    else:
        print("Otros servicios rlogin (exec/shell) detectados. Enumerar manualmente: %s:%s" % (ip_address, port))
    return

# POR HACER (TODO): permitir que sshEnum y reconscan pasen listas de usuario/contraseña a los submódulos
def sshEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    print("INFO: Enumerando SSH en %s:%s" % (ip_address, port))
    subprocess.check_output(['./sshrecon.py',ip_address,port],encoding='utf8')
    return

def snmpEnum(ip_address, port):
    print("INFO: Enumerando SNMP en %s:%s" % (ip_address, port))
    subprocess.check_output(['./snmprecon.py',ip_address],encoding='utf8')
    return

# POR HACER (TODO): asegurar pasar el puerto a SMTP recon y omitir el error
def smtpEnum(ip_address, port):
    print("INFO: Enumerando SMTP en %s:%s" % (ip_address, port))
    if port.strip() == "25":
       subprocess.check_output(['./smtprecon.py',ip_address],encoding='utf8')
    else:
       print("ADVERTENCIA: SMTP detectado en puerto no estándar, smtprecon omitido (debe ejecutarse manualmente)")
    return

def smbEnum(ip_address, port):
    print("INFO: Enumerando SMB en %s:%s" % (ip_address, port))
    if port.strip() == "139":
       subprocess.check_output(['./smbrecon.py',ip_address,port],encoding='utf8')
    if port.strip() == "445":
       subprocess.check_output(['./smbrecon.py',ip_address,port],encoding='utf8')
    if port.strip() == "137":
       subprocess.check_output(['./smbrecon.py',ip_address,port],encoding='utf8')
    return

# POR HACER (TODO): permitir que telnet y reconscan pasen listas de usuario/contraseña a los submódulos
def telnetEnum(ip_address, port):
    # EDITAR CON LISTAS DE USUARIO/CONTRASEÑA
    # TELNETRECON en subdirectorio por si ftp/ssh/mysql están presentes, hydra tendrá archivos hydra.restore independientes
    print("INFO: Enumerando Telnet en %s:%s" % (ip_address, port))
    subprocess.check_output(['telnet/./telnetrecon.py',ip_address,port],encoding='utf8')
    return

def tftpEnum(ip_address, port):
   print("INFO: Enumerando TFTP en %s:%s" % (ip_address, port))
   subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','tftp-enum,vulners','-oA',"/root/scripts/recon_enum/results/exam/tftp/%s_%s_tftp" % (ip_address,port),ip_address],encoding='utf8')
   return

def nmapFullSlowScan(ip_address):
   ip_address = ip_address.strip()
   print("INFO: Ejecutando escaneos Nmap completos lentos TCP/UDP para %s" % (ip_address))
   tcplines = subprocess.check_output(['nmap','-n','-vv','--stats-every','30s','-Pn','-sT','-T','3','-p-','--max-retries','1','--min-rate',SLOW_NMAP_MIN_RATE,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%s_FULL" % ip_address,ip_address],encoding='utf8').split("\n")
   for line in tcplines:
      line = line.strip()
      if ("tcp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar el nombre del servicio
         port = line.split(" ")[0] # capturar el puerto/protocolo
         port = port.split("/")[0]
         print(("INFO: Nmap Completo Lento para %s encontró TCP: %s en %s") % (ip_address, service, port))
   udplines = subprocess.check_output(['nmap','-n','-vv','--stats-every','30s','-Pn','-sU','-T','3','-p-','--max-retries','1','--min-rate',SLOW_NMAP_MIN_RATE,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%sU_FULL" % ip_address,ip_address],encoding='utf8').split("\n")
   for line in udplines:
      line = line.strip()
      if ("udp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar el nombre del servicio
         port = line.split(" ")[0] # capturar el puerto/protocolo
         port = port.split("/")[0]
         print(("INFO: Nmap Completo Lento para %s encontró UDP: %s en %s") % (ip_address, service, port))
   print("INFO: Escaneos Nmap completos lentos TCP/UDP completados para %s" % (ip_address))
   return

# Asegúrate de cambiar la interfaz si es necesario
#-mT/-mU TCP/UDP respectivamente, rango completo de puertos. -L timeout 3 segundos (7 por defecto), 300 paquetes por segundo (por defecto)
# -n                    No realizar resolución DNS
# -vv                   Modo muy detallado (very verbose)
# --stats-every 30s     Mostrar estadísticas cada 30 segundos
# -Pn                   Tratar hosts como en línea (omitir descubrimiento de hosts)
# -sT                   Conexión TCP completa (evita ráfagas SYN excesivas)
# -T4                   Plantilla de temporización 4, escaneo más rápido
# -p-                   Escanear todos los puertos (1-65535)
# --max-retries 1       Reintentar un puerto solo una vez
# --min-rate            Enviar paquetes a la tasa mínima especificada
# -oA                   Generar salida en los tres formatos (nmap, gnmap, xml)
#
def nmapFullFastScan(ip_address):
   ip_address = ip_address.strip()
   print("INFO: Ejecutando escaneos Nmap completos rápidos TCP/UDP para " + ip_address)
   tcplines = subprocess.check_output(['nmap','-n','-vv','--stats-every','30s','-Pn','-sT','-T','4','-p-','--max-retries','1','--min-rate',FAST_NMAP_MIN_RATE,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%s_INITIAL" % ip_address,ip_address],encoding='utf8').split("\n")
   tcpPorts = []
   udpPorts = []
   for line in tcplines:
      line = line.strip()
      if ("tcp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar el nombre del servicio
         port = line.split(" ")[0] # capturar el puerto/protocolo
         port = port.split("/")[0]
         tcpPorts.append(port)
         print(("INFO: Nmap Rápido para %s encontró TCP: %s en %s") % (ip_address, service, port))
   for port in tcpPorts: # el último elemento en la lista está vacío
      if port != "":
         multProc(nmapVersionTCPAndPass, ip_address, port)
   udplines = subprocess.check_output(['nmap','-n','-vv','--stats-every','30s','-Pn','-sU','-T','4','-p-','--max-retries','1','--min-rate',FAST_NMAP_MIN_RATE,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%sU_INITIAL" % ip_address,ip_address],encoding='utf8').split("\n")
   for line in udplines:
      line = line.strip()
      if ("udp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar el nombre del servicio
         port = line.split(" ")[0] # capturar el puerto/protocolo
         port = port.split("/")[0]
         udpPorts.append(port)
         print(("INFO: Nmap Rápido para %s encontró UDP: %s en %s") % (ip_address, service, port))
   for port in udpPorts: # el último elemento en la lista está vacío
      if port != "":
         multProc(nmapVersionUDPAndPass, ip_address, port)
   print("INFO: Nmap rápido TCP/UDP finalizado para %s. Tareas delegadas a los scripts correspondientes" % (ip_address))
   jobs = []
   q = multiprocessing.Process(target=nmapFullSlowScan, args=(scanip,)) # coma requerida
   jobs.append(q)
   q.start()
   return

def nmapVersionTCPAndPass(ip_address, port):
   # Necesario para versionar puertos y en caso de no haber módulo de reconocimiento específico, contar con un escaneo base. Ejecuta scripts por defecto.
   lines = subprocess.check_output(['nmap','-n','-vv','-Pn','-A','-sC','-sV','-sT','-T','4','-p',port,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%s_%s" % (ip_address,port),ip_address],encoding='utf8').split("\n")
   print("INFO: Detección de versión Nmap y derivación completada para TCP %s:%s" % (ip_address, port))
   for line in lines:
      line = line.strip()
      if ("tcp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar nombre del servicio
         port = line.split(" ")[0] # capturar puerto/protocolo
         port = port.split("/")[0]
         if ("http" in service):
            multProc(httpEnum, ip_address, port)
         elif ("ajp13" in service):
            multProc(jserveEnum, ip_address, port)
         elif ("domain" in service): # asegurar detección si DNS está en TCP
            multProc(dnsEnum, ip_address, port)
         elif ("login" in service or "exec" in service or "shell" in service):
            multProc(rloginEnum, ip_address, port)
         elif ("finger" in service):
            multProc(fingerEnum, ip_address, port)
         elif ("ftp" in service):
            multProc(ftpEnum, ip_address, port)
         elif ("ldap" in service):
            multProc(ldapEnum, ip_address, port)
         elif ("netbios-ssn" in service):
            multProc(smbEnum, ip_address,port)
         elif ("microsoft-ds" in service):
            multProc(smbEnum, ip_address, port)
         elif ("msrpc" in service):
            multProc(msrpcEnum, ip_address, port)
         elif ("ms-sql" in service or "mssql" in service):
            multProc(mssqlEnum, ip_address, port)
         elif ("my-sql" in service or "mysql" in service):
            multProc(mysqlEnum, ip_address, port)
         elif ("nfs" in service):
            multProc(nfsEnum, ip_address, port)
         elif ("rdp" in service or "ms-wbt-server" in service):
            multProc(rdpEnum, ip_address, port)
         elif ("rpcbind" == service):
            multProc(rpcbindEnum, ip_address, port)
         elif ("ssh/http" in service or "https" in service):
            multProc(httpsEnum, ip_address, port)
         elif ("ssh" in service):
            multProc(sshEnum, ip_address, port)
         elif ("smtp" in service):
            multProc(smtpEnum, ip_address, port)
         elif ("telnet" in service):
            multProc(telnetEnum, ip_address, port)
         elif ("tftp" in service):
            multProc(tftpEnum, ip_address, port)

def nmapVersionUDPAndPass(ip_address, port):
   lines = subprocess.check_output(['nmap','-n','-vv','-Pn','-A','-sC','-sV','-sU','-T','4','-p',port,'-oA',"/root/scripts/recon_enum/results/exam/nmap/%s_%sU" % (ip_address,port),ip_address],encoding='utf8').split("\n")
   print("INFO: Detección de versión Nmap y derivación completada para UDP %s:%s" % (ip_address, port))
   for line in lines:
      line = line.strip()
      if ("udp" in line) and ("open" in line) and not ("Discovered" in line):
         while "  " in line:
            line = line.replace("  ", " ")
         linesplit= line.split(" ")
         service = linesplit[2] # capturar nombre del servicio
         port = line.split(" ")[0] # capturar puerto/protocolo
         port = port.split("/")[0]
         if ("domain" in service):
            multProc(dnsEnum, ip_address, port)
         elif ("snmp" in service):
            multProc(snmpEnum, ip_address, port)
         elif ("tftp" in service):
            multProc(tftpEnum, ip_address, port)

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# Crear los directorios definidos para la estructura de resultados
# Directorio dotdotpwn para informes generados por dotdotpwn
def createDirectories():
   scriptsToRun = "dirb","dirb/80","dirb/443","dotdotpwn","finger","ftp","http","ldap","msrpc","mssql","mysql","nfs","nikto","nmap","rdp","rpc","smb","smtp","snmp","ssh","ssl","telnet","tftp","whatweb"
   for path in scriptsToRun:
      mkdir_p("%s/%s" % (OUTPUT_DIR,path))
   mkdir_p("/usr/share/dotdotpwn/Reports")

def backupExisting():
   print("INFO: Carpetas anteriores encontradas, empaquetando copia de seguridad")
   # Mover temporalmente targets.txt, comprimir archivos, respaldar, limpiar directorios y restaurar targets.txt
   movedTargets = False
   movedDotTemplate = False
   if os.path.isfile("%s/targets.txt" % (OUTPUT_DIR)):
      os.rename("%s/targets.txt" % (OUTPUT_DIR), "/root/scripts/recon_enum/results/targets.txt")
      movedTargets = True
   if os.path.isfile("%s/dot_template" % (OUTPUT_DIR)):
      os.rename("%s/dot_template" % (OUTPUT_DIR), "/root/scripts/recon_enum/results/dot_template")
      movedDotTemplate = True
   backupName = "backup_%s.tar.gz" % (time.strftime("%H:%M"))
   BACKUP = "tar czf /root/Downloads/%s %s/* --remove-files" % (backupName,OUTPUT_DIR)
   subprocess.check_output(BACKUP, shell=True)
   if movedTargets == True:
      os.rename("/root/scripts/recon_enum/results/targets.txt", "%s/targets.txt" % (OUTPUT_DIR))
   if movedDotTemplate == True:
      os.rename("/root/scripts/recon_enum/results/dot_template", "%s/dot_template" % (OUTPUT_DIR))

# Enlazar simbólicamente directorios requeridos a /usr/share/wordlists
# Funcionalidad diseñada para distribuciones como Kali Linux
# La carpeta de wordlists es utilizada por scripts de reconocimiento ftp y ssh
def mksymlink():
   dirsToLink = "/root/lists","/root/lists/SecLists-master"
   dst = "/usr/share/wordlists"
   for path in dirsToLink:
      if os.path.isdir(path):
         tmp = path.split("/")
         try:
            os.symlink(path, dst + "/" + tmp[-1])
         except OSError as exc:
            if exc.errno == errno.EEXIST:
               pass
            else:
               raise
      else:
         print("ADVERTENCIA [reconscan]: " + path + " no existe y no puede enlazarse simbólicamente. Esto puede causar inconvenientes en submódulos.")

# Banner principal informativo
def printBanner():
   print("##############################################################")
   print("####                      RECON SCAN                      ####")
   print("####          Escáner de servicios multiproceso           ####")
   print("####        finger, http, mssql, mysql, nfs, nmap,        ####")
   print("####        rdp, smb, smtp, snmp, ssh, telnet, tftp       ####")
   print("##############################################################")
   print("############# No olvides iniciar tu TCPDUMP #############")
   print("############ No olvides iniciar tu RESPONDER ############")
   print("##############################################################")
   print("##### Esta herramienta depende de varias utilidades. Asegúrate #####")
   print("##### de ejecutar setup.sh primero y tenerlas en tu PATH       #####")
   print("##############################################################")

# El script crea los directorios donde se colocarán los resultados
# El usuario debe indicar los objetivos en results/exam/targets.txt
if __name__=='__main__':
   parser = argparse.ArgumentParser(description='Script para gestionar escaneos Nmap y enumeración detallada de servicios descubiertos. Uso: reconscan.py <opciones>')
   parser.add_argument('-t','--target-list',dest='targetFile',default='/root/scripts/recon_enum/results/exam/targets.txt',help='Especificar manualmente la lista de objetivos a enumerar separados por saltos de línea.')
   # POR HACER (TODO): una única lista de usuario/contraseña no aplica para todos los servicios
   #parser.add_argument('-U','--user-list',dest='userFile',default='',help='Especificar manualmente una lista de usuarios para fuerza bruta.')
   #parser.add_argument('-P','--password-list',dest='passwordFile',default='',help='Especificar manualmente una lista de contraseñas para fuerza bruta.')
   #parser.add_argument('--hydra',dest='hydra',default=False,action='store_true',help='Invocar fuerza bruta con Hydra. Por defecto False.')
   args = parser.parse_args()

   targets = args.targetFile

   # VARIABLES PRIVADAS
   userAgent = "'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'" # Reemplaza el User-Agent HTTP por defecto de Nmap
   FAST_NMAP_MIN_RATE = "1000"
   SLOW_NMAP_MIN_RATE = "100"
   OUTPUT_DIR = "/root/scripts/recon_enum/results/exam"

   printBanner()
   if os.path.isdir('/root/scripts/recon_enum/results/exam/nmap'):
      backupExisting()

   mksymlink()
   createDirectories()

   # Tomar los hosts activos del escaneo de descubrimiento para enumeración
   # También verificar User-Agent de Nmap
   if os.path.isfile(targets):
       if os.path.getsize(targets) > 2: # 0 está vacío, 2 es archivo con \n
           try:
               with open(targets,'r') as f:
                  for scanip in f:
                     jobs = []
                     if scanip[0] != "#":
                        p = multiprocessing.Process(target=nmapFullFastScan, args=(scanip,)) # coma requerida para pasar un solo argumento
                        jobs.append(p)
                        p.start()
           except:
               raise
       else:
           print("ERROR: ¿targets.txt está vacío? Asegúrate de poblar targets.txt. Ejecuta aliverecon.py o similar.")
           exit(1)
   else:
        print("ERROR: ¡No se detectó targets.txt! Asegúrate de poblar targets.txt. Ejecuta aliverecon.py o similar.")
        exit(1)
