#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Informe Técnico Formal: Fase 1 - Validación Integral del Arsenal Propio (Lab A, Lab B y Lab C)
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
    
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
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
    r_sub = p_sub.add_run("Fase 1: Validación Integral del Arsenal Propio (Lab A: Reconocimiento | Lab B: Linux PrivEsc | Lab C: Windows PrivEsc)")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
    
    tbl_meta = doc.add_table(rows=1, cols=4)
    meta_headers = ["Fecha de Evaluación", "Objetivos Evaluados", "Sistemas Operativos", "Alcance Metodológico"]
    meta_data = [["22 de Noviembre, 2026", "Metasploitable 2 & 3 Windows", "Ubuntu 8.04 x86 / Windows Server 2008 R2 x64", "OSCP / OSWP / Propuesta Maestría"]]
    style_table(tbl_meta, [1.6, 2.0, 1.8, 1.6], meta_headers, meta_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # 1. Resumen Ejecutivo
    h1 = doc.add_heading("1. Resumen Ejecutivo", level=1)
    h1.paragraph_format.space_before = Pt(12)
    p = doc.add_paragraph(
        "El presente informe formaliza la culminación integral de la Fase 1 del Plan de Estudio Práctico, orientada "
        "a la auditoría de código, refactorización para compatibilidad moderna y calibración operativa de las herramientas "
        "propias del repositorio 'oscpRepo'. Se evaluaron tres módulos críticos: Laboratorio A (Reconocimiento perimetral "
        "con 'scripts/recon_enum3/'), Laboratorio B (Post-explotación y escalada local Linux con 'Priv Esc Checks/Linux/') y "
        "Laboratorio C (Post-explotación y análisis de parches Windows con 'Priv Esc Checks/Windows/')."
    )
    p.paragraph_format.line_spacing = 1.15
    
    add_callout(
        doc,
        "DICTAMEN GLOBAL: Se corrigieron fallos de rutas absolutas antiguas y de control de flujo en Python 3 en la suite de red. "
        "En Linux, se verificó la superioridad de herramientas multiplataforma (Perl/Python) frente a scripts rígidos de Bash ante entornos legacy. "
        "En Windows, se contrastó el sugeridor histórico (.xls de 2017) frente a la solución estándar moderna WES-NG (actualizada a 2026), "
        "demostrando que mientras los exploits de kernel envejecen, las malas configuraciones de permisos y servicios (iCacls / Unquoted Paths) "
        "siguen vigentes como vectores críticos universales tanto en sistemas antiguos como modernos.",
        "DICTAMEN DE OPERATIVIDAD Y EFICACIA"
    )
    
    # 2. Laboratorio A: Reconocimiento Modular
    doc.add_heading("2. Laboratorio A: Suite de Reconocimiento Automatizado (scripts/recon_enum3/)", level=1)
    p = doc.add_paragraph(
        "Se evaluaron los scripts de reconocimiento dirigido contra los servicios activos de Metasploitable 2 (192.168.1.154), "
        "comprobando la capacidad de extraer inteligencia técnica sin generar denegación de servicio:"
    )
    
    tbl_lab_a = doc.add_table(rows=1, cols=4)
    h_a = ["Script Evaluado", "Puerto / Protocolo", "Hallazgo Técnico Principal", "Vector de Ataque Asociado"]
    d_a = [
        ["smbrecon.py", "TCP 139, 445 (SMB)", "Samba 3.0.20-Debian, SMBv1, Recurso '\\\\tmp' con permisos READ/WRITE anónimo", "RCE directo vía usermap_script; escritura de payloads en /tmp"],
        ["nfsrecon.py", "TCP 111, 2049 (NFS)", "Export list 'showmount -e': '/' exportado a cualquier host (*)", "Montaje remoto no autenticado; inyección de claves SSH en /root/.ssh/"],
        ["sshrecon.py", "TCP 22 (SSH)", "OpenSSH 4.7p1 Debian 8ubuntu1, soporte de cifrados CBC heredados", "Enumeración de usuarios CVE-2018-15473 y password spraying controlado"],
        ["webrecon.py", "TCP 80 (HTTP)", "Apache 2.2.8 + PHP 5.2.4; Mutillidae con LFI/XSS; Nikto detectó phpMyAdmin y TRACE", "Inclusión de archivos locales (LFI), ejecución de scripts en cliente (XST/XSS)"]
    ]
    style_table(tbl_lab_a, [1.5, 1.4, 2.3, 1.8], h_a, d_a)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 3. Laboratorio B: Arsenal de Post-Explotación Linux
    doc.add_heading("3. Laboratorio B: Arsenal de Post-Explotación Local Linux (Priv Esc Checks/Linux/)", level=1)
    p = doc.add_paragraph(
        "Operando bajo la cuenta no privilegiada 'msfadmin' (UID 1000) en Metasploitable 2, se auditaron los sugeridores de kernel y configuraciones locales:"
    )
    
    tbl_lpc = doc.add_table(rows=1, cols=3)
    h_lpc = ["Herramienta Evaluada", "Comportamiento / Hallazgo", "Impacto Técnico y Operativo"]
    d_lpc = [
        ["linux-exploit-suggester.sh", "Abortó: 'Script needs Bash in version 4.0 or newer'", "Incompatibilidad en Ubuntu 8.04 (Bash 3.2); demuestra la fragilidad de scripts bash modernos en entornos legacy"],
        ["perl-linux-exploit-suggester-2.pl", "Detectó 6 exploits: Dirty COW (CVE-2016-5195), can_bcm (CVE-2010-2959), half_nelson, etc.", "Excelente portabilidad: Perl se ejecuta de inmediato sin dependencias adicionales"],
        ["linuxprivchecker.py", "Detectó binario SUID crítico: /usr/bin/nmap (v4.53) y compiladores (gcc, make)", "Elevación inmediata a root ejecutando 'nmap --interactive' -> '!sh'"]
    ]
    style_table(tbl_lpc, [1.8, 2.8, 2.4], h_lpc, d_lpc)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 4. Laboratorio C: Arsenal de Post-Explotación Windows
    doc.add_heading("4. Laboratorio C: Arsenal de Post-Explotación Windows (Priv Esc Checks/Windows/)", level=1)
    p = doc.add_paragraph(
        "Para validar el arsenal Windows, se interactuó con Metasploitable 3 Windows (192.168.1.155) mediante WMI e Impacket. "
        "Se extrajo la telemetría base de 'systeminfo' revelando una instalación de Windows Server 2008 R2 SP1 con únicamente 2 hotfixes instalados (KB3191566 y KB976902)."
    )
    
    # 4.1 Análisis Comparativo de Sugeridores
    doc.add_heading("4.1 Auditoría de Parches: Script Histórico (.xls 2017) vs WES-NG (Actualizado 2026)", level=2)
    p = doc.add_paragraph(
        "Se identificó que el script original 'SecWiki-Windows-Exploit-Suggester.py' depende de Python 2 y de una base de datos estática "
        "('2017-06-14-mssb.xls') que desconoce los parches emitidos después de 2017. Para cerrar esta brecha tecnológica y homologar la metodología moderna, "
        "se integró y ejecutó WES-NG (Windows Exploit Suggester - Next Generation) con definiciones sincronizadas al 20261122:"
    )
    
    tbl_wes = doc.add_table(rows=1, cols=4)
    h_wes = ["CVE / Boletín", "Severidad / Impacto", "Componente Afectado", "Exploit Público Asociado"]
    d_wes = [
        ["CVE-2010-2729 (KB2347290)", "Critical / Remote Code Execution", "Print Spooler Service", "https://exploit-db.com/exploits/16361"],
        ["CVE-2012-0002 (KB2621440)", "Critical / Remote Code Execution", "Remote Desktop Protocol (RDP)", "MS12-020 (Denegación y RCE en puerto 3389)"],
        ["CVE-2010-4398 (KB2443105)", "Important / Elevation of Privilege", "Windows Kernel", "Exploit local de ring0 / escalada a SYSTEM"],
        ["CVE-2010-3338 (KB2401593)", "Important / Elevation of Privilege", "Task Scheduler", "Evasion de UAC y secuestro de tareas programadas"]
    ]
    style_table(tbl_wes, [1.8, 1.8, 1.8, 1.6], h_wes, d_wes)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 4.2 Auditoría de Permisos de Servicios Débiles con iCacls
    doc.add_heading("4.2 Detección de Malas Configuraciones de Servicios con iCacls_Service_Check.bat", level=2)
    p = doc.add_paragraph(
        "A diferencia de los exploits de kernel que dependen de parches específicos, la auditoría de configuraciones busca "
        "errores humanos o de instaladores de software de terceros. Se ejecutó 'iCacls_Service_Check.bat' contra todos los servicios no estándar:"
    )
    
    add_code_block(
        doc,
        "# [Salida de iCacls_Service_Check.bat en Metasploitable 3 Windows]\n"
        "C:\\glassfish\\glassfish4\\glassfish\\domains\\domain1\\bin\\domain1Service.exe\n"
        "  NT AUTHORITY\\SYSTEM:(I)(F)\n"
        "  BUILTIN\\Administrators:(I)(F)\n"
        "  BUILTIN\\Users:(I)(RX)\n\n"
        "C:\\ManageEngine\\DesktopCentral_Server\\bin\\wrapper.exe -s C:\\ManageEngine\\DesktopCentral_Server\\conf\\wrapper.conf:\n"
        "  The filename, directory name, or volume label syntax is incorrect.\n"
        "  [HALLAZGO CRÍTICO]: Ruta de binario de servicio sin entrecomillar (Unquoted Service Path)"
    )
    
    add_callout(
        doc,
        "La salida reveló un vector clásico de Unquoted Service Path en 'ManageEngine DesktopCentral'. "
        "Al no contener comillas en la ruta, Windows intentará ejecutar secuencialmente: C:\\ManageEngine.exe o "
        "C:\\ManageEngine\\DesktopCentral_Server\\bin\\wrapper.exe. Si un atacante tiene permisos de escritura en la carpeta raíz, "
        "puede colocar un binario malicioso y esperar el reinicio del servicio para obtener shell como NT AUTHORITY\\SYSTEM.",
        "VECTOR DE ESCALADA POR SERVICIOS SIN ENTRECOMILLAR"
    )
    
    # 5. Reflexión Estratégica: Kernel Exploits vs Misconfigurations
    doc.add_heading("5. Análisis Estratégico: Vulnerabilidades de Kernel vs Malas Configuraciones en 2026", level=1)
    p = doc.add_paragraph(
        "Un aprendizaje central de esta práctica responde a la vigencia del arsenal ofensivo en infraestructuras modernas:"
    )
    
    tbl_strat = doc.add_table(rows=1, cols=3)
    h_strat = ["Dimensión de Seguridad", "Exploits de Kernel (CVEs Específicos)", "Malas Configuraciones (Misconfigurations)"]
    d_strat = [
        ["Vida Útil del Vector", "Corta: Los proveedores emiten parches automáticos y los EDR bloquean firmas conocidas.", "Permanente: No se resuelven con 'Windows Update'; dependen de políticas de administración."],
        ["Riesgo Operativo", "Alto: Puede causar pantallazo azul (BSOD) o desestabilizar servidores de producción.", "Bajo: La explotación de permisos débiles o tokens es limpia, silenciosa y altamente confiable."],
        ["Frecuencia en Entornos Reales", "Presente en servidores obsoletos o aislados sin conexión a parches.", "Presente en más del 80% de despliegues modernos (Active Directory, software heredado, permisos laxos)."]
    ]
    style_table(tbl_strat, [1.8, 2.6, 2.6], h_strat, d_strat)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 6. Conexión con la Tesis de Maestría
    doc.add_heading("6. Integración con la Arquitectura de Tesis: Censys, ML y Triage con Ollama", level=1)
    p = doc.add_paragraph(
        "Los resultados de estos tres laboratorios fundamentan directamente el diseño del sistema autónomo de ciberseguridad propuesto para la maestría:"
    )
    
    p1 = doc.add_paragraph()
    r = p1.add_run("1. Extracción y Normalización de Telemetría Perimetral e Interna: ")
    r.bold = True
    p1.add_run(
        "El pipeline propuesto consumirá datos de escaneo externo (Censys API para banners y certificados) combinados con "
        "telemetría local de host (salida de systeminfo, listas de hotfixes, permisos de servicios). Esta combinación proporciona "
        "una visión integral de superficie externa e interna."
    )
    
    p2 = doc.add_paragraph()
    r = p2.add_run("2. Modelos de Machine Learning para Filtrado y Reducción de Ruido: ")
    r.bold = True
    p2.add_run(
        "Herramientas como WES-NG generan decenas de vulnerabilidades potenciales. El modelo de Machine Learning (clasificador supervisado) "
        "filtra los falsos positivos basándose en los procesos en ejecución reales y el contexto de red, priorizando las alertas de riesgo inminente."
    )
    
    p3 = doc.add_paragraph()
    r = p3.add_run("3. Agente de Razonamiento y Hardening Automatizado con Ollama: ")
    r.bold = True
    p3.add_run(
        "En lugar de depender de scripts estáticos con listas rígidas, el agente LLM local en Ollama recibe la telemetría "
        "filtrada y sintetiza el plan de remediación en lenguaje natural (ej. 'Comando icacls para revocar permisos de escritura "
        "en ManageEngine y regla de bloqueo en firewall para el puerto 3389'), cerrando la brecha entre detección y respuesta."
    )
    
    # 7. Conclusiones y Próximos Pasos
    doc.add_heading("7. Conclusiones y Cierre Oficial de la Fase 1", level=1)
    p = doc.add_paragraph(
        "1. La Fase 1 del Plan de Estudio (Arsenal Propio) queda 100% completada, verificada y documentada en los entornos Linux y Windows.\n"
        "2. Se modernizaron y corrigieron defectos de ejecución en la suite de red 'recon_enum3' y se validó la eficacia de 'Priv Esc Checks'.\n"
        "3. El arsenal propio se encuentra listo para servir de soporte técnico durante la Fase 2: Simulacros Intensivos de Examen OSCP (Black Box)."
    )
    
    out_dir = "/home/diego-romero/Documents/oscpRepo/laboratorios/fase1_arsenal_propio"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Informe_Laboratorio_Fase1_Arsenal_Propio.docx")
    doc.save(out_path)
    print(f"Informe actualizado y guardado exitosamente en: {out_path}")

if __name__ == "__main__":
    build_report()
