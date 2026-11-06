#!/usr/bin/env python

import subprocess
import multiprocessing
from multiprocessing import Process, Queue
import os
import time

def lbd(domain):
   domain = domain.strip()
   print("INFO: Ejecutando escaneos generales de ldb para " + domain)
   # lbdSCAN = "lbd %s"  % (domain)
   # results = subprocess.check_output(lbdSCAN, shell=True)
   # lines = results.split("\n")
   lines = subprocess.check_output(['ldb',domain],encoding='utf8').split("\n")
   for line in lines:
      line = line.strip()
      if ("Load-balancing" in line) and not ("NOT" in line):
         print (line)
      if ("does NOT use Load-balancing" in line):
         print (line)
      else:
         return
   return

if __name__=='__main__':
   f = open('/root/scripts/recon_enum/results/exam/targets.txt', 'r') # ¡MODIFICAR ESTO! Tomar los hosts activos del escaneo de descubrimiento para enumerar
					     # Verificar también el User-Agent de Nmap, se recomienda configurarlo como Firefox
   for domain in f:
       jobs = []
       p = multiprocessing.Process(target=lbd, args=(domain,))
       jobs.append(p)
       p.start()
   f.close()
