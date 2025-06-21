"""
Generador PDF ultra-simplificado para Andru.ia
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
from datetime import datetime

def create_simple_pdf(data, title="Reporte Andru.ia"):
    """Crea un PDF simple con los datos proporcionados"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))

    # Fecha
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Generado: {fecha}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Debug info - mostrar estructura de datos
    if isinstance(data, list) and len(data) > 0:
        story.append(Paragraph(f"Total de RdAs: {len(data)}", styles['Heading2']))

        # Mostrar las claves disponibles del primer elemento para debug
        first_item = data[0]
        available_keys = list(first_item.keys()) if isinstance(first_item, dict) else []
        story.append(Paragraph(f"Columnas disponibles: {', '.join(available_keys[:10])}", styles['Normal']))
        story.append(Spacer(1, 10))

        # Contar niveles académicos para debug
        level_counts = {}
        for item in data:
            level = item.get('Nivel Académico Origen', 'N/A')
            level_counts[level] = level_counts.get(level, 0) + 1

        if level_counts:
            story.append(Paragraph("Distribución por Nivel Académico:", styles['Heading3']))
            for nivel, count in level_counts.items():
                story.append(Paragraph(f"• Nivel {nivel}: {count} RdAs", styles['Normal']))
            story.append(Spacer(1, 10))

        # Tabla simple
        table_data = [['RdA', 'Nivel Bloom', 'Observable', 'Corrección']]

        for item in data:
            rda_text = str(item.get('RA', item.get('rda', 'N/A')))
            if len(rda_text) > 50:
                rda_text = rda_text[:50] + '...'

            row = [
                rda_text,
                str(item.get('Nivel Bloom Detectado', item.get('bloom_level', 'N/A'))),
                str(item.get('Puntaje Observable', item.get('observable', 'N/A'))),
                str(item.get('Puntaje Corrección', item.get('correction', 'N/A')))
            ]
            table_data.append(row)

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
    else:
        story.append(Paragraph("No hay datos para mostrar", styles['Normal']))

    # Pie
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generado por Andru.ia", styles['Italic']))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_detailed_pdf(data, academic_level=None, summary_stats=None):
    return create_simple_pdf(data, "Análisis Detallado de RdAs")

def generate_executive_pdf(data, academic_level=None, summary_stats=None):
    return create_simple_pdf(data, "Reporte Ejecutivo")

def generate_level_pdf(data, level, summary_stats=None):
    """Genera PDF por nivel - CORREGIDO para filtrar correctamente"""
    if isinstance(data, list) and len(data) > 0:
        # Filtrar datos por nivel académico
        filtered_data = []
        for item in data:
            # Buscar el nivel académico en diferentes posibles nombres de columna
            item_level = item.get('Nivel Académico Origen', item.get('nivel_academico', item.get('level', '')))

            # Convertir a string y limpiar espacios
            item_level_str = str(item_level).strip()
            level_str = str(level).strip()

            # Comparar niveles
            if item_level_str == level_str:
                filtered_data.append(item)

        if filtered_data:
            return create_simple_pdf(filtered_data, f"Análisis Nivel Académico {level} ({len(filtered_data)} RdAs)")
        else:
            # Si no hay datos filtrados, crear PDF con mensaje
            empty_data = [{
                'RA': f'No se encontraron RdAs para el nivel académico {level}',
                'Nivel Bloom Detectado': 'N/A',
                'Puntaje Observable': 'N/A',
                'Puntaje Corrección': 'N/A'
            }]
            return create_simple_pdf(empty_data, f"Análisis Nivel Académico {level} (Sin datos)")

    return create_simple_pdf(data, f"Análisis Nivel Académico {level}")

def generate_complete_pdf(data, academic_level=None, summary_stats=None):
    return create_simple_pdf(data, "Reporte Completo")