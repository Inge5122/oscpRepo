#!/usr/bin/env python
import subprocess
import sys
import os
import argparse
import pathlib

# Documentación de Scripts NSE
# EN EJECUCIÓN:
# ftp-anon: comprueba si el servidor FTP permite acceso anónimo y lista el contenido
# ftp-bounce: comprueba si permite escaneo de puertos mediante el método FTP bounce
# ftp-proftpd-backdoor: comprueba puerta trasera en ProFTPD 1.3.3c (OSVDB-ID 69562)
# ftp-syst: envía comandos SYST y STAT para consultar información del SO y estado del servidor
# ftp-vsftpd-backdoor: comprueba puerta trasera en vsFTPd 2.3.4 (CVE-2011-2523)
# ftp-vuln-cve-2010-4221: comprueba desbordamiento de búfer en ProFTPD 1.3.2rc3 a 1.3.3b
# tftp-enum: fuerza bruta de nombres de archivo comunes sobre TFTP (UDP)

# NO EN EJECUCIÓN:
# ftp-brute: fuerza bruta de credenciales FTP
# ftp-libopie: comprueba CVE-2010-1938 (puede bloquear el servicio)
def doNmap():
    print("INFO: Realizando escaneo de scripts FTP con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=banner,ftp-anon,ftp-bounce,ftp-syst,ftp-proftpd-backdoor,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221,tftp-enum,vulners','-oA',"%s/%s_%s_ftp" % (BASE,ip_address,port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error desconocido en doNmap en ftprecon")

# usuario: anonymous
# password: guest
def doHydra():
    print("INFO: Realizando escaneo FTP con Hydra contra %s" % (ip_address))
    hydra_outfile = "%s/%s_%s_ftphydra.txt" % (BASE,ip_address,port)
    try:
        subprocess.check_output(['hydra','-L','/usr/share/wordlists/lists/userlist.txt','-P','/usr/share/wordlists/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-u',ip_address,'-s',port,'ftp'],encoding='utf8')
        with open(hydra_outfile,'r') as h:
            for result in h:
                if "login:" in result:
                    print("[*] Credenciales FTP válidas encontradas: " + result)
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa ftphydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: No se encontraron credenciales FTP válidas")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints FTP y TFTP. Uso: ftprecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows/Linux objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/ftp'
    mkdir_p(BASE)

    doNmap()
    if args.hydra:
        doHydra()
