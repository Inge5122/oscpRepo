#!/bin/sh
# Este script aprovisiona una instalación base para reflejar la configuración de la ISO personalizada

# Instalar tantos paquetes de apt como sea posible:
apt-get update

variant="xfce"
install_string=""
for package in $(cat $variant/kali.list.chroot | grep -v "#"); do
  install_string="$install_string $package";
done

REM=""
for i in $install_string; do 
  res="";
  res=$(apt-cache search $i); 
  if [ -z "${res}" ]; then 
    echo "$i ha sido eliminado de kali-rolling. ¡Crea un hook o descarga y añade el paquete manualmente!"; REM="$i $REM"; 
  fi;
done

if [ ! -z "${REM}" ]; then 
  exit 1;
fi;


apt install -y $install_string 

for hook in $(ls hooks/*.chroot); do
  cat $hook | bash;
done
