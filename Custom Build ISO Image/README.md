Creación de una imagen ISO de instalación personalizada

Si deseas construir una ISO personalizada, puedes seguir fácilmente los pasos en https://docs.kali.org/kali-dojo/02-mastering-live-build

Este directorio contiene un script (`setup.sh`) que automatizará este proceso. Es recomendable ejecutarlo en un sistema Kali. Esto construirá una ISO instaladora de 64 bits.

El trabajo futuro incluirá una opción en `setup.sh` para construir una ISO live o una ISO instaladora.

El script `setup.sh` hará lo siguiente:
* Descargar este repositorio en `tmp` para copiar los hooks, la lista de paquetes, el preseed y los scripts/listas del repositorio en su lugar.
* Descargar las dependencias para `live-build-config`
* Determinar si algún paquete en la lista de paquetes ha sido eliminado de kali-rolling (lo cual haría fallar la compilación)
* Configurar `install.cfg` e `isolinux` para el arranque automático y la selección de la instalación al iniciar

Todas las variantes se construirán al mismo tiempo. Comenta las variantes que no quieras construir. El entorno por defecto para Kali es ahora xfce y no gnome.

Opciones de personalización:
* Revisa cada hook en el directorio `hooks`. Si están presentes en el directorio `hooks/normal`, el hook se ejecutará tanto en la imagen live como en la instaladora. Las imágenes live solo requieren que estén en `config/hooks/live`.
* Revisa `kali.list.binary`. Esta es la lista de paquetes que se instalarán en la imagen instaladora. Nombrarlo `kali.list.chroot` instalará paquetes únicamente en la imagen live. Nombrarlo `kali.list` instalará paquetes tanto en live como en el instalador.
* Variante. Puedes elegir qué variante construir (gnome, mate, lxde, etc.). Al añadir variantes adicionales, asegúrate de que la lista de paquetes incluya los requisitos de paquetes de esa variante para su entorno visual.
* Preseed. El archivo preseed incluido tiene contraseñas por defecto, sin cuenta de usuario, etc. DEBES cambiar la contraseña de root en el preseed. Próximamente se añadirá soporte para cuentas locales para reflejar kali.2020.

Otras opciones (flags) que puedes considerar incluir en el script `/live-build-config/auto/config` son:

--apt-recommends false 
--apt-indices false
--clean 
--debian-installer-gui false
--cache-packages true 
--apt-http-proxy http://your.proxy
--memtest none

El producto final si ejecutas este script será una ISO de Kali de 64 bits con la capacidad de instalarse de forma completamente desatendida. La lista de paquetes actual tendrá alrededor de 100 herramientas, varios diccionarios (wordlists), scripts de reconocimiento, scripts de enumeración, el KeepNote de BookmarkList y zsh con algunos plugins. Es una ISO bastante grande y, como tal, solo cabe la imagen live o la imagen instaladora en un DVD.


Otras notas técnicas para futura depuración:
* Es posible incluir un paquete `tasksel` personalizado. Esto está incluido en `setup.sh` ahora, pero no se utiliza por el momento durante la instalación (live).
* `--installer live` es clave para facilitar las cosas, pero usar `live-build` aumenta el tamaño del disco.

Algunos recursos excelentes:
http://xpt.sourceforge.net/techdox/nix/live/debian-cd/dcd04-DebianDistributionCD/ar01s02.html
https://d-i.debian.org/doc/internals/apb.html#idm914
https://lists.debian.org/debian-live/2011/04/msg00009.html



Registro de cambios (Changelog): 
2-2020:
 Actualizado para Kali.2020.1. 
 Moviendo listas a `/usr/share/lists`
 Paquetes eliminados por restricciones de tamaño/compatibilidad:
  atom
  maltego
  maltego-teeth
  veil
 Paquetes añadidos:
  openssh-server
 Hooks actualizados:
  Algunos hooks se han cambiado para descargar archivos `.zip` en lugar de clonar repositorios por restricciones de tamaño
  cactustorch: añadido
  firefox: preferencias y extensiones añadidas (aún necesita un hook para `user.js`)
  keepnote: eliminado
  cherrytree: añadido
  sharpshooter: añadido
  vscode: añadido






