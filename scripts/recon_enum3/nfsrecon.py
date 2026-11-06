#!/usr/bin/python

import sys
import os
import subprocess
import argparse
import errno
import pathlib

# POR HACER (TODO): este módulo dependía de nfspy para ciertas comprobaciones. Evaluar dockerizar nfspy y reimplementarlo

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# En ejecución:
# nfs-ls: intenta obtener información útil sobre archivos desde los recursos compartidos NFS (exports)
# nfs-showmount: muestra recursos compartidos NFS similar a 'showmount -e'
# nfs-statfs: obtiene espacio en disco de NFS similar a 'df'
def doNmap(ip_address, port):
    print("INFO: Iniciando nfs con nmap en %s:%s" % (ip_address, port))
    if len(port.split(",")) > 1:
        for ports in port.split(","):
            outfileNmap = "/root/scripts/recon_enum/results/exam/nfs/%s_%s_nfsnmap" % (ip_address, ports)  
            subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',ports,'--script','nfs-ls,nfs-showmount,nfs-statfs,vulners',"-oA",outfileNmap,ip_address],encoding='utf8')
    else:
        outfileNmap = "/root/scripts/recon_enum/results/exam/nfs/%s_%s_nfsnmap" % (ip_address, port)
        subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','nfs-ls,nfs-showmount,nfs-statfs,vulners',"-oA",outfileNmap,ip_address],encoding='utf8')
    print("INFO: Nfs con nmap completado en %s:%s" % (ip_address, port))
    return

def doSysCommands(ip_address, port):
    print("INFO: Iniciando sysCommands para nfs en %s:%s" % (ip_address, port))
    f = open(outfile,'w')
    DEVNULL = open(os.devnull, 'w')
    try:
        results1 = subprocess.check_output(['showmount','-a',ip_address],encoding='utf8',stderr=DEVNULL)
        if results1:
            f.write("Showmount -a: " + "\n")
            f.write(results1)
            f.write("\n")
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            print("No fue posible ejecutar showmount -a, intentar manualmente")
        else:
            print("Error inesperado en nfsrecon doSysCommands 1")
    try:
        results2 = subprocess.check_output(['showmount','-e',ip_address],encoding='utf8',stderr=DEVNULL)
        DEVNULL.close()
        if results2:
            f.write("Showmount -e: " + "\n")
            f.write(results2)
            f.write("\n")
            f.close()
        results = results2.split("\n")
        doNfspy(results)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            print("No fue posible ejecutar showmount -e, intentar manualmente")
        else:
            print("Error inesperado en nfsrecon doSysCommands 2")


def doNfspy(results):
    for res in results:
        if "/" in res:
            try:
                sharename = res.split(" ")[0] # capturar solo el recurso montado
                fqsharename = "%s:%s" % (ip_address, sharename)
                if os.path.isfile('/bin/nfspy'):
                    try:
                        dir = sharename.split("/")[-1] # tomar último elemento para asignarle nombre
                        dir = "/mnt/%s" % dir
                        if not os.path.isdir(dir):
                            mkdir_p(dir)
                        subprocess.check_output(['nfspy',dir,'-o','server=%s,getroot,hide,allow_root,rw' % (fqsharename)],encoding='utf8')
                        print("INFO: %s debería estar montado en %s" % (sharename, dir))
                    except:
                        print("Error en NFSRecon, fallo en nfspy")
            except:
                print("Ocurrió un error con nfspy o en la creación. Probar manualmente para: %s" % res)
    print("INFO: sysCommands para nfs completado en %s:%s" % (ip_address, port))
    return


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar la enumeración de NFS. Uso: nfsrecon.py ip {port}')
    parser.add_argument('ip', help="Dirección IP del objetivo")
    parser.add_argument('--port', default='111,2049', help="Puerto. Por defecto 111,2049")

    args = parser.parse_args()
    ip_address = args.ip
    
    if args.port != '111,2049':
        port = '111,2049,%s' % args.port # requiere rpc para los scripts de nmap
    else:
        port = '111,2049'

    BASE = "/root/scripts/recon_enum/results/exam/nfs"
    mkdir_p(BASE)
    outfile = "/root/scripts/recon_enum/results/exam/nfs/%s_%s_nfsrecon.txt" % (ip_address, port)
      

    doNmap(ip_address, port)
    doSysCommands(ip_address, port)
    print("INFO: nfsRecon completado para %s:%s" % (ip_address, port))
