#!/usr/bin/env python
import subprocess
import sys
import os
import pathlib
import argparse
import socket
import shutil

# RPCDump es un script de Impacket. Requiere tener instalado python3-impacket mediante setup.py

# Parche para forzar que ifmap continúe ante errores de tiempo de espera (timeout) en vez de lanzar excepciones
def patch_ifmap():
    # línea 329: dce.connect()
    ifmap = '/usr/local/lib/python3.7/dist-packages/impacket-0.9.21.dev1+20200313.160519.0056b61c-py3.7.egg/EGG-INFO/scripts/ifmap.py'
    tmpmap = '/tmp/ifmap.py'
    sha256sum = 'ca54b5a010df84ef57e39143cb14d86343574ed22efb44b9c40b8a12c9558b4c' # archivo original
    sha256sum_patched = '883d9d9085d67b010eb3ff63699a678101db95e597373b99029ca6d6be5c18ac' # parchado
    if os.path.isfile(ifmap):
        sha_check = subprocess.run(['sha256sum',ifmap],check=True,stdout=subprocess.PIPE,encoding='utf8').stdout
        sha_check = sha_check.split(' ')[0]
        if sha_check == sha256sum_patched:
            return
        shutil.copy(ifmap,"%s.bak" % ifmap)
        sha_check = subprocess.run(['sha256sum',ifmap],check=True,stdout=subprocess.PIPE,encoding='utf8').stdout
        sha_check = sha_check.split(' ')[0]
        if sha_check == sha256sum:
            print("Aplicando parche a ifmap")
            try:
                f = open(ifmap, 'r')
                g = open(tmpmap,'w+')
                for line in f:
                    if line == "    dce.connect()\n":
                        continue
                    elif line == "  for tup in sorted(probes):\n":
                        g.write(
"""  for tup in sorted(probes):
    try:
      dce.connect()
    except:
      continue""")
                    else:
                        g.write(line)
                f.close()
                g.close()
                shutil.move(tmpmap, ifmap)
            except:
                print("No fue posible parchar ifmap correctamente.")
                shutil.move("%s.bak" % ifmap, ifmap)
        else:
            print("El hash SHA de ifmap no coincide con el original ni con el parchado, se omite el parche")

# Documentación de Scripts NSE
# En ejecución:
# msrpc-enum: consulta al endpoint mapper de MSRPC para obtener una lista de servicios mapeados
def doNmap():
    print("INFO: Realizando escaneo de scripts MSRPC con nmap para %s:%s" % (ip_address, port))
    subprocess.check_output(['nmap','-n','-sV','-Pn','-vv','-p',port,'--script','msrpc-enum,vulners','-oA','/root/scripts/recon_enum/results/exam/msrpc/%s_%s_msrpc.nmap' % (ip_address,port),ip_address],encoding='utf8')

# Para interfaces a la escucha en msrpc, ejecutar ifmap
def doIFMap():
    print("Iniciando ifmap")
    if os.path.isfile("/usr/local/bin/ifmap.py"):
        DEVNULL = open(os.devnull, 'w')
        ifmap_tmp = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_ifmap_tmp.txt" % (ip_address, port)
        ifmap_outfile = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_ifmap.txt" % (ip_address, port)
        ifmap_results_array = []
        try:
            ifmap_tmp_handle = open(ifmap_tmp,'w')
            subprocess.run(['ifmap.py',ip_address,port],encoding='utf8',stdout=ifmap_tmp_handle,stderr=DEVNULL)
            ifmap_tmp_handle.close()
            DEVNULL.close()
            rawUUIDs = []
            f = open(ifmap_outfile, "w")
            g = open(ifmap_tmp, "r")
            for line in g:
                if ("UUID" in line):
                    if ("other version listed" in line):
                        rawUUIDs.append(line[11:-33])
                    elif ("not listed" in line):
                        rawUUIDs.append(line[11:-23])
                    elif ("listed, listening" in line):
                        rawUUIDs.append(line[11:-19])
                f.write(line)
            f.close()
            g.close()

            with open(ifmap_tmp,'r') as f:
                ifmap_results_array = f.read().splitlines()

            os.remove(ifmap_tmp)
            try:
                print("Iniciando opdump")
                doOpdump(rawUUIDs,ifmap_results_array)
            except:
                print("¡Falló opdump!")
        except:
            print("Ocurrió un error con ifmap en %s:%s, ejecutar manualmente" % (ip_address, port))
    else:
        print("No se encontró ifmap, debe ejecutarse manualmente")

