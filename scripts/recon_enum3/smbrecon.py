#!/usr/bin/python
import sys
import subprocess
import os
import errno
import multiprocessing
from multiprocessing import Process
import argparse
import pathlib

# POR HACER (TODO): añadir soporte para autenticación con contraseña
# POR HACER (TODO): algunas funciones pueden reemplazarse con CME, smbmap u otra herramienta para reducir dependencias externas.
#    Las dependencias externas actuales son nullinux y nbtscan-unixwiz

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# Documentación de Scripts NSE
# En ejecución:
# smb-double-pulsar-backdoor: comprueba si el objetivo tiene activa la puerta trasera Double Pulsar SMB
# smb-enum-domains: intenta enumerar dominios en el sistema con sus políticas (suele requerir credenciales)
# smb-enum-groups: obtiene lista de grupos remotos y usuarios asociados (similar a 'enum.exe /g')
# smb-enum-processes: obtiene lista de procesos remotos vía SMB consultando el registro remoto (requiere Admin)
# smb-enum-sessions: enumera usuarios conectados localmente o mediante recurso compartido
# smb-enum-shares: enumera recursos compartidos mediante srvsvc.NetShareEnumAll y NetShareGetInfo
# smb-enum-users: enumera usuarios en sistema remoto mediante MSRPC por puertos 445 o 139 (SAMR y LSA)
# smb-ls: obtiene información detallada sobre archivos en volúmenes compartidos SMB (similar a 'ls')
# smb-os-discovery: determina SO, nombre del equipo, dominio, grupo de trabajo y hora actual vía SMB (anónimo)
# smb-protocols: comprueba versiones soportadas de SMB; si detecta SMBv1 lo marca como inseguro
# smb-security-mode: muestra información de seguridad de SMB (firmado, challenge-response, etc.)
# smb-system-info: extrae información del registro remoto
# smb-vuln-cve-2017-7494: comprueba vulnerabilidad de carga de librerías arbitrarias en Samba (CVE-2017-7494 / SambaCry)
# smb-vuln-ms17-010: comprueba vulnerabilidad MS17-010 (EternalBlue) conectándose al árbol $IPC
# smb-vuln-ms10-061: comprueba vulnerabilidad MS10-061 de suplantación en Printer Spooler
# smb2-security-mode: determina configuración de firma de mensajes en servidores SMBv2
# smb2-vuln-uptime: detecta parches faltantes comprobando el tiempo de actividad devuelto en la negociación SMB2
# samba-vuln-cve-2012-1182: comprueba ejecución remota como root desde conexión anónima en Samba
# nbstat: obtiene nombres NetBIOS y dirección MAC del objetivo

