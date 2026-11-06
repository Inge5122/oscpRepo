#!/bin/sh
#Autor: rewardone
#Descripción:
# Requiere permisos de root o suficientes para usar tcpdump
# Escuchará los primeros 8 paquetes de un login nulo (null session)
# y capturará la versión de SMB
#Notas:
# A veces no capturará o imprimirá múltiples
# líneas. Puede que necesites ejecutarlo una segunda vez.
if [ -z $1 ]; then echo "Uso: ./smbver.sh RHOST {RPORT}" && exit; else rhost=$1; fi
if [ ! -z $2 ]; then rport=$2; else rport=139; fi
tcpdump -s0 -n -i tap0 src $rhost and port $rport -A -c 10 2>/dev/null | grep -i "samba\|s.a.m" | tr -d '.' | grep -oP 'UnixSamba.*[0-9a-z]' | tr -d '\n' & echo -n "$rhost: " &
echo "exit" | smbclient -L $rhost 1>/dev/null 2>/dev/null
echo "" && sleep .1
