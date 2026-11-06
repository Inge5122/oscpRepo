#!/usr/bin/env python
import subprocess
import sys
import argparse
import pathlib

# POR HACER (TODO): requiere que la lista de comunidades SNMP se encuentre en la ruta esperada

# Si "#mibs :" no está en /etc/snmp/snmp.conf
# puedes ejecutar 'apt install snmp-mibs-downloader', comentar /etc/snmp/snmp.conf y obtener salida legible de MIBs
snmpdetect = 0

# -c <archivo_comunidades> archivo con nombres de comunidad a probar
# -i <archivo_entrada> archivo con hosts objetivo
# -o <archivo_salida> registro de salida
# -d modo depuración, usar dos veces para mayor información
# -w n esperar n milisegundos entre paquetes (por defecto 10)
# -q modo silencioso, no imprimir a stdout, usar con -l
def onesixtyone():
    # snmp_all_communities proviene de seclists con 3250 cadenas
    print("INFO: Realizando fuerza bruta con onesixtyone para %s:161" % (ip_address))
    results = subprocess.check_output(['onesixtyone','-o',ONESIXTYONE_RESULTS,ip_address,'-c',SNMP_COMMUNITY_STRINGS],encoding='utf8')
    if results != "":
        return True
    else:
        return False

# Documentación de Scripts NSE
# En ejecución:
# snmp-hh3c-logins: intenta enumerar usuarios definidos localmente en Huawei / HP / H3C mediante OID hh3c-user.mib --script-args creds.snmp=:<comunidad>
# snmp-info: extrae información básica de peticiones SNMPv3 GET
# snmp-ios-config: intenta descargar archivos de configuración IOS de routers Cisco mediante SNMP RW (v1) y guardarlos --script-args creds.snmp=:<comunidad>
# snmp-netstat: consulta información similar a netstat para identificar y añadir nuevos objetivos
# snmp-processes: enumera procesos en ejecución mediante SNMP
# snmp-sysdescr: extrae información del sistema mediante el servicio SNMP v1
# snmp-win32-services: enumera servicios de Windows mediante SNMP
# snmp-win32-shares: enumera recursos compartidos de Windows mediante SNMP
# snmp-win32-software: enumera software instalado en Windows mediante SNMP
# snmp-win32-users: enumera cuentas de usuario de Windows mediante SNMP

# No en ejecución:
# snmp-interfaces: intenta enumerar interfaces de red mediante SNMP. Requiere snmp-interfaces.host
# snmp-brute: fuerza bruta de cadenas de comunidad
def nmap_communities(community):
    print("INFO: Realizando escaneo de scripts SNMP con nmap para %s:161 y comunidad %s" % (ip_address, community))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-sU','-p','%s' % port,'--script=snmp-brute,snmp-hh3c-logins,snmp-info,snmp-ios-config,snmp-netstat,snmp-processes,snmp-sysdescr,snmp-win32-services,snmp-win32-shares,snmp-win32-software,snmp-win32-users,vulners','--script-args',"creds.snmp=:%s" % community,'-oA','%s/%s_%s_snmp.nmap' % (BASE,ip_address,community),ip_address],encoding='utf8')

def nmap():
    print("INFO: Realizando escaneo de scripts SNMP con nmap para %s:161,162 SIN COMUNIDAD" % (ip_address))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-sU','-p',port,'161,162','--script=snmp-brute,snmp-hh3c-logins,snmp-info,snmp-ios-config,snmp-netstat,snmp-processes,snmp-sysdescr,snmp-win32-services,snmp-win32-shares,snmp-win32-software,snmp-win32-users,vulners','-oA','%s/%s_%s_snmp.nmap' % (BASE,ip_address,port),ip_address],encoding='utf8')

# Versión v1.8 (escrita en Perl) / v1.9 (escrita en Ruby)
# -p : puerto SNMP (por defecto 161)
# -c : comunidad SNMP (por defecto public)
# -v : versión SNMP (1, 2c)
# -w : detectar acceso de escritura (acción separada por enumeración)
# -d : deshabilitar enumeración de conexiones TCP
# -t : tiempo de espera en segundos
def snmp_check(community):
    print("INFO: Realizando SNMP_check para %s:161 con la(s) comunidad(es) encontrada(s)" % (ip_address))

    snmp18_1_outfile = "%s/%s_%s_snmpcheck_v1" % (BASE,ip_address,community)
    snmp18_2_outfile = "%s/%s_%s_snmpcheck_v2" % (BASE,ip_address,community)
    snmp19_1_outfile = "%s/%s_%s_snmpcheck_v1" % (BASE,ip_address,community)
    snmp19_2_outfile = "%s/%s_%s_snmpcheck_v2c" % (BASE,ip_address,community)

    # Verificación de versión por compatibilidad. 1.8 requiere -t para el objetivo, mientras que 1.9 no.
    version = subprocess.check_output(['snmp-check','-h'],encoding='utf8')
    if "v1.8" in version:
        results = subprocess.check_output(['snmp-check','-v','1','-c',community,'-w','-t',ip_address],encoding='utf8')
        if results:
            f = open(snmp18_1_outfile,'w')
            for res in results:
                f.write(res)
            f.close()
            snmpwalk("1", community)
        results = subprocess.check_output(['snmp-check','-v','2','-c',community,'-w','-t',ip_address],encoding='utf8')
        if results:
            f = open(snmp18_2_outfile,'w')
            for res in results:
                f.write(res)
            f.close()
            snmpwalk("2c", community)
    if "v1.9" in version:
        results = subprocess.check_output(['snmp-check','-v','1','-c',community,'-w',ip_address],encoding='utf8')
        if results:
            f = open(snmp19_1_outfile,'w')
            for res in results:
                f.write(res)
            f.close()
            snmpwalk("1", community)
        results = subprocess.check_output(['snmp-check','-v','2c','-c',community,'-w',ip_address],encoding='utf8')
        if results:
            f = open(snmp19_2_outfile,'w')
            for res in results:
                f.write(res)
            f.close()
            snmpwalk("2c", community)
    return True

# snmpwalk: recorre el árbol MIB mediante SNMP
# -v 1|2c|3: versión de SNMP
# -c COMMUNITY: cadena de comunidad
def snmpwalk(version, community):
    print("Recorriendo árbol con snmpwalk")
    outfile = "/root/scripts/recon_enum/results/exam/snmp/%s_%s_snmpwalk_%s" % (ip_address, community, version)
    results = subprocess.check_output(['snmpwalk','-c',community,'-v',version,ip_address])
    if results:
        f = open(outfile, 'w')
        for res in results:
            f.write(res)
        f.close()

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints SNMP. Uso: snmprecon.py <dirección_ip>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows/Linux objetivo")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = 161
    
    BASE = '/root/scripts/recon_enum/results/exam/snmp'
    mkdir_p(BASE)

    SNMP_COMMUNITY_STRINGS = "/root/lists/snmp_all_communities.txt"
    ONESIXTYONE_RESULTS = '%s/%s_%s_onesixtyone' % (BASE,ip_address,port)

    communities = onesixtyone()
    if communities:
        print("¡Comunidades encontradas! Pasando a nmap y snmp_check")
        f = open(ONESIXTYONE_RESULTS,'r')
        for community in f:
            if "[" and "]" in community:
                community = community.split("[")[1].split("]")[0]
            nmap_communities(community)
            snmp_check(community)
        f.close()
    else:
        nmap()
    print("INFO: snmpRecon completado. Si se detectaron comunidades y requieres más información que la devuelta por snmp-check, consulta snmpwalk manualmente")
