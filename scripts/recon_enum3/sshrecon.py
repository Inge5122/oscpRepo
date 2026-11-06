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

# Documentación de Scripts NSE
# En ejecución:
# ssh-auth-methods: Devuelve los métodos de autenticación soportados por el servidor SSH
# ssh2-enum-algos: Reporta el número y lista de algoritmos ofrecidos por el servidor
# sshv1: Comprueba si el servidor soporta el protocolo obsoleto e inseguro SSHv1

# No en ejecución:
# ssh-brute: Fuerza bruta de credenciales contra servidores SSH
# ssh-hostkey: Muestra la huella digital de la clave del host y la clave pública
# ssh-publickey-acceptance: Fuerza bruta con claves privadas, frases de paso y usuarios
# ssh-run: Ejecuta un comando remoto en el servidor SSH y retorna la salida
def doSSHNmap():
    print("INFO: Realizando SSH con nmap para %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=banner,ssh-auth-methods,sshv1,ssh2-enum-algos,vulners','-oA','%s/%s_%s_ssh' % (BASE,ip_address,port),ip_address],encoding='utf8')
    print("INFO: Finalizado SSH con nmap para %s:%s" % (ip_address, port))
    return

def doSSLRecon():
    print("INFO: Iniciando sslrecon con nmap para %s:%s" % (ip_address, port))
    subprocess.check_output(['./sslrecon.py', ip_address, port],encoding='utf8')
    print("INFO: Finalizado sslrecon con nmap para %s:%s" % (ip_address, port))
    return

def doOpenSSLConnect():
    ## openssl s_client -connect servidor:puerto para identificar versión exacta de OpenSSL
    outPath = "%s/%s_%s_openssl_connect" % (BASE, ip_address,port)
    errPath = "%s/%s_%s_openssl_connect_err" % (BASE, ip_address,port)
    try:
        subprocess.run(['openssl','s_client','-connect','%s:%s' % (ip_address,port)],encoding='utf8',check=True,stdout=outPath,stderr=errPath).stdout
    except subprocess.CalledProcessError as e:
        print(type(e))
        print("Error inesperado en doOpenSSLConnect en sshrecon")
        pass
    print("TTP: Recuerda, en OpenSSH 2.3<7.4 es posible enumerar usuarios con la PoC (https://www.exploit-db.com/exploits/45210/)")

def doHydra():
    print("INFO: Realizando escaneo SSH con Hydra contra %s:%s" % (ip_address, port))
    try:
        hydra_outfile = '%s/%s_%s_sshhydra.txt' % (BASE, ip_address, port)
        subprocess.check_output(['hydra','-L',args.userlist,'-P',args.passlist,'-f','-t',args.threads,'-o',hydra_outfile,'-u',ip_address,'-s',port,'ssh'],encoding='utf8')
        with open(hydra_outfile,'r') as h:
            for line in h:
                if "login:" in h:
                    print("[*] Credenciales válidas de SSH encontradas para %s: " + line % (ip_address))
    except subprocess.CalledProcessError as hydrerr:
        if hydrerr.returncode == 255:
            print("Hydra finalizó antes con código 255, ¡debe haber encontrado algo! Revisa sshhydra para ver la salida.")
        elif hydrerr.returncode != 0:
            print("Hydra falló:")
            print(hydrerr.returncode)
            print(hydrerr.output)
        else:
            print("INFO: [hydra] No se encontraron credenciales SSH válidas para %s:%s" % (ip_address, port))

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para gestionar enumeración SSH y fuerza bruta si se especifica (deshabilitada por defecto). Uso: sshrecon.py {--hydra} target port')
    parser.add_argument('--hydra', default=False, action='store_true', dest='hydra', help="Especificar para ejecutar Hydra")
    parser.add_argument('-L', '--userlist', default='/root/lists/userlist.txt', help="Especificar lista de usuarios para Hydra")
    #parser.add_argument('-l', '--login', help="Especificar un único usuario para Hydra")
    parser.add_argument('-P', '--passlist', default='/root/lists/quick_password_spray.txt', help="Especificar lista de contraseñas para Hydra")
    #parser.add_argument('p', '--password', help="Especificar una única contraseña para Hydra")
    parser.add_argument('-t', '--threads', default='4', help="Especificar hilos para Hydra")
    parser.add_argument('target', help="IP objetivo")
    parser.add_argument('port', help="Puerto con servicio SSH")

    args = parser.parse_args()

    ip_address = args.target
    port = args.port

    BASE = '/root/scripts/recon_enum/results/exam/ssh'
    mkdir_p(BASE)

    doSSHNmap()
    doSSLRecon()
    doOpenSSLConnect()
    if args.hydra:
        doHydra()
