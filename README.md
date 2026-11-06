# OSCPRepo

> [!NOTE]
> - Consulta la **[Caja de Herramientas de Ciberseguridad (CAJA_DE_HERRAMIENTAS.md)](./CAJA_DE_HERRAMIENTAS.md)** para acceder al arsenal de utilidades organizadas por fase y su instalación en Ubuntu/Debian.
> - Consulta el **[Plan de Estudio y Guía de Laboratorios (PLAN_DE_ESTUDIO_Y_LABORATORIOS.md)](./PLAN_DE_ESTUDIO_Y_LABORATORIOS.md)** para seguir la progresión por niveles ("subiendo los voltios"), preparación en Ubuntu, lista recomendada de máquinas y plantilla de reportes.

Esta es una lista de recursos y scripts que he estado recopilando (y continúo recopilando) en preparación para el OSCP. Ahora que lo he obtenido, este repositorio seguirá ampliando sus recursos para futuras certificaciones. Todos estos son recursos gratuitos en Internet, así que siéntete libre de usarlos como quieras para ayudarte en tus estudios o como material de referencia. Si he tomado información tuya o de tu trabajo, por favor házmelo saber para poder darte el crédito correspondiente.

¿Tienes un millón de marcadores guardados? ¿Todos esos marcadores contienen información única? ¿Repositorios de GitHub marcados con estrella para más tarde?
Quería componer y ofrecer una recopilación real de todos estos recursos en un único cuaderno organizado. Ya no hay necesidad de enlaces guardados en marcadores. No hace falta abrir un navegador web. Todo estará aquí para ti.

# CherryTree

Al no poder instalar KeepNote en Kali-Rolling, se ha realizado la migración a CherryTree. Ten en cuenta que los nodos estarán desordenados debido a la importación en comparación con KeepNote. El ordenamiento y los enlaces se irán corrigiendo con el tiempo, además de añadir contenido nuevo.

# Recursos Destacados
UsefulCommands.ctb

Contiene metodologías, comandos y ubicaciones de archivos interesantes. Esto se ha ido trasladando cada vez más a BookmarkList. El objetivo será asegurar que UsefulCommands sea exactamente eso: comandos útiles (páginas man, material de referencia, etc.). Para guías paso a paso (walkthroughs) e información detallada, dirígete a BookmarkList.

BookmarkList.ctb

Lista tras lista de marcadores recopilados, páginas de GitHub, blogs, reseñas de OSCP, herramientas y mucho más, todo reunido en una lista organizada de marcadores y referencias a las que poder recurrir (sin conexión). Las fuentes de todos los recursos siguen ahí para que puedas leer el material directamente si lo deseas. Este es un trabajo en curso y hay secciones que aún no he terminado de leer ni les he creado nodos secundarios, pero aun así es increíblemente extenso y se sigue trabajando en él (casi) todos los días (¡mira el historial de commits!).