# Procesa los resultados a la escucha desde ifmap y obtiene mayor detalle con opdump
def doOpdump(rawUUIDs,ifmap_results_array):
    access_denied=[]
    success=[]
    try:
        DEVNULL = open(os.devnull, 'w')
        timeout_outfile = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_opdump_timeout.txt" % (ip_address, port)
        t = open(timeout_outfile,'w')
        for UUID in rawUUIDs:
            scanme=UUID.split(" v")
            try:
                results = subprocess.check_output(['opdump.py',ip_address,port,scanme[0],scanme[1]],encoding='utf8',stderr=DEVNULL)
            except subprocess.CalledProcessError:
                t.write("opdump con UUID: " + scanme[0] + " v" + scanme[1] + " resultó en tiempo de espera agotado (timeout).\n")
                continue
            except Exception as e:
                print(type(e))
                print("Excepción no controlada en ifmap: doOpdump")
                print("opdump con UUID: " + scanme[0] + " v" + scanme[1] + " agotó el tiempo de espera.")
                continue
            if ("rpc_s_access_denied" in results):
                access_denied.append(scanme[0] + " " + scanme[1])
                access_denied.append(results)
            else:
                success.append(scanme[0] + " " + scanme[1])
                success.append(results)
        DEVNULL.close()
        denied_outfile = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_opdump_denied.txt" % (ip_address, port)
        f = open(denied_outfile, "w")
        for denied in access_denied:
            f.write(denied)
            f.write("\n")
        f.close()
        analyzeOpdump(success,ifmap_results_array)
    except NameError:
        print("No es posible ejecutar opdump sin ifmap")

def analyzeOpdump(successArray,ifmap_results):
    print("Analizando opdump")
    # Para resultados exitosos con opdump, correlaciona el UUID con información referencial
    success_outfile = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_opdump_success.txt" % (ip_address, port)
    f = open(success_outfile, "w")
    if successArray is not None:
        for good in successArray:
            tmp_uuid=good[:-4]
            if ":" not in good:
                for ifmap in ifmap_results:
                    if str(tmp_uuid) in ifmap:
                        tmp_uuid_index = ifmap_results.index(ifmap)
                        tmp_protocol_index = tmp_uuid_index - 2
                        uuid=ifmap_results[tmp_uuid_index]
                        if ("other version listed" in uuid):
                            f.write(uuid[11:-33])
                        elif ("not listed" in uuid):
                            f.write(uuid[11:-23])
                        elif ("listed, listening" in uuid):
                            f.write(uuid[11:-19])
                        f.write(" | ")
                        f.write(ifmap_results[tmp_protocol_index])
                        f.write(good)
                        f.write("\n")
                        break
            else:
                f.write(good)
                f.write("\n")
        f.close()
    else:
        print("No es posible analizar opdump en tuberías exitosas")

def doRPCDump():
    if os.path.isfile('/usr/bin/impacket-rpcdump'):
        print("Iniciando rpcdump")
        # Información complementaria sin autenticación (soporta hash para SMB)
        rpcdump_outfile = "/root/scripts/recon_enum/results/exam/msrpc/%s_%s_rpcdump.txt" % (ip_address, port)
        results = subprocess.check_output(['impacket-rpcdump',ip_address,'-port',port],encoding='utf8')
        f = open(rpcdump_outfile, "w")
        for res in results:
            f.write(res)
        f.close()

        print("Este RPCDump NO es autenticado, debe ejecutarse manualmente para autenticación")
    else:
        print("No se encontró impacket-rpcdump, debe ejecutarse manualmente")

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para verificar endpoints MSRPC y tuberías (pipes) disponibles. Uso: msrpcrecon.py <dirección_ip> <puerto>')
    parser.add_argument('ip_address', help="Dirección IP de la máquina Windows objetivo")
    parser.add_argument('port', help="Puerto específico a enumerar")
    args = parser.parse_args()

    ip_address = args.ip_address
    port = args.port

    BASE = "/root/scripts/recon_enum/results/exam/msrpc"
    mkdir_p(BASE)

    print("\nINFO: Iniciando MSRPCrecon")
    patch_ifmap()
    doNmap()
    doIFMap() # IFMap llamará a doOpdump y doOpdump llamará a analyzeOpdump
    doRPCDump()
    print("\nINFO: MSRPCrecon completado")
