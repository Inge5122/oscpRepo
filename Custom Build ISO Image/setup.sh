#!/bin/bash

# POR HACER (TODO): Integrar Covenant, Merlin y otros C2
# POR HACER (TODO): Binarios precompilados para Seatbelt y otros enumeradores
# POR HACER (TODO): Experimentar con instalador exclusivo

# Entorno de compilación
# Variantes disponibles: xfce, gnome, lxde
live_build_dir="/root/live-build-config"
variant="xfce"
live_build_config_package_list="$live_build_dir/kali-config/variant-$variant/package-lists/kali.list.chroot"

#============EN PRUEBAS============#
simple_cdd_profile_name="kali-custom"
simple_cdd_profile_folder="$live_build_dir/simple-cdd/profiles/$simple_cdd_profile_name"
simple_cdd_profile_package_list="$simple_cdd_profile_folder/$simple_cdd_profile_name.packages"
simple_cdd_conf="$live_build_dir/simple-cdd/simple-cdd.conf"
#==================================#

echo
echo "=============================================================================="
echo "Actualizando el sistema e instalando cabeceras del kernel"
echo "=============================================================================="
echo
apt-get update && apt-get -y upgrade && apt-get -y dist-upgrade
apt-get -y install linux-headers-$(uname-r)

echo
echo "=============================================================================="
echo "Descargando y actualizando el repositorio live-build-config"
echo "=============================================================================="
echo

apt install git curl rsync live-build cdebootstrap devscripts -y
direc=$live_build_dir
if [ -d $direc ]; then cd $direc && git pull; else git clone https://gitlab.com/kalilinux/build-scripts/live-build-config.git $direc; fi

echo
echo "=============================================================================="
echo "Descargando archivos de configuración de live-build desde OSCPRepo"
echo "=============================================================================="
echo
if [ -d "/tmp/OSCPRepo" ]; then cd "/tmp/OSCPRepo" && git pull; else git clone https://github.com/rewardone/OSCPRepo.git "/tmp/OSCPRepo"; fi

# Copiar la lista de paquetes personalizada a kali.list.chroot
cp "/tmp/OSCPRepo/Custom Build ISO Image/$variant/kali.list.chroot" "$live_build_config_package_list"

echo
echo "=============================================================================="
echo "Comprobando paquetes que puedan haber sido eliminados de kali-rolling"
echo "=============================================================================="
echo
REM=""
for i in $(cat "/tmp/OSCPRepo/Custom Build ISO Image/$variant/kali.list.chroot" | grep -v "#" | grep -ve "^$"); do res=""; res=$(apt-cache search $i); if [ -z "${res}" ]; then echo "$i ha sido eliminado de kali-rolling. ¡Crea un hook o descárgalo manualmente!"; REM="$i $REM"; fi; done
if [ ! -z "${REM}" ]; then exit 1; fi;

echo
echo "=============================================================================="
echo "Creando tarea personalizada de Tasksel"
echo "=============================================================================="
echo

tasksel_hook="$live_build_dir/kali-config/common/includes.installer/usr/lib/live-installer.d/0050-custom-tasksel"
tasksel_file="/target/usr/share/tasksel/descs/kali-custom.desc"
if [ ! -f "$tasksel_hook" ]; then
  cat << EOF > $tasksel_hook
#!/bin/sh
set -e
echo 'Task: kali-custom
Relevance: 1
Description: Kali-Custom Package List
 This task installs custom ISO tools as listed in kali.list.chroot
Packages: list
EOF
  for i in $(cat "/tmp/OSCPRepo/Custom Build ISO Image/$variant/kali.list.chroot"); do echo " $i" >> $tasksel_hook; done
  cat << EOF >> $tasksel_hook
Section: user' > $tasksel_file
EOF
  chmod +x $tasksel_hook
fi

echo
echo "=============================================================================="
echo "Moviendo notas, scripts, listas y binarios para inclusión local"
echo "=============================================================================="
echo

direc="$live_build_dir/kali-config/common/includes.chroot/usr/share/windows-binaries"
mkdir -p $direc
cp -r /tmp/windows-binaries/* $direc 2>/dev/null

echo
echo "=============================================================================="
echo "Configurando preseed y archivo install.cfg"
echo "=============================================================================="
echo

cp "/tmp/OSCPRepo/Custom Build ISO Image/preseed.cfg" "$live_build_dir/kali-config/common/includes.installer/preseed.cfg"

isolinux_alternate_install="$live_build_dir/kali-config/common/includes.binary/isolinux/install.cfg"
if [ -f $isolinux_alternate_install ]; then 
  if ! grep -q "label installauto" $isolinux_alternate_install; then 
    cat << EOF >> $isolinux_alternate_install
label installauto
        menu label ^Install Automated 
        linux /install/vmlinuz
        initrd /install/initrd.gz
        append vga=788 @APPEND_INSTALL@ --- quiet file=/preseed.cfg locale=en_US.UTF-8 keymap=us hostname=kali domain=local.lan
EOF
  fi
  else
    cat << EOF >> $isolinux_alternate_install
label installauto
        menu label ^Install Automated 
        linux /install/vmlinuz
        initrd /install/initrd.gz
        append vga=788 @APPEND_INSTALL@ --- quiet file=/preseed.cfg locale=en_US.UTF-8 keymap=us hostname=kali domain=local.lan
EOF
fi

echo
echo "=============================================================================="
echo "Copiando hooks personalizados"
echo "=============================================================================="
echo
direc="$live_build_dir/kali-config/common/hooks/normal"
mkdir -p $direc
rm -rf $direc/*
rsync -r "/tmp/OSCPRepo/Custom Build ISO Image/hooks/" $direc
chmod +x $direc/*.chroot

echo
echo "=============================================================================="
echo "Modificando opciones de compilación en auto/config"
echo "=============================================================================="
echo
# Modificar instalador a modo live en lugar de cdrom
sed -i 's/--debian-installer cdrom/--debian-installer live/g' "$live_build_dir/auto/config"

# Remover memtest para reducir tamaño en disco
sed -i 's/--memtest memtest86/--memtest none/g' "$live_build_dir/auto/config"

echo
echo "=============================================================================="
echo "Limpiando y compilando... este proceso tomará tiempo..."
echo "=============================================================================="
echo

cd $live_build_dir
rm -rf cache/ chroot* live* config/ images/ local/

# Ejecutar script de compilación para la variante seleccionada
$live_build_dir/./build.sh --distribution kali-rolling --variant $variant --verbose

# Una vez finalizado, la ISO estará en el directorio de imágenes de live-build.
