#!/usr/bin/python

import sys
import os
import subprocess
import argparse
import errno
import getpass
import pathlib

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

# Documentación de Scripts NSE
# En ejecución:
# ldap-novell-getpass: obtiene Novell Universal Password para un usuario (requiere cuenta admin)
# ldap-rootdse: obtiene la entrada raíz DSE de LDAP

# No en ejecución:
# ldap-brute: fuerza bruta de autenticación LDAP
# ldap-search: realiza búsqueda LDAP y devuelve coincidencias (requiere cuenta)
def doNmap():
    print("INFO: Iniciando LDAP con nmap en %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','ldap-novell-getpass,ldap-rootdse,vulners',"-oA",outfileNmap,ip_address],encoding='utf8')
    print("INFO: LDAP con nmap completado en %s:%s" % (ip_address, port))
    return

# Opciones de ad-ldap-enum.py:
# -v, --verbose                                     muestra información de depuración
# -o FILENAME_PREPEND, --prepend FILENAME_PREPEND   prefijo para nombres de archivos de salida
# -l LDAP_SERVER, --server LDAP_SERVER              dirección IP del servidor LDAP
# -d DOMAIN, --domain DOMAIN                        FQDN de la cuenta de autenticación
# -a ALT_DOMAIN, --alt-domain ALT_DOMAIN            FQDN alternativo como Base DN
# -e, --nested                                      expandir grupos anidados
# -n, --null                                        usar enlace nulo (null binding) anónimo
# -s, --secure                                      conectar sobre SSL
# -u USERNAME, --username USERNAME                  nombre de usuario
# -p PASSWORD, --password PASSWORD                  contraseña
def doADLdapEnum():
    # https://github.com/CroweCybersecurity/ad-ldap-enum
    print("INFO: Iniciando ADLdapEnum en %s:%s" % (ip_address, args.port))
    if args.username == "" and args.password == "" and args.domain == "":
        try: 
            if "," in args.port:
                ports = args.port.split(",")
                for port in ports:
                    outdirADLdapEnum = "%s/%s" % (BASE, port)
                    mkdir_p(outdirADLdapEnum)
                    ADLDAPENUM = "cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -n -v" % (outdirADLdapEnum, ip_address)
                    subprocess.call(ADLDAPENUM, shell=True)
            else:
                outdirADLdapEnum = "%s/%s" % (BASE, args.port)
                mkdir_p(outdirADLdapEnum)
                ADLDAPENUM = "cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -n -v" %(outdirADLdapEnum, ip_address)
                subprocess.call(ADLDAPENUM, shell=True)
        except subprocess.CalledProcessError as e:
            print("Código de error en ADLdapEnum: " + str(e.returncode) + "\n")
    else:
        try:
            if "," in args.port:
                ports = args.port.split(",")
                for port in ports:
                    outdirADLdapEnum = "%s/%s" % (BASE, port)
                    mkdir_p(outdirADLdapEnum)
                    if port == 636:
                        ADLDAPENUM = 'cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -d %s -u %s -p \'%s\' -s -v' % (outdirADLdapEnum, ip_address, args.domain, args.username, args.password)
                        results = subprocess.call(ADLDAPENUM,encoding='utf8',shell=True)
                    else:
                        ADLDAPENUM = "cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -d %s -u %s -p \'%s\' -v" % (outdirADLdapEnum, ip_address, args.domain, args.username, args.password)
                        results = subprocess.call(ADLDAPENUM,encoding='utf8',shell=True)
            else: 
                outdirADLdapEnum = "%s/%s" % (BASE, args.port)
                mkdir_p(outdirADLdapEnum)
                if args.port == 636:
                    ADLDAPENUM = "cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -d %s -u %s -p \'%s\' -s -v" % (outdirADLdapEnum, ip_address, args.domain, args.username, args.password)
                    results = subprocess.call(ADLDAPENUM, shell=True)
                else:
                    ADLDAPENUM = "cd %s && python /root/Documents/ADLdapEnum/ad-ldap-enum.py -l %s -d %s -u %s -p \'%s\' -v" % (outdirADLdapEnum, ip_address, args.domain, args.username, args.password)
                    results = subprocess.call(ADLDAPENUM, shell=True)
        except subprocess.CalledProcessError as e:
            print("Código de error en ADLdapEnum: " + str(e.returncode) + "\n")
    print("INFO: ADLdapEnum completado en %s:%s" % (ip_address, args.port))
    return

# Opciones de ldapdomaindump:
# HOSTNAME              Hostname/IP o cadena de conexión ldap://host:puerto (usar ldaps:// para SSL)
# -u USERNAME           DOMINIO\usuario para autenticación (vacío para anónimo)
# -p PASSWORD           Contraseña o hash LM:NTLM
# -at                   Tipo de autenticación (NTLM o SIMPLE, por defecto: NTLM)
# -o DIRECTORY          Directorio donde guardar el volcado
# --no-html / --no-json / --no-grep deshabilitar formatos de salida
# -r, --resolve         Resolver nombres de host de equipos
def doLdapDD():
    # https://github.com/dirkjanm/ldapdomaindump
    print("INFO: Iniciando LdapDD en %s:%s" % (ip_address, args.port))
    outfileLDD = "%s/%s_%s_ldd" % (BASE, ip_address, args.port)
    DEVNULL = open(os.devnull, 'w')
    if args.username == "" and args.password == "":
        if "," in args.port:
            ports = args.port.split(",")
            for port in ports:
                outfileLDD = "%s/%s_%s_ldd" % (BASE, ip_address, port)
                outfileDir = "%s/%s" % (BASE, port)
                mkdir_p(outfileDir)
                try:
                    subprocess.check_output(['ldapdomaindump','ldap://%s:%s' % (ip_address, port),'-o',outfileDir],encoding='utf8',stderr=DEVNULL)
                except subprocess.CalledProcessError as e:
                    f = open(outfileLDD, 'w')
                    f.write("Código de error: " + str(e.returncode) + "\n")
                    f.write("Salida de herramienta: " + e.output)
                    f.close()
        else:
            try:
                outfileDir = "%s/%s" % (BASE, args.port)
                mkdir_p(outfileDir)
                subprocess.check_output(['ldapdomaindump','ldap://%s:%s' % (ip_address, args.port),'-o',outfileDir],encoding='utf8', stderr=DEVNULL)
            except subprocess.CalledProcessError as e:
                f = open(outfileLDD, 'w')
                f.write("Código de error: " + str(e.returncode) + "\n")
                f.write("Salida de herramienta: " + e.output)
                f.close()
    else:
        if "," in args.port:
            ports = args.port.split(",")
            for port in ports:
                outfileLDD = "%s/%s_%s_ldd" % (BASE, ip_address, port)
                outfileDir = "%s/%s" % (BASE, port)
                mkdir_p(outfileDir)
                try:
                    subprocess.check_output(['ldapdomaindump','-u',args.username,'-p',args.password,'ldap://%s:%s' % (ip_address, port),'-o',outfileDir],encoding='utf8', stderr=DEVNULL)
                except subprocess.CalledProcessError as e:
                    f = open(outfileLDD, 'w')
                    f.write("Código de error: " + str(e.returncode) + "\n")
                    f.write("Salida de herramienta: " + e.output)
                    f.close()
        else:
            try:
                outfileDir = "%s/%s" % (BASE, args.port)
                mkdir_p(outfileDir)
                subprocess.check_output(['ldapdomaindump','-u',args.username,'-p',args.password,'ldap://%s:%s' % (ip_address, args.port),'-o',outfileDir],encoding='utf8', stderr=DEVNULL)
            except subprocess.CalledProcessError as e:
                f = open(outfileLDD, 'w')
                f.write("Código de error: " + str(e.returncode) + "\n")
                f.write("Salida de herramienta: " + e.output)
                f.close()
    print("INFO: LdapDD completado en %s:%s" % (ip_address, args.port))
    DEVNULL.close()
    return

# Opciones de ldapsearch:
# -b base dn
# -c continuo, no detenerse ante errores
# -D bind DN
# -h servidor LDAP
# -p puerto
# -x autenticación simple
def doLdapSearch():
    results = ""
    print("INFO: Iniciando ldapsearch en %s:%s" % (ip_address, args.port))
    
    f = open(outfileLdapSearch, 'w+')
    # No autenticado
    if "," in args.port:
        ports = args.port.split(",")
        for port in ports:
            try:
                basedn = getBaseDN()
                results = subprocess.check_output(['ldapsearch','-h',ip_address,'-p',port,'-x','-b',basedn],encoding='utf8')
                if results:
                    for res in results:
                        f.write(res)
            except subprocess.CalledProcessError as e:
                print("Código de error en ldapsearch no autenticado: " + str(e.returncode) + " en puerto " + port + "\n")
    else:
        try:
            basedn = getBaseDN()
            results = subprocess.check_output(['ldapsearch','-h',ip_address,'-p',args.port,'-x','-b',basedn],encoding='utf8')
            if results:
                for res in results:
                    f.write(res)
        except subprocess.CalledProcessError as e:
            print("Código de error en ldapsearch no autenticado: " + str(e.returncode) + " en puerto " + args.port + "\n")

    if args.username and args.password and args.domain:
        try:
            print("Intentando búsqueda autenticada con ldapsearch")
            basedn = getBaseDN()
            short_domain = (args.domain).split('.')[0]         
            results = subprocess.check_output(['ldapsearch','-h',ip_address,'-b',basedn,'-x','-D','%s@%s' % (args.username,short_domain),'-w',args.password],encoding='utf8')
            if results:
                for res in results:
                    f.write(res)
            print("Búsqueda autenticada con ldapsearch completada")
        except subprocess.CalledProcessError as e:
            print("Código de error en ldapsearch autenticado: " + str(e.returncode) + "\n")
    f.close()
    print("INFO: ldapsearch completado en %s:%s" % (ip_address, args.port))

def getBaseDN():
    # Obtener el basedn desde nmap
    GREP_COMMAND = "grep namingContexts %s.nmap  | cut -d' ' -f9" % (outfileNmap)
    try:
        basedn = subprocess.check_output(GREP_COMMAND,encoding='utf8',shell=True)
        if "\n" in basedn:
            basedn = basedn.split('\n')[0]
        return basedn
    except subprocess.CalledProcessError as e:
        print("Código de error en obtención de baseDN: " + str(e.returncode) + "\n")

def cleanHistory():
    print("Limpiando archivos de historial")
    bash_history = "/root/.bash_history"
    zsh_history = "/root/.zsh_history"
    if os.path.isfile(bash_history):
        os.remove(bash_history)
    if os.path.isfile(zsh_history):
        os.remove(zsh_history)


if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar la enumeración de LDAP. Uso: ldaprecon.py {-u username -p password -d FQDN} IP {port}')
    parser.add_argument('-u', '--username', default = "", help="Nombre de usuario para conectar. Anónimo si no se especifica. Usar formato Dominio\\\\Usuario")
    parser.add_argument('-p', '--password', nargs='?', default = "", help="Contraseña de autenticación. Anónimo si no se especifica. Solicita interactivamente si solo se pasa -p")
    parser.add_argument('-d', '--domain', default = "", help="FQDN del dominio")
    parser.add_argument('ip', help="Dirección IP del objetivo")
    parser.add_argument('--port', default='389,636', dest='port', help="Puerto. Por defecto 389,636")
    parser.add_argument('--not-safe', dest='not_safe', default=False, action='store_const', const=True, help="Deshabilitar la eliminación de archivos de historial de bash/zsh")

    args = parser.parse_args()

    ip_address = args.ip
    port = args.port

    if args.username != "":
        args.password = getpass.getpass('Contraseña: ')

    BASE = "/root/scripts/recon_enum/results/exam/ldap"
    mkdir_p(BASE)
    outfile = "%s/%s_%s_ldaprecon.txt" % (BASE, ip_address, port)
    outfileNmap = "%s/%s_%s_ldapnmap" % (BASE, ip_address, port)
    outfileLdapSearch = "%s/%s_%s_ldapsearch" % (BASE, ip_address, port)

    doNmap()
    if args.domain != "":
        doADLdapEnum()
    doLdapDD()
    doLdapSearch()
    if not args.not_safe:
        cleanHistory()
    print("INFO: ldaprecon completado en %s:%s" % (ip_address, port))
    print("Recuerda que PowerView y otras herramientas más avanzadas pueden emplearse disponiendo de credenciales")
