#!/usr/bin/env python
import subprocess
import sys
import argparse
import pathlib

# Documentación de Scripts NSE
# En ejecución:
# rdp-enum-encryption: determina el nivel de cifrado soportado en RDP
# rdp-vuln-ms12-020: comprueba vulnerabilidad MS12-020 en RDP (DoS y posible RCE)

# No en ejecución:
# rdp-ntlm-info: extrae información NTLM si está soportada
def doNmap():
    print("INFO: Realizando escaneo de scripts RDP con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=banner,rdp-enum-encryption,rdp-vuln-ms12-020,vulners','-oA','%s/%s_%s_rdp' % (BASE,ip_address,port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error desconocido en doNmap en rdprecon")

# Configuración por defecto de Hydra con listas reducidas para password spraying
def doHydra():
    print("INFO: Realizando escaneo RDP con Hydra contra %s. Esto puede tomar bastante tiempo" % (ip_address))
    hydra_outfile = '%s/%s_%s_rdphydra.txt' % (BASE,ip_address,port)
    try:
        subprocess.check_output(['hydra','-L','/root/lists/userlist.txt','-P','/root/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-t','4','-u',ip_address,'-s',port,'rdp'],encoding='utf8')
        with open(hydra_outfile,'r') as h:
            for result in h:
                if "login:" in result:
                    print("[*] Credenciales RDP válidas encontradas: %s" % (result))
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa rdphydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: No se encontraron credenciales RDP válidas")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints RDP. Uso: rdprecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/rdp'
    mkdir_p(BASE)

    doNmap()
    if args.hydra:
        doHydra()