![Parent Nodes](https://github.com/rewardone/OSCPRepo/blob/master/CherryTrees/BookmarkList.png)

Recon_Scan.py

Un script popular en Python 3 (Python 2 para fines de archivo). Su objetivo es ejecutar nmap, identificar servicios populares, pasar ese descubrimiento a otros scripts para una enumeración detallada, etc., y luego realizar un escaneo completo de nmap (en caso de que se haya pasado algo por alto). La integración parcial con Sparta está completa, y `setup.sh` moverá esos archivos por ti. También echa un vistazo a Vanquish.

Desde la CLI, reconscan hace el trabajo con un simple `./reconscan.py`. Está diseñado para ejecutarse en múltiples hilos (multithreaded) contra múltiples objetivos simultáneamente si el ancho de banda de la red lo permite. Puedes ajustar el `min-rate` en los scripts.

Ahora hay un script `setup.sh` en la carpeta `/scripts` que clonará algunos repositorios necesarios, moverá las carpetas a su lugar y dejará a reconscan listo para funcionar. Recon_Scan ha sido portado a Python 3, pero puede tener algunos detalles por pulir. Se agradece la ayuda con las pruebas.


# Otras Cosas

Las carpetas hablan mayormente por sí solas. `lists` contiene un montón de diccionarios/wordlists (`setup.sh` descargará más). Algunas metodologías y hojas de referencia (cheat sheets) están descargadas. Algunas herramientas y scripts se mantienen de forma local hasta que sean integrados. Puedes encontrar verificadores de enumeración local y de escalada de privilegios (privesc) en sus respectivas carpetas (ten en cuenta que son instantáneas y no necesariamente las versiones más actualizadas de estos scripts).

GetGitHubStars

Un script rápido de PowerShell que puede obtener los repositorios marcados con estrella de un usuario y exportarlos a un archivo CSV. Quería combinarlos con mis propios comentarios personales para tener una lista de todas mis estrellas y facilitar su clasificación, etiquetado, etc. Edita `commentsToJSON` y se añadirán a `output.csv`. Adicionalmente, el script puede obtener los repositorios en tendencia. Por hacer (TODO): añadir función para marcar repositorios con estrella desde el script; añadir función para poner en 'lista negra' los repositorios populares que ya no quieras ver.

# Últimos Cambios
Actualización 2020: El OSCP está ahora en la versión 2. Aún no he comprado el acceso al nuevo material, por lo que se agradecen las actualizaciones para la versión 2. Imagino que la mayor parte del material necesario sigue incluido, pero podría optimizarse más.

26 Dic 18: OSCP logrado. Esto marca un hito en el repositorio: toda la información necesaria para aprobar el OSCP está incluida aquí en las secciones correspondientes. Aunque la información no puede reemplazar la práctica real, si necesitas un lugar donde empezar a profundizar en un tema particular, está aquí o enlazado aquí. Reconscan no necesariamente se ha 'expandido' tanto como podría, pero ha sido crucial en los laboratorios, exámenes, HackTheBox y CTFs. Incluso si no quieres usar el script, revisa los módulos para ver los comandos que deberías incluir en tu metodología.

22 Ago 18: BlackHat y Defcon fueron increíbles. Hubo mucha corrección de errores. Los scripts se están volviendo más modulares y agradables de usar (saluda al reconocimiento de NFS y LDAP). `dirbustEVERYTHING` ha recibido mucha atención, incluyendo la integración de wfuzz y parameth. Puedes comprobar qué scripts de nmap se ejecutan y en qué script se encuentran con la hoja 'nmap to recon scan mapping' (parcialmente completa porque sobrescribí la maestra, pero la terminaré de nuevo más adelante). Se han ajustado algunas listas y payloads.

21 May 18: Unicornscan y el multiprocesamiento de Python no se llevan bien. Se cambió todo a Nmap. Es recomendable ajustar `--min-rate` según sea necesario. Se añadieron algunos módulos. Banners. Toda la lógica de `dirbEverything` y los diccionarios han sido actualizados. Nmap también se ha cambiado para ejecutar escaneos de conexión completa (`sT`). Los escaneos SYN son demasiado identificables (aunque la velocidad probablemente no ayude a este script).

10 Abr 18: LinEnum actualizado. La mayoría de los scripts de enumeración no están mal incluso si no se han actualizado en algunos años. Tuve preferencia por `linuxprivchecker.py` durante mucho tiempo; sin embargo, quería algo por si acaso una máquina no tenía Python instalado. Realmente me gusta la idea detrás de la rama master de `linux-privesc-check` de pentestmonkey. Incluso pensé en trabajar en Lynis o crear un perfil de 'pentest'. Finalmente elegí actualizar LinEnum debido a que es un solo archivo, está relativamente actualizado y ya cuenta con funciones como generación de informes y nivel de detalle (thorough). Muchas comprobaciones adicionales, número de versión actualizado, etc. Por favor, házmelo saber si quieres que se incluyan comprobaciones adicionales o si encuentras errores. Disfrútalo.

28 Mar 18: Algunas actualizaciones menores. Se incluyó `aliverecon`, que simplemente hace un escaneo ping de nmap. Se incluyó `nbtscan` para cobertura adicional en `smbrecon`. Reconscan ahora hará una copia de seguridad de todo en la carpeta `exam` y lo moverá cada vez que se inicie. Por favor, asegúrate de tener siempre un archivo `targets.txt` en su lugar.

4 Mar 18: `dirTrav.py` como envoltorio (wrapper) para dotdotpwn. Requiere un archivo con una lista de URLs a probar. Si encuentra algo, obtendrá los archivos listados en la lista por defecto (`lists/Personal/Misc\ Lists/DirTrav/linux_all.txt`). El soporte para Windows no ha sido probado. Este script requiere una invocación manual. No quería que se ejecutara automáticamente a partir de los resultados de gobuster (ya que siempre hay mucha basura y solo aumentaría el tiempo de dirTrav). Nota especial: `setup.sh` modifica dotdotpwn para que no sea necesario presionar 'Enter' al iniciar el escaneo.

20 Feb 18: Como mínimo, `httpenum`, `httpsenum` y `dirbustEVERYTHING` deberían poder manejar cambios de puerto (es decir, escanear y generar salidas de diferentes puertos manualmente). Es posible que `httpenum` y `httpsenum` se extraigan y se conviertan en sus propios módulos. `dirbustEVERYTHING` ahora busca extensiones `.php` y `.html` y ejecuta `cewl` para generar una nueva lista para enumeración adicional.
