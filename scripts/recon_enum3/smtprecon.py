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

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# Documentación de Scripts NSE
# En ejecución:
# smtp-commands: intenta usar EHLO y HELP para recopilar comandos extendidos soportados [--script-args smtp-commands.domain=<dominio>]
# smtp-enum-users: intenta enumerar usuarios mediante comandos VRFY, EXPN o RCPT TO. Se detiene si se exige autenticación.
# smtp-ntlm-info: enumera servidores que permiten autenticación NTLM. Enviar NTLM NULL devuelve NetBIOS, DNS y versión del SO.
# smtp-vuln-cve2011-1764: comprueba vulnerabilidad de formato de cadena en Exim 4.70-4.75 con soporte DKIM (CVE-2011-1764).
# pop3-capabilities: obtiene las capacidades del servidor de correo POP3
# pop3-ntlm-info: enumera información de POP3 con autenticación NTLM activada

# No en ejecución:
# smtp-brute: Fuerza bruta de login/plain/cram-md5/digest-md5/NTLM
# smtp-open-relay: intenta relay de correo mediante combinación de comandos SMTP
# smtp-strangeport: comprueba si SMTP se ejecuta en puertos no estándar
# smtp-vuln-cve2010-4344: comprueba desbordamiento de Heap en versiones de EXIM previas a 4.69 (CVE-2010-4344) y escalada de privilegios previa a 4.72 (CVE-2010-4345)
# smtp-vuln-cve2011-1720: comprueba corrupción de memoria en servidor Postfix al usar biblioteca Cyrus SASL (CVE-2011-1720)
def doNmap():
    print("INFO: Realizando escaneo de scripts SMTP con nmap para %s:25,110,143,465,587,993,995" % (ip_address))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p','25,110,143,465,587,993,995','--script','banner,smtp-commands,smtp-enum-users,smtp-ntlm-info,smtp-vuln-cve2011-1764,pop3-capabilities,pop3-ntlm-info,vulners','-oA',nmap_outfile,ip_address],encoding='utf8')

# nmap --script=smtp-enum-users a veces genera error incluso si la información es accesible.
# Añadido segundo método con smtp-user-enum
def doSmtpUserEnum():
    if os.path.isfile('/usr/bin/smtp-user-enum'):
        try:
            results = subprocess.check_output(['smtp-user-enum','-U',userlist,'-t',ip_address],encoding='utf8')
            f = open(smtpuserenum_outfile, "w")
            if results:
                f.write(results)
            f.close()
        except Exception as e:
            print(type(e))
            print("Problema inesperado en doSmtpUserEnum en smtprecon")

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints SMTP. Uso: smtprecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    userlistAlt = "/root/lists/secLists/Usernames/Honeypot-Captures/multiplesources-users-fabian-fingerle.de.txt"
    userlist = "/usr/share/wordlists/metasploit/unix_users.txt"

    BASE = "/root/scripts/recon_enum/results/exam/smtp"
    mkdir_p(BASE)

    nmap_outfile = "%s/%s_%s_smtp" % (BASE,ip_address,port)
    smtpuserenum_outfile = "%s/%s_%s_smtp_user_enum" % (BASE,ip_address,port)

    doNmap()
    doSmtpUserEnum()
