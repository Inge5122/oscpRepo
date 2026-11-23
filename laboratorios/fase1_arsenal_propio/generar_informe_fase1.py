#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Informe Técnico Formal: Fase 1 - Validación del Arsenal Propio (Lab A y Lab B)
OSCP / Pentesting Ético y Base de Investigación de Maestría
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout(doc, text, title="NOTA TÉCNICA / HALLAZGO CRÍTICO"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EDF2F7")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="28" w:space="0" w:color="2B6CB0"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_title = p.add_run(f"[{title}]\n")
    run_title.bold = True
    run_title.font.name = "Arial"
    run_title.font.size = Pt(9.5)
    run_title.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
    
    run_text = p.add_run(text)
    run_text.font.name = "Arial"
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "1A202C")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="4A5568"/>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="4A5568"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="4A5568"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="4A5568"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(code_str.strip())
    run.font.name = "Courier New"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def style_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A365D")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    for row_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = "F7FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for i, val in enumerate(row_data):
            row_cells[i].text = str(val)
            set_cell_background(row_cells[i], bg_color)
            set_cell_margins(row_cells[i], top=80, bottom=80, left=120, right=120)
            p = row_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
                
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def build_report():
    doc = docx.Document()
    
    # Configuración de márgenes
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
    # Encabezado Principal
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("INFORME TÉCNICO FORMAL DE LABORATORIO")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Fase 1: Validación y Calibración del Arsenal Propio (Lab A: Reconocimiento & Lab B: Post-Explotación)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
    
    # Metadata del Documento
    tbl_meta = doc.add_table(rows=1, cols=4)
    meta_headers = ["Fecha de Evaluación", "Objetivo Evaluado", "Arquitectura / SO", "Certificación / Alcance"]
    meta_data = [["22 de Noviembre, 2026", "Metasploitable 2 (192.168.1.154)", "Ubuntu 8.04 Linux (Kernel 2.6.24 x86)", "OSCP / OSWP / Propuesta Maestría"]]
    style_table(tbl_meta, [1.6, 2.0, 1.8, 1.6], meta_headers, meta_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # 1. Resumen Ejecutivo
    h1 = doc.add_heading("1. Resumen Ejecutivo", level=1)
    h1.paragraph_format.space_before = Pt(12)
    p = doc.add_paragraph(
        "El presente informe documenta la ejecución formal de la Fase 1 del Plan de Estudio Intensivo, correspondiente "
        "a la validación de compatibilidad, corrección de defectos de ingeniería y calibración práctica de las herramientas "
        "internas del repositorio 'oscpRepo'. Dicha evaluación se estructuró en dos módulos complementarios: "
        "Laboratorio A (Automatizadores de Reconocimiento Perimetral en 'scripts/recon_enum3/') y Laboratorio B "
        "(Arsenal de Post-Explotación y Escalada de Privilegios Local en 'Priv Esc Checks/Linux/')."
    )
    p.paragraph_format.line_spacing = 1.15
    
    add_callout(
        doc,
        "La evaluación demostró que la suite de scripts históricos (2018-2020) presentaba bloqueos por rutas hardcodeadas "
        "hacia '/root/scripts/recon_enum/results/'. Tras el refactor dinámico a rutas relativas y la implementación de control "
        "robusto de excepciones en Python 3, la suite ejecutó con éxito contra Metasploitable 2 descubriendo acceso R/W en SMB, "
        "exportación total de la raíz en NFS, y vectores críticos de escalada local (SUID Nmap y vulnerabilidades de Kernel).",
        "DICTAMEN DE OPERATIVIDAD"
    )
    
    # 2. Laboratorio A: Automatizadores de Reconocimiento
    doc.add_heading("2. Laboratorio A: Validación de Suite de Reconocimiento (scripts/recon_enum3/)", level=1)
    
    p = doc.add_paragraph(
        "El objetivo del Laboratorio A consistió en verificar la capacidad de la suite para enumerar servicios específicos "
        "sin generar sobrecarga en la red ni causar falsos positivos por fallos de dependencias. Se auditaron cuatro scripts modulares:"
    )
    
    # Tabla de Resultados Lab A
    tbl_lab_a = doc.add_table(rows=1, cols=4)
    h_a = ["Script Evaluado", "Puerto / Protocolo", "Hallazgo Técnico Principal", "Vector de Ataque Asociado"]
    d_a = [
        ["smbrecon.py", "TCP 139, 445 (SMB)", "Samba 3.0.20-Debian, SMBv1, Recurso '\\\\tmp' con permisos READ/WRITE anónimo", "RCE directo vía usermap_script; escritura de shells o binarios maliciosos"],
        ["nfsrecon.py", "TCP 111, 2049 (NFS)", "Export list 'showmount -e': '/' accesible para cualquier host (*)", "Montaje remoto no autenticado; inyección de claves SSH en /root/.ssh/"],
        ["sshrecon.py", "TCP 22 (SSH)", "OpenSSH 4.7p1 Debian 8ubuntu1, soporte de cifrados CBC heredados", "Enumeración de usuarios CVE-2018-15473 y password spraying controlado"],
        ["webrecon.py", "TCP 80 (HTTP)", "Apache 2.2.8 + PHP 5.2.4; Mutillidae con LFI/XSS; Nikto detectó phpMyAdmin y TRACE", "Inclusión de archivos locales (LFI), ejecución de scripts en cliente (XST/XSS)"]
    ]
    style_table(tbl_lab_a, [1.5, 1.4, 2.3, 1.8], h_a, d_a)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 2.1 Refactor de Código
    doc.add_heading("2.1 Refactorización e Ingeniería de Compatibilidad Aplicada", level=2)
    p = doc.add_paragraph(
        "Durante las pruebas se detectaron tres anomalías críticas en el código heredado de 'scripts/recon_enum3/' que fueron corregidas y versionadas en master:"
    )
    add_code_block(
        doc,
        "# [Mejora 1: Resolución dinámica de rutas relativas]\n"
        "SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))\n"
        "BASE = os.path.join(SCRIPT_DIR, 'results', 'exam', 'smb')\n"
        "mkdir_p(BASE)\n\n"
        "# [Mejora 2: Tolerancia a fallos por herramientas externas ausentes]\n"
        "try:\n"
        "    results = subprocess.check_output(['enum4linux', '-va', ip_address], encoding='utf8')\n"
        "except FileNotFoundError:\n"
        "    print(\"INFO: 'enum4linux' no está instalado en el sistema. Omitiendo.\")\n\n"
        "# [Mejora 3: Corrección de redirección en Python 3 subprocess.run]\n"
        "with open(outPath, 'w') as out_f, open(errPath, 'w') as err_f:\n"
        "    subprocess.run(['openssl', 's_client', '-connect', f'{ip}:{port}'], stdout=out_f, stderr=err_f)"
    )
    
    # 3. Laboratorio B: Arsenal de Post-Explotación Linux
    doc.add_heading("3. Laboratorio B: Arsenal de Post-Explotación Local (Priv Esc Checks/Linux/)", level=1)
    p = doc.add_paragraph(
        "Una vez obtenido el acceso al sistema, la fase de post-explotación requiere auditar vectores de elevación de privilegios. "
        "Se transfirieron y ejecutaron las herramientas del repositorio en Metasploitable 2 operando bajo el usuario no privilegiado 'msfadmin' (UID 1000)."
    )
    
    # 3.1 Detección de Exploits de Kernel
    doc.add_heading("3.1 Sugerencia y Auditoría de Vulnerabilidades de Kernel", level=2)
    p = doc.add_paragraph(
        "Al intentar ejecutar 'linux-exploit-suggester.sh' (Bash), el script abortó de forma inmediata reportando incompatibilidad: "
        "'Script needs Bash in version 4.0 or newer. Aborting'. La distribución Ubuntu 8.04 cuenta con Bash 3.2. "
        "En su lugar, se ejecutó 'perl-linux-exploit-suggester-2.pl' (Perl), el cual operó de forma inmediata y certera:"
    )
    add_code_block(
        doc,
        "#############################\n"
        "  Linux Exploit Suggester 2  \n"
        "#############################\n"
        "Local Kernel: 2.6.24 | Searching among 71 exploits...\n"
        "Possible Exploits:\n"
        "[+] american-sign-language (CVE-2010-4347) -> BID 45408\n"
        "[+] can_bcm (CVE-2010-2959)               -> EDB-ID 14814\n"
        "[+] dirty_cow (CVE-2016-5195)             -> EDB-ID 40616\n"
        "[+] do_pages_move (CVE-2010-0415)         -> Spenders Enlightenment\n"
        "[+] half_nelson (CVE-2010-3848)           -> EDB-ID 17787\n"
        "[+] msr (CVE-2013-0268)                   -> /dev/cpu/*/msr driver privilege escalation"
    )
    
    # 3.2 Auditoría de Configuraciones Locales con linuxprivchecker.py
    doc.add_heading("3.2 Auditoría de Configuraciones Débiles con linuxprivchecker.py", level=2)
    p = doc.add_paragraph(
        "El script 'linuxprivchecker.py' (escrito en Python 2.x por Mike Czumak) fue ejecutado como 'msfadmin'. "
        "El script realizó una auditoría completa del entorno sin requerir librerías externas adicionales. Destacan:"
    )
    
    tbl_lpc = doc.add_table(rows=1, cols=3)
    h_lpc = ["Categoría Auditada", "Detalle del Hallazgo", "Riesgo de Seguridad"]
    d_lpc = [
        ["Binarios SUID Críticos", "-rwsr-xr-x 1 root root /usr/bin/nmap (v4.53)", "CRÍTICO: Permite escape a shell de root inmediata ejecutando 'nmap --interactive' -> '!sh'"],
        ["Permisos de Archivos", "/etc/passwd y /etc/shadow permisos convencionales; /tmp con permisos globales", "MEDIO: Facilita almacenamiento y staging de herramientas de explotación"],
        ["Servicios de Red Locales", "Puertos 512, 513 (rlogin/rsh), 2049 (NFS), 3306 (MySQL) escuchando en 0.0.0.0", "ALTO: Conexiones internas no autenticadas o con credenciales por defecto"],
        ["Herramientas de Compilación", "gcc 4.2.3, make, perl 5.8.8, python 2.5.2 disponibles localmente", "ALTO: Permite compilar código fuente en C (exploits de kernel) directamente en el host"]
    ]
    style_table(tbl_lpc, [1.8, 2.7, 2.5], h_lpc, d_lpc)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 4. Comparativa Técnica: linuxprivchecker vs linpeas
    doc.add_heading("4. Comparativa Técnica de Arsenal: linuxprivchecker.py vs linpeas.sh", level=1)
    p = doc.add_paragraph(
        "En auditorías de seguridad y exámenes de certificación (OSCP), la elección de la herramienta de enumeración "
        "influye en el sigilo, la velocidad y la compatibilidad con el entorno auditado:"
    )
    
    tbl_comp = doc.add_table(rows=1, cols=4)
    h_comp = ["Parámetro de Evaluación", "linuxprivchecker.py (Repo)", "linpeas.sh (Estándar Moderno)", "Veredicto Operativo"]
    d_comp = [
        ["Huella en Disco / Tamaño", "Ligero (25 KB, un solo archivo)", "Pesado (> 800 KB en versiones recientes)", "linuxprivchecker es ideal para transferencias restrictivas"],
        ["Compatibilidad de Shell", "Independiente de la versión de Bash; corre sobre Python", "Exige Bash moderno; falla en shells reducidas o versiones antiguas (<4.0)", "linuxprivchecker y Perl LES superan a LinPEAS en sistemas legacy"],
        ["Ruido y Detección (EDR)", "Bajo: no genera cientos de subprocesos concurrentes", "Muy alto: ejecuta miles de comandos en bucle agresivo", "linuxprivchecker genera menor anomalía en logs de telemetría"],
        ["Formato de Salida", "Texto plano estructurado; fácil de procesar con regex o LLM", "Colores ANSI intensos; excelente visualización humana en consola", "linpeas gana en inspección humana; linuxprivchecker gana en ingesta automática ML"]
    ]
    style_table(tbl_comp, [1.6, 1.8, 1.8, 1.8], h_comp, d_comp)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 5. Articulación con la Tesis de Maestría
    doc.add_heading("5. Implicaciones para la Tesis de Maestría (Escaneo, ML y Ollama)", level=1)
    p = doc.add_paragraph(
        "La validación de estos laboratorios aporta valor directo a la propuesta académica de investigación de maestría:"
    )
    
    p1 = doc.add_paragraph()
    r = p1.add_run("1. Extracción de Telemetría para Modelos de Machine Learning: ")
    r.bold = True
    p1.add_run(
        "La salida estructurada generada por 'webrecon.py', 'smbrecon.py' y 'linuxprivchecker.py' proporciona vectores "
        "de características limpios (puertos, cabeceras HTTP, dialectos SMB, binarios SUID) que pueden ser vectorizados "
        "para entrenar modelos de detección de anomalías o clasificación automática de severidad."
    )
    
    p2 = doc.add_paragraph()
    r = p2.add_run("2. Triage y Remediación Automatizada con Ollama: ")
    r.bold = True
    p2.add_run(
        "Al alimentar los archivos de evidencia ('lpc_output.txt', 'smb_recon.txt') a un agente LLM local servido con Ollama, "
        "el modelo puede sintetizar de inmediato los 3 caminos más directos hacia el compromiso del sistema y sugerir "
        "las reglas de firewall o endurecimiento (hardening) requeridas, cerrando el ciclo de DevSecOps inteligente."
    )
    
    # 6. Conclusiones y Próximos Pasos
    doc.add_heading("6. Conclusiones y Próximos Pasos de la Fase 1", level=1)
    p = doc.add_paragraph(
        "1. Las herramientas del repositorio en 'scripts/recon_enum3/' y 'Priv Esc Checks/Linux/' se encuentran plenamente operativas, "
        "corregidas para entornos modernos y probadas con éxito contra sistemas Linux.\n"
        "2. Se demostró la importancia de contar con alternativas en múltiples lenguajes (Perl/Python) ante fallos de compatibilidad en Bash.\n"
        "3. El siguiente paso en la Fase 1 corresponde al Laboratorio C: Arsenal de Post-Explotación Windows sobre Metasploitable 3 "
        "('SecWiki-Windows-Exploit-Suggester.py' y 'HostEnum.py'), el cual se programará para cuando se active dicho entorno."
    )
    
    out_dir = "/home/diego-romero/Documents/oscpRepo/laboratorios/fase1_arsenal_propio"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Informe_Laboratorio_Fase1_Arsenal_Propio.docx")
    doc.save(out_path)
    print(f"Informe generado exitosamente en: {out_path}")

if __name__ == "__main__":
    build_report()