# No en ejecución:
# smb-brute: fuerza bruta de credenciales sobre SMB
# smb-enum-services: lista servicios en ejecución (requiere Admin)
# smb-flood: agota el límite de conexiones del servidor SMB remoto
# smb-mbenum: consulta información gestionada por el Windows Master Browser
# smb-print-text: prueba impresión en impresoras compartidas vía RPC
# smb-psexec: módulo de ejecución remota psexec (requiere configuración previa)
# smb-server-stats: estadísticas del servidor SMB (requiere Admin)
# smb-vuln-conficker: detecta infección por gusano Conficker (puede desestabilizar el host)
# smb-vuln-cve2009-3103: vulnerabilidad de denegación de servicio (bloquea el servicio)
# smb-vuln-ms06-025: vulnerabilidad en RasRPCSubmitRequest RPC
# smb-vuln-ms07-029: vulnerabilidad DNS RPC (puede bloquear el servicio)
# smb-vuln-ms08-067: vulnerabilidad crítica MS08-067
# smb-vuln-ms10-054: vulnerabilidad MS10-054 (genera pantallazo azul BSOD)
# smb-vuln-regsvc-dos: desreferencia a puntero nulo en regsvc
# smb2-capabilities: lista capacidades de dialectos soportados en SMBv2
# smb2-time: obtiene fecha y hora de inicio de servidores SMB2
def doNmap():
    print("INFO: Realizando escaneo de scripts SMB con nmap para %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script=smb-double-pulsar-backdoor,smb-enum-domains,smb-enum-groups,smb-enum-processes,smb-enum-sessions,smb-enum-shares,smb-enum-users,smb-ls,smb-os-discovery,smb-protocols,smb-security-mode,smb-system-info,smb-vuln-cve-2017-7494,smb-vuln-ms10-061,smb-vuln-ms17-010,smb2-security-mode,smb2-vuln-uptime,samba-vuln-cve-2012-1182,nbstat,vulners','-oA',nmap_outfile,ip_address],encoding='utf8')

def doSAMR():
    print("INFO: Intentando escaneo samrdump no autenticado para %s:%s" % (ip_address, port))
    try:
        results = subprocess.check_output(['samrdump.py',ip_address],encoding='utf8').split("\n")
        f = open(samr_outfile,'w')
        for res in results:
            f.write(res)
            if "\n" not in res:
                f.write("\n")
        f.close()
    except Exception as e:
        print(type(e))
        print("Problema inesperado en doSAMR en smbrecon")

#-va:   ejecutar en modo detallado y probar todos los comandos
#-U:    obtener lista de usuarios
#-M:    obtener lista de máquinas
#-S:    obtener lista de recursos compartidos (shares)
#-P:    obtener información de directiva de contraseñas
#-G:    obtener grupos y miembros
#-d:    modo detallado, aplica a -U y -S
#-a:    -USGProni
#-r:    recorrido de RID (RID cycling)
#-l:    información limitada vía LDAP 389 (solo controladores de dominio)
#-o:    obtener información del SO
#-i:    obtener información de impresoras
#-n:    realizar nmblookup
#-v:    modo detallado (verbose)
def doEnum4Linux():
    print("INFO: Realizando escaneo enum4linux para %s:%s" % (ip_address, port))
    try:
        results = subprocess.check_output(['enum4linux','-va',ip_address],encoding='utf8').split("\n")
        if results:
            f = open(enum4linux_outfile,'w')
            for res in results:
                f.write(res)
                if "\n" not in res:
                    f.write("\n")
            f.close()
    except subprocess.CalledProcessError:
        print("ADVERTENCIA: enum4linux finalizó con código distinto de 0 para %s, pero la salida se registrará" % (ip_address))

# Opciones de nbtscan-unixwiz:
# -V        mostrar información de versión
# -f        mostrar respuestas completas de registros NBT (recomendado)
# -H        generar cabeceras HTTP
# -v        modo de depuración detallado
# -n        no buscar nombres inversos
# -p <n>    vincular al puerto UDP <n> (por defecto 0)
# -m        incluir dirección MAC en la respuesta (implícito con -f)
# -T <n>    tiempo de espera en segundos (por defecto 2s)
def doNbtscanUnixWiz():
    print("INFO: Realizando escaneo nbtscan-unixwiz para %s:%s" % (ip_address, port))
    try:
        results = subprocess.check_output(['nbtscan-unixwiz','-f',ip_address],encoding='utf8').split("\n")
        f = open(nbtscanunixwiz_outfile,'w')
        for res in results:
            f.write(res)
            if "\n" not in res:
                f.write("\n")
        f.close()
    except Exception as e:
        print(type(e))
        print("Problema inesperado en doNbtscanUnixWiz en smbrecon")

# Opciones de nullinux:
# -shares   enumerar dinámicamente recursos compartidos
# -users    enumerar usuarios mediante diversas técnicas
# -quick    enumeración rápida sin fuerza bruta
# -U        especificar usuario (opcional)
# -P        especificar contraseña (opcional)
# -v        salida detallada
def doNullLinux():
    print("INFO: Realizando escaneo nullinux para %s:%s" % (ip_address, port))
    if os.path.isfile('/usr/local/bin/nullinux'):
        try:
            results = subprocess.check_output(['nullinux','-v',ip_address],encoding='utf8').split("\n")
            f = open(nullinux_outfile,'w')
            for res in results:
                f.write(res)
                f.write("\n")
            f.close()
        except Exception as e:
            print(type(e))
            print("Problema inesperado en doNullLinux en smbrecon")

def doSMBVer():
    # Relevante para ciertas versiones de SMB en Linux
    print("INFO: Comprobando versión de SMB para %s" % (ip_address))
    results = subprocess.check_output(['./smbver.sh',ip_address],encoding='utf8')
    f = open(smbver_outfile,'w')
    for res in results:
        f.write(res)
        f.write("\n")
    f.close()


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints SMB y recursos compartidos disponibles. Uso: smbrecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows/Linux objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    args = parser.parse_args()

    BASE = "/root/scripts/recon_enum/results/exam/smb"
    mkdir_p(BASE)

    ip_address = args.ip_address 
    port = args.port
    nmap_outfile = "%s/%s_%s_smb" % (BASE,ip_address,port)
    samr_outfile = "%s/%s_%s_samrdump" % (BASE,ip_address,port)
    enum4linux_outfile = "%s/%s_%s_enum4linux" % (BASE,ip_address,port)
    nbtscanunixwiz_outfile = "%s/%s_%s_nbtscan-unixwiz" % (BASE,ip_address,port)
    nullinux_outfile = "%s/%s_%s_nullinux" % (BASE,ip_address,port)
    smbver_outfile = "%s/%s_%s_smbversion" % (BASE,ip_address, port)

    doNmap()
    doSAMR()
    doEnum4Linux()
    doNbtscanUnixWiz()
    doNullLinux()
    doSMBVer()
