#!/usr/bin/python

import sys
import os
import subprocess
import errno
import multiprocessing
from multiprocessing import Process
import time
import argparse
import pathlib
from urllib.parse import urlparse

# Función mkdir_p actualizada para Python >= 3.5
def mkdir_p(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

# Función CEWL para rastreo y generación de diccionario contextual
def cewl(depth,urlOrFile,scanname):
    # -c: contar repeticiones de cada palabra
    # -d: profundidad de rastreo (por defecto 2)
    # -k: conservar archivos descargados
    # -a: considerar metadatos (descargados en /tmp)
    # -m: longitud mínima de palabra
    # -n: no imprimir wordlist por salida estándar
    # -o: visitar sitios externos si se especifica
    # -u: User-Agent
    # -w: escribir salida a archivo
    print("INFO: Iniciando escaneo cewl con %s para %s" % (args.tool, url))
    dev_null = open(os.devnull, 'w')
    if os.path.isfile(urlOrFile): # si se pasa un archivo con fragmentos
        f = open(scanname,'w')
        g = open(urlOrFile,'r')
        for line in g:
            line = line.split(" ")[0]
            if line[-1] == "\n":
                line = line[:-1]
            try:
                results = subprocess.check_output(['cewl','-d %d' % depth,'-k','-a','-m 5','-u',user_agent,line],encoding='utf8',stderr=dev_null)
            except Exception as e:
                print(type(e))
                print("Error desconocido en cewl en dirbustEVERYTHING")
            f.write(results)
        f.close()
        g.close()
    else: # escaneo sobre una sola URL
        try:
            results = subprocess.check_output(['cewl','-d %d' % depth,'-k','-a','-m 5','-u',user_agent,urlOrFile,'-w',scanname],encoding='utf8',stderr=dev_null)
        except Exception as e:
                print(type(e))
    print("INFO: Finalizado escaneo cewl con %s para %s" % (args.tool, url))

def genlistLoopProc(tool_default_list):
    if getStatus200(tool_default_list):
        jobs = []
        count = 0
        if (os.path.getsize(STAT_200) != 0):
            tmp = "stat200_%s_%s_chunk" % (name, port)
            chunkWordlistGeneric(BASE,STAT_200,tmp,PROCESSES)
            for chunk in os.listdir(BASE):
                if tmp in chunk:
                    path = "%s/%s" % (BASE,chunk)
                    if os.path.getsize(path) > 0:
                        scanname = "%s_results_chunk_%s" % (CEWL_OUT, str(count))
                        p = multiprocessing.Process(target=cewl, args=(2,path,scanname))
                        p.start()
                        jobs.append(p)
                        count += 1
            for p in jobs:
                p.join()
            tmp = "cewl_%s_%s_results_chunk_" % (name,port)
            comuni(tmp,CEWL_OUT)
            for resChunk in os.listdir(BASE):
                if os.path.isfile("%s/%s" % (BASE,resChunk)):
                    resultFile = "%s_%s_results_chunk_" % (name, port)
                    if resultFile in resChunk:
                        resChunk = "%s/%s" % (BASE,resChunk)
                        os.remove(resChunk)
                    statFile = "stat200_%s_%s_chunk" % (name, port)
                    if statFile in resChunk:
                        resChunk = "%s/%s" % (BASE,resChunk)
                        os.remove(resChunk)
        else: # si no hay páginas con estado 200, rastrear la página principal
            cewl(5,url,CEWL_OUT)
    else:
        return

def genlistLoop(tool_default_list):
    print("INFO: Generando lista de palabras personalizada")
    getStatus200(tool_default_list)
    g = open(STAT_200, 'r')
    cewldWords = set()
    dev_null = open(os.devnull, 'w')
    if (os.path.getsize(STAT_200) != 0):
        for line in g:
            line = line.split(" ")[0]
            results = subprocess.check_output(['cewl','-d 2','-k','-a','-m 5','-u %s' % user_agent,line],encoding='utf8',stderr=dev_null)
            for res in results:
                cewldWords.add(res)
    else:
        results = subprocess.check_output(['cewl','-d 5','-k','-a','-m 5','-u %s' % user_agent,url],encoding='utf8',stderr=dev_null)
        for res in results:
            cewldWords.add(res)
    dev_null.close()
    g.close()
    g = open(CEWL_OUT, 'w')
    for word in cewldWords:
        g.write(word)
    g.close()

# Tras la primera ejecución de gobuster/dirb, filtra las URLs con estado 200 para CEWL
def getStatus200(tool_default_list):
    g = open(tool_default_list, 'r')
    status200=[]
    tmp = "/tmp/stat200"
    if args.tool == "gobuster" or args.tool == "dirb":
        for line in g:
            if ("(Status: 200)" in line) or ("(CODE:200" in line):
                status200.append(line)
        g.close()
        if len(status200) > 0:
            g = open(STAT_200, 'w')
            for line in status200:
                g.write(line)
            g.close()
            UNIQ="cat %s | sort | uniq > %s" % (STAT_200, tmp)
            subprocess.check_call(UNIQ, shell=True)
            MOVE="mv %s %s" % (tmp, STAT_200)
            subprocess.check_call(MOVE, shell=True)
            return True
        else:
            print("INFO: No se detectaron páginas accesibles (sin respuestas con estado 200) para %s:%s" % (ip_address, port))
            return False
    g.close()
    if args.tool == "wfuzz":
        transformWfuzzOutput(tool_default_list, STAT_200)
        if os.path.getsize(STAT_200) != 0:
            return True
        else:
            return False

def transformWfuzzOutput(file1, file2):
    f = open(file1, 'r')
    g = open(file2, 'w')
    for line in f:
        if "C=200" in line:
            tmpLineCount = set(line.split("C=200")[1].split("\t")[0])
            for i in range(0, len(tmpLineCount), 1):
                pop = tmpLineCount.pop()
                if pop == "" or pop == " " or pop == "L":
                    continue
                else:
                    lineCount = pop
                    break
            directory = line.split('"')[-2]
            g.write(url + "/" + directory + " (Status: 200) [Size: " + lineCount + "]\n")
    f.close()
    g.close()

def dirb(wordlist, scanname):
    # Opciones de Dirb:
    # -a: User-Agent personalizado
    # -b: no contraer secuencias de /../ o /./
    # -f: ajuste de detección 404
    # -S: modo silencioso
    if (wordlist == ""):
        cwd = os.getcwd()
        os.chdir(LISTS)
        files = os.listdir(LISTS)
        f = open(scanname, 'a')
        for file in files:
            results = subprocess.check_output(['dirb',url,file,'-a',user_agent,'-b','-f','-S'],encoding='utf8')
            try:
                itter = results.split("\n")
                for line in itter:
                    if ( str("+") in line ) or ( str("(!)") in line):
                        f.write(line)
            except:
                pass
        os.chdir(cwd)
        f.close()
    else:
        f = open(scanname, 'w')
        results = subprocess.check_output(['dirb',url,wordlist,'-a',user_agent,'-b','-f','-S'],encoding='utf8')
        try:
            itter = results.split("\n")
            for line in itter:
                if ( str("+") in line ) or ( str("(!)") in line):
                        f.write(line)
        except:
            pass
        f.close()

# Opciones de wfuzz:
# -v: salida detallada
# -t N: concurrencia de conexiones
# -L: seguir redirecciones HTTP
# -u: URL objetivo
# -w: lista de palabras
def wfuzz(wordlist, scanname):
    results = subprocess.check_output(['wfuzz','-v','-t',threads,'-L','--hc','404','-w',wordlist,'-u',url,'-f',scanname],encoding='utf8')
    return results

def gobuster(wordlist, scanname):
    # Opciones de Gobuster:
    # -a: cadena de User-Agent
    # -e: modo expandido (URLs completas)
    # -l: incluir tamaño de respuesta en la salida
    # -q: modo silencioso
    # -r: seguir redirecciones
    # -s: códigos de estado aceptados (por defecto 200,204,301,302,307)
    # -t: hilos concurrentes
    # -x: extensiones de archivo a buscar
    # -k: omitir verificación de certificado SSL
    results = subprocess.check_output(['gobuster','dir','-a',user_agent,'-t',threads,'-e','-q','-r','-s',dirStatusCodes,'-u',url,'-x',FILE_EXT,'-l','-w',wordlist,'-o',scanname,'-k'],encoding='utf8')
    if "Wildcard response found" in results:
        print("Se detectó una respuesta de comodín (wildcard), reiniciando...")
        results = subprocess.check_output(['gobuster','dir','-a',user_agent,'-t',threads,'-e','-q','-r','-s',dirStatusCodes,'-u',url,'-x',FILE_EXT,'-l','-w',wordlist,'--wildcard','-o',scanname],encoding='utf8')
    if "Invalid certificate" in results:
        print("Se detectó un certificado inválido, reiniciando...")
        results = subprocess.check_output(['gobuster','dir','-a',user_agent,'-t',threads,'-e','-q','-r','-s',dirStatusCodes,'-u',url,'-x',FILE_EXT,'-l','-w',wordlist,'-o',scanname,'-k'],encoding='utf8')
    if "Unable to connect:" in results:
        print("Gobuster no pudo conectar")
        f = open(scanname,'w')
        f.write(results)
        f.close()

def sortBySize(nameAndPathOfResults):
    f = open(nameAndPathOfResults, 'r')
    sizear = set()
    for line in f:
        if "Size:" in line:
            tmpsize = line.split('[Size: ')[1]
            if ("\n" in tmpsize):
                tmpsize = tmpsize[:-2]
            else:
                tmpsize = tmpsize[:-1]
            sizear.add(tmpsize)
    for size in sizear:
        GREP = "grep %s %s > %s/gobuster_%s_%s_size_%s_only" % (size, nameAndPathOfResults, BASE, name, port, size)
        GREPRESULTS = subprocess.call(GREP, shell=True)
    f.close()

def cleanup():
    directory = "%s/%s" % (BASE,name)
    for resultFile in os.listdir(BASE):
        if not os.path.isdir(directory):
            mkdir_p(directory)
        if os.path.isdir("%s/%s" % (BASE,resultFile)):
            continue
        if name in resultFile:
            destination = "%s/%s" % (directory,resultFile)
            resultFile = "%s/%s" % (BASE,resultFile)
            os.rename(resultFile,destination)

def whatWeb(path):
    print("INFO: Iniciando whatweb en %s" % (url))
    if os.path.getsize(path) == 0:
        print("ERROR: %s no fue generado" % (path))
        return
    else:
        dev_null = open(os.devnull, 'w')
        f = open(path)
        g = open(WW_URLS,'w')
        for line in f:
            line = line.split(" ")[0]
            if "(" in line or ")" in line or line == "" or "Unable to connect:" in line or not "." in line:
                pass
            else:
                g.write(line + "\n")
        g.close()
        if os.path.getsize(WW_URLS) > 0:
            results = subprocess.check_output(['whatweb','-i',WW_URLS,'-u',user_agent,'-a 3','-v','--log-xml',WW_OUT],encoding='utf8',stderr=dev_null)
            f = open(WW_OUT_VERBOSE,'w')
            for res in results:
                f.write(res)
            f.close()
            dev_null.close()
        else:
            print("No hay URLs para analizar con whatweb en %s:%s" % (ip_address,port))
    print("INFO: Identificación con WhatWeb en %s completada" % (url))

def chunkWordlistGeneric(dirToStoreChunks, absPathFileToChunk, chunkFileNames, numChunks):
    if not os.path.exists(dirToStoreChunks):
        mkdir_p(dirToStoreChunks)
    proceed = True
    for thing in os.listdir(dirToStoreChunks):
        if chunkFileNames in thing:
            proceed = False
            break
    if os.path.exists(dirToStoreChunks) and proceed:
        f = open(absPathFileToChunk, 'r')
        chunkCount = 0
        chunkFileCount = 0
        chunkFile = "%s/%s_%s" % (dirToStoreChunks,chunkFileNames,str(chunkFileCount))
        origSize = subprocess.check_output(['wc', '-l', absPathFileToChunk],encoding='utf8').split(" ")[0]
        g = open(chunkFile, 'w')
        for line in f:
            g.write(line)
            if chunkCount >= (int(origSize)/numChunks):
                g.close()
                chunkFileCount += 1
                chunkFile = "%s/%s_%s" % (dirToStoreChunks,chunkFileNames,str(chunkFileCount))
                chunkCount = 0
                g = open(chunkFile, 'w')
            chunkCount += 1
        f.close()
        g.close()

def comuni(tool,combined_name):
    COMUNI = "awk \'!a[$0]++\' %s/%s* > %s" % (BASE, tool, combined_name)
    comuniresults = subprocess.check_call(COMUNI, shell=True)

def parameth(STAT_200_URLS,scanname):
    print("INFO: Iniciando parameth en %s" % (url))
    tmpScanname = "/tmp/%s_%s_%s_%s_paramethtmp" % (args.tool, ip_address, port, args.intensity)
    f = open(STAT_200_URLS, 'r')
    g = open(scanname, "w+")
    paramethRunCount = 0
    urlSet = set()
    for url200 in f:
        urlOnly = url200.split(" ")[0]
        if "?" in urlOnly:
            urlOnly = urlOnly.split("?")[0]
        urlSet.add(urlOnly)
    for uniqURL in urlSet:
        if paramethRunCount == 0:
            results = subprocess.check_output(['/root/Documents/Parameth/./parameth.py','-u',url,'-p',args.parameth_wordlist,'-a',user_agent,'-t',threads],encoding='utf8').split("\n")
            paramethRunCount += 1
        if paramethRunCount > 0:
            results = subprocess.check_output(['/root/Documents/Parameth/./parameth.py','-u',uniqURL,'-p',args.parameth_wordlist,'-a',user_agent,'-t',threads],encoding='utf8').split("\n")
        for res in results:
            if "->" and "http" in res:
                g.write(res)
                g.write("\n")
            else:
                continue
    f.close()
    g.close()
    os.rename(scanname, tmpScanname)
    GREPV_AUTHOR = "cat %s | grep -iv 'Author' > %s" % (tmpScanname, scanname)
    subprocess.call(GREPV_AUTHOR, shell=True)
    print("INFO: Parameth completado en %s" % (url))

# Configuración de extensiones a evaluar según intensidad
def getFileExtensionsForIntensity(intensity_value):
    if intensity_value in [2,3,6,7,10,11]:
        if args.FILE_EXT != ".php":
            FILE_EXT=".html,.txt,.php"+args.FILE_EXT
        else:
            FILE_EXT=".html,.txt,.php"
    elif intensity_value in [4,8,12]:
        FILE_EXT=".php,.html,.cgi,.txt,.bak,.old,.asp,.aspx,.git"
    else:
        if args.FILE_EXT == "":
            FILE_EXT=".html"
        else:
            FILE_EXT=args.FILE_EXT
    return FILE_EXT

def getDefaultWordlistForIntensity(intensity_value):
    if intensity_value in [1,2,3,4]:
        default_wordlist = "/root/lists/Web/secProb_no_ext.txt"
    elif intensity_value in [5,6,7,8]:
        default_wordlist = "/root/lists/Web/personal_with_vulns_no_ext.txt"
    else:
        default_wordlist = args.default_wordlist
    return default_wordlist

def check_intensity():
    intensity = args.intensity
    if int(intensity) >= 13 or int(intensity) <= 0:
        raise argparse.ArgumentTypeError("La intensidad debe estar comprendida entre 1 y 12")
    else:
        args.intensity = int(args.intensity)

def check_processes():
    args.PROCESSES = int(args.PROCESSES)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Script para gestionar fuerza bruta de directorios y parámetros web. Uso: dirbust.py {-t [gobuster|dirb] -x ".html" -a <UA> -w <wordlist> -p <#> -i <#>} <http(s)://IP_objetivo:puerto>')
    parser.add_argument('-t', '--tool', default="gobuster", choices=["gobuster", "dirb", "wfuzz"], help="Herramienta a utilizar: gobuster, dirb o wfuzz (por defecto: gobuster)")
    parser.add_argument('-m', '--more-threads', dest="more_threads", default='10', help="Hilos a pasar a las herramientas")
    parser.add_argument('-x', '--extensions', dest="FILE_EXT", default=".html", help="Extensiones a comprobar separadas por coma (ej. .php,.html)")
    parser.add_argument('-a', '--user-agent', dest="user_agent", default="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1", help="Cadena User-Agent")
    parser.add_argument('-w', '--wordlist', dest="default_wordlist", default="/root/lists/Web/secProb_no_ext.txt", help="Lista de palabras para directorios")
    parser.add_argument('-q', '--pwordlist', dest="parameth_wordlist", default="/root/lists/Web/all_url_params.txt", help="Lista de palabras para parámetros")
    parser.add_argument('-p', '--processes', dest="PROCESSES", default='10', help="Número de fragmentos para dividir la lista de palabras")
    parser.add_argument('-i', '--intensity', default="3", dest='intensity', help="Nivel de intensidad de escaneo (1 al 12).")
    parser.add_argument('url', help="URL objetivo con formato http(s)://IP:PUERTO")
    args = parser.parse_args()

    check_intensity()
    check_processes()

    parsed_url = urlparse(args.url)

    if not parsed_url.port:
        if parsed_url.scheme == 'http':
            port = '80'
            print("INFO: [dirbustEVERYTHING] no se indicó puerto, http asigna puerto 80 por defecto")
        elif parsed_url.scheme == 'https':
            port = '443'
            print("INFO: [dirbustEVERYTHING] no se indicó puerto, https asigna puerto 443 por defecto")
        else:
            print("ERROR: [dirbustEVERYTHING] esquema desconocido")
            sys.exit(1)
    else:
        port = parsed_url.port

    if ":" in parsed_url.scheme:
        ip_address = parsed_url.scheme.split(':')[0]
    else:
        ip_address = parsed_url.scheme

    name = "%s_i%s" % (ip_address, args.intensity)
    user_agent = args.user_agent
    userAgent = args.user_agent
    threads = args.more_threads
    PROCESSES = args.PROCESSES

    dirStatusCodes = '200,204,301,302,307,403'
    FILE_EXT = getFileExtensionsForIntensity(args.intensity)
    default_wordlist = getDefaultWordlistForIntensity(args.intensity)

    wordlistLastItem=args.default_wordlist.split("/")[len(args.default_wordlist.split("/"))-1]
    if len(wordlistLastItem.split(".")) == 1:
        WORDLIST_CHUNK_DIR="/root/lists/Web/%sChunked" % wordlistLastItem
    else:
        wordlistLastItem = wordlistLastItem.split(".")[0]
        WORDLIST_CHUNK_DIR="/root/lists/Web/%sChunked" % wordlistLastItem

    BASE="/root/scripts/recon_enum/results/exam/dirb/%s" % (port)
    LISTS="/root/lists/Web/AllWebLists/separate"
    CEWL_OUT="%s/cewl_%s_%s" % (BASE, name, port)
    STAT_200="%s/stat200_%s_%s" % (BASE, name, port)
    GOB_DEFAULT="%s/gobuster_%s_%s_default" % (BASE, name, port)
    GOB_CEWL_OUTPUT="%s/gobuster_%s_%s_cewld" % (BASE, name, port)
    GOB_COMBINED="%s/gobuster_%s_%s_combined" % (BASE, name, port)
    GOB_PARAMETH="%s/gobuster_%s_%s_parameth" % (BASE, name, port)
    DIRB_DEFAULT="%s/dirb_%s_%s_default" % (BASE, name, port)
    DIRB_CEWL_OUTPUT="%s/dirb_%s_%s_cewld" % (BASE, name, port)
    DIRB_COMBINED="%s/dirb_%s_%s_combined" % (BASE, name, port)
    DIRB_PARAMETH="%s/dirb_%s_%s_parameth" % (BASE, name, port)
    WFUZZ_DEFAULT="%s/wfuzz_%s_%s_default" % (BASE, name, port)
    WFUZZ_CEWL_OUTPUT="%s/wfuzz_%s_%s_cewld" % (BASE, name, port)
    WFUZZ_COMBINED="%s/wfuzz_%s_%s_combined" % (BASE, name, port)
    WFUZZ_COMBINED_TMP="/tmp/wfuzz_%s_%s_combined_tmp" % (name, port)
    WFUZZ_PARAMETH="%s/wfuzz_%s_%s_parameth" % (BASE, name, port)
    WW_URLS="/root/scripts/recon_enum/results/exam/whatweb/%s_%s_whatwebURLs" % (name, port)
    WW_OUT="/root/scripts/recon_enum/results/exam/whatweb/%s_%s_whatweb.xml" % (name, port)
    WW_OUT_VERBOSE="/root/scripts/recon_enum/results/exam/whatweb/%s_%s_whatweb_verbose" % (name, port)

    if (args.tool == "dirb"):
        print("INFO: Iniciando escaneo dirb para %s:%s" % (url, port))
        dirb(default_wordlist, DIRB_DEFAULT)
        print("INFO: Finalizado escaneo inicial de dirb para %s:%s" % (url, port))
        if args.intensity in [3,4,7,8,11,12]:
            genlistLoop(DIRB_DEFAULT)
            dirb(CEWL_OUT, DIRB_CEWL_OUTPUT)
            comuni("dirb",DIRB_COMBINED)
            sortBySize(DIRB_COMBINED)
            print("INFO: Fuerza bruta de directorios en %s completada" % (url))
            whatWeb(DIRB_COMBINED)
            print("INFO: Iniciado escaneo nmapHttpVulns en %s:%s" % (ip_address, port))
            subprocess.check_output(['./nmapHttpVulns.py',STAT_200,url],encoding='utf8')
            print("INFO: nmapHttpVulns en %s completado" % (url))
            parameth(DIRB_COMBINED, DIRB_PARAMETH)
            cleanup()
        else:
            comuni("dirb",DIRB_COMBINED)
            sortBySize(DIRB_COMBINED)
            cleanup()
            print("INFO: Dirb completado en %s" % (url))

    if (args.tool == "gobuster"):
        print("INFO: Iniciando escaneo gobuster para %s:%s" % (url, port))
        chunkWordlistGeneric(WORDLIST_CHUNK_DIR,default_wordlist,wordlistLastItem,PROCESSES)
        count = 0
        jobs = []
        for chunk in os.listdir(WORDLIST_CHUNK_DIR):
            path = "%s/%s" % (WORDLIST_CHUNK_DIR,chunk)
            if os.path.getsize(path) > 0:
                scanname = "%s_%s_%s_default_chunk_%s" % (GOB_DEFAULT, name, port, str(count))
                p = multiprocessing.Process(target=gobuster, args=(path,scanname))
                p.start()
                jobs.append(p)
                count += 1
        for p in jobs:
            p.join()
        scanChunkNames = "gobuster_%s_%s_default_%s_%s_default_chunk_" % (name, port, name, port)
        comuni(scanChunkNames,GOB_DEFAULT)
        for resChunk in os.listdir(BASE):
            if os.path.isfile("%s/%s" % (BASE,resChunk)):
                tmp = "_default_%s_%s_default_chunk" % (name, port)
                if tmp in resChunk:
                    resChunk = "%s/%s" % (BASE,resChunk)
                    os.remove(resChunk)
        if args.intensity in [3,4,7,8,11,12]:
            genlistLoopProc(GOB_DEFAULT)
            gobuster(CEWL_OUT, GOB_CEWL_OUTPUT)
            comuni("gobuster",GOB_COMBINED)
            print("INFO: Fuerza bruta de directorios en %s completada" % (url))
            sortBySize(GOB_COMBINED)
            whatWeb(GOB_COMBINED)
            print("INFO: Iniciado escaneo nmapHttpVulns en %s:%s" % (ip_address, port))
            subprocess.check_output(['/root/scripts/recon_enum/./nmapHttpVulns.py',STAT_200,url],encoding='utf8')
            print("INFO: nmapHttpVulns en %s completado" % (url))
            parameth(GOB_COMBINED, GOB_PARAMETH)
            cleanup()
        else:
            comuni("gobuster",GOB_COMBINED)
            sortBySize(GOB_COMBINED)
            cleanup()
            print("INFO: Gobuster completado en %s" % (url))

    if (args.tool == "wfuzz"):
        print("INFO: Iniciando escaneo wfuzz para %s:%s" % (url, port))
        if url[-1] != "/":
            url = url + "/"
        url = url + "FUZZ"
        chunkWordlistGeneric(WORDLIST_CHUNK_DIR,default_wordlist,wordlistLastItem,PROCESSES)
        count = 0
        jobs = []
        for chunk in os.listdir(WORDLIST_CHUNK_DIR):
            path = "%s/%s" % (WORDLIST_CHUNK_DIR,chunk)
            if os.path.getsize(path) > 0:
                scanname = "%s_%s_%s_default_chunk_%s" % (WFUZZ_DEFAULT, name, port, str(count))
                p = multiprocessing.Process(target=wfuzz, args=(path,scanname))
                p.start()
                jobs.append(p)
                count += 1
        for p in jobs:
            p.join()
        scanChunkNames = "wfuzz_%s_%s_default_%s_%s_default_chunk_" % (name, port, name, port)
        comuni(scanChunkNames,WFUZZ_DEFAULT)
        for resChunk in os.listdir(BASE):
            if os.path.isfile("%s/%s" % (BASE,resChunk)):
                tmp = "_default_%s_%s_default_chunk" % (name, port)
                if tmp in resChunk:
                    resChunk = "%s/%s" % (BASE,resChunk)
                    os.remove(resChunk)
        if args.intensity in [3,4,7,8,11,12]:
            url = url[:-5]
            genlistLoopProc(WFUZZ_DEFAULT)
            wfuzz(CEWL_OUT, WFUZZ_CEWL_OUTPUT)
            comuni("wfuzz",WFUZZ_COMBINED)
            os.rename(WFUZZ_COMBINED, WFUZZ_COMBINED_TMP)
            transformWfuzzOutput(WFUZZ_COMBINED_TMP, WFUZZ_COMBINED)
            print("INFO: Fuerza bruta de directorios en %s completada" % (url))
            sortBySize(WFUZZ_COMBINED)
            whatWeb(WFUZZ_COMBINED)
            print("INFO: Iniciado escaneo nmapHttpVulns en %s:%s" % (url, port))
            subprocess.check_output(['./nmapHttpVulns.py',STAT_200,url],encoding='utf8')
            print("INFO: nmapHttpVulns en %s completado" % (url))
            parameth(WFUZZ_COMBINED, WFUZZ_PARAMETH)
            cleanup()
        else:
            comuni("wfuzz",WFUZZ_COMBINED)
            sortBySize(WFUZZ_COMBINED)
            cleanup()
            print("INFO: Wfuzz completado en %s" % (url))
