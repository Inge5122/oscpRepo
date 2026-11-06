#!/usr/bin/env python
import subprocess
import sys
import argparse
import pathlib

# Documentación de Scripts NSE
# En ejecución:
# telnet-encryption: determina si soporta cifrado
# telnet-ntlm-info: extrae información NTLM de Microsoft Telnet

# No en ejecución:
# telnet-brute: auditoría de contraseñas por fuerza bruta
def doNmap():
    print("INFO: Realizando escaneo de scripts Telnet con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=banner,telnet-encryption,telnet-ntlm-info,vulners','-oA','%s/%s_%s_telnet' % (BASE,ip_address,port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error desconocido en doNmap en telnetrecon")

# Hydra configurado para spray débil, no exhaustivo
def doHydra():
    print("INFO: Realizando escaneo Telnet con Hydra contra %s" % (ip_address))
    hydra_outfile = '%s/%s_%s_telnethydra.txt' % (BASE,ip_address,port)
    try:
        subprocess.check_output(['hydra','-L','/root/lists/userlist.txt','-P','/root/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-u',ip_address,'-s',port,'telnet'],encoding='utf8')
        with open(hydra_outfile,'r') as h:
            for result in h:
                if "login:" in result:
                    print("[*] Credenciales Telnet válidas encontradas: %s" % (result))
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa telnethydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: No se encontraron credenciales Telnet válidas")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints Telnet. Uso: telnetrecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/telnet'
    mkdir_p(BASE)

    doNmap()
    if args.hydra:
        doHydra()
