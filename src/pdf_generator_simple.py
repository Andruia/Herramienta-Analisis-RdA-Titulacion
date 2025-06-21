"""
Generador PDF mejorado para Andru.ia - Con tablas completas, orientación horizontal y gráficos
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import base64
from collections import Counter

def create_charts_pdf(data, title="📈 Reporte con Gráficos"):
    """Crea un PDF con gráficos y análisis visual en orientación horizontal"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 15))
    
    # Fecha
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<b>Generado:</b> {fecha}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    if isinstance(data, list) and len(data) > 0:
        story.append(Paragraph(f"<b>Total de RdAs:</b> {len(data)}", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # === GRÁFICO 1: Distribución por Nivel Bloom ===
        bloom_counts = {}
        for item in data:
            bloom_level = item.get('Nivel Bloom Detectado', 'N/A')
            bloom_counts[bloom_level] = bloom_counts.get(bloom_level, 0) + 1
        
        if bloom_counts:
            # Crear gráfico de barras
            fig, ax = plt.subplots(figsize=(8, 4))
            levels = list(bloom_counts.keys())
            counts = list(bloom_counts.values())
            
            bars = ax.bar(levels, counts, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#0F7B0F'])
            ax.set_title('Distribución por Nivel de Bloom', fontsize=14, fontweight='bold')
            ax.set_xlabel('Nivel de Bloom')
            ax.set_ylabel('Cantidad de RdAs')
            
            # Añadir valores en las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Guardar gráfico como imagen
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Añadir imagen al PDF
            story.append(Paragraph("<b>Gráfico 1: Distribución por Nivel de Bloom</b>", styles['Heading3']))
            story.append(Spacer(1, 5))
            img = Image(img_buffer, width=6*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 15))
        
        # === GRÁFICO 2: Distribución por Nivel Académico ===
        level_counts = {}
        for item in data:
            level = item.get('Nivel Académico Origen', 'N/A')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        if level_counts:
            # Crear gráfico de pastel
            fig, ax = plt.subplots(figsize=(6, 6))
            levels = list(level_counts.keys())
            counts = list(level_counts.values())
            colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
            
            wedges, texts, autotexts = ax.pie(counts, labels=levels, autopct='%1.1f%%', 
                                            colors=colors_pie, startangle=90)
            ax.set_title('Distribución por Nivel Académico', fontsize=14, fontweight='bold')
            
            # Guardar gráfico
            img_buffer2 = io.BytesIO()
            plt.savefig(img_buffer2, format='png', dpi=150, bbox_inches='tight')
            img_buffer2.seek(0)
            plt.close()
            
            # Añadir al PDF
            story.append(Paragraph("<b>Gráfico 2: Distribución por Nivel Académico</b>", styles['Heading3']))
            story.append(Spacer(1, 5))
            img2 = Image(img_buffer2, width=4*inch, height=4*inch)
            story.append(img2)
            story.append(Spacer(1, 15))
        
        # === GRÁFICO 3: Promedios de Puntuaciones ===
        metrics = ['Puntaje Observable', 'Puntaje Medible', 'Puntaje Evaluable', 'Puntaje Corrección']
        averages = []
        
        for metric in metrics:
            scores = []
            for item in data:
                score = item.get(metric, 0)
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif str(score).isdigit():
                    scores.append(int(score))
            
            if scores:
                averages.append(sum(scores) / len(scores))
            else:
                averages.append(0)
        
        if averages:
            fig, ax = plt.subplots(figsize=(8, 4))
            metric_labels = ['Observable', 'Medible', 'Evaluable', 'Corrección']
            bars = ax.bar(metric_labels, averages, color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
            
            ax.set_title('Promedios de Puntuaciones por Métrica', fontsize=14, fontweight='bold')
            ax.set_ylabel('Puntuación Promedio')
            ax.set_ylim(0, 3)
            
            # Añadir valores en las barras
            for bar, avg in zip(bars, averages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{avg:.2f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Guardar gráfico
            img_buffer3 = io.BytesIO()
            plt.savefig(img_buffer3, format='png', dpi=150, bbox_inches='tight')
            img_buffer3.seek(0)
            plt.close()
            
            # Añadir al PDF
            story.append(Paragraph("<b>Gráfico 3: Promedios de Puntuaciones</b>", styles['Heading3']))
            story.append(Spacer(1, 5))
            img3 = Image(img_buffer3, width=6*inch, height=3*inch)
            story.append(img3)
            story.append(Spacer(1, 15))
        
        # === NUEVA PÁGINA: TABLA COMPLETA ===
        story.append(PageBreak())
        story.append(Paragraph("<b>Tabla Detallada de Resultados</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Tabla completa (versión compacta para que quepa con los gráficos)
        table_data = [[
            'RdA', 'Nivel Bloom', 'Obs', 'Med', 'Eval', 'Corr', 'Aut.Acc', 'K.Conc'
        ]]
        
        for item in data:
            rda_text = str(item.get('RA', 'N/A'))
            if len(rda_text) > 40:
                rda_text = rda_text[:40] + '...'
            
            row = [
                rda_text,
                str(item.get('Nivel Bloom Detectado', 'N/A')),
                str(item.get('Puntaje Observable', 'N/A')),
                str(item.get('Puntaje Medible', 'N/A')),
                str(item.get('Puntaje Evaluable', 'N/A')),
                str(item.get('Puntaje Corrección', 'N/A')),
                str(item.get('Autenticidad Acción', 'N/A')),
                str(item.get('Conocimiento Conceptual', 'N/A'))
            ]
            table_data.append(row)
        
        # Tabla optimizada para orientación horizontal
        col_widths = [3*inch, 1.2*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.7*inch, 0.7*inch]
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Generado por Andru.ia - Reporte con Gráficos y Análisis Visual", styles['Italic']))
    
    doc.build(story)
    return buffer.getvalue()

def create_executive_pdf(data, title="📊 Reporte Ejecutivo"):
    """Crea un PDF ejecutivo con columnas esenciales"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))
    
    # Fecha
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<b>Generado:</b> {fecha}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if isinstance(data, list) and len(data) > 0:
        story.append(Paragraph(f"<b>Total de RdAs:</b> {len(data)}", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Tabla ejecutiva con columnas esenciales
        table_data = [['RdA', 'Nivel Bloom', 'Observable', 'Medible', 'Evaluable', 'Corrección']]
        
        for item in data:
            rda_text = str(item.get('RA', 'N/A'))
            if len(rda_text) > 40:
                rda_text = rda_text[:40] + '...'
            
            row = [
                rda_text,
                str(item.get('Nivel Bloom Detectado', 'N/A')),
                str(item.get('Puntaje Observable', 'N/A')),
                str(item.get('Puntaje Medible', 'N/A')),
                str(item.get('Puntaje Evaluable', 'N/A')),
                str(item.get('Puntaje Corrección', 'N/A'))
            ]
            table_data.append(row)
        
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generado por Andru.ia - Reporte Ejecutivo", styles['Italic']))
    
    doc.build(story)
    return buffer.getvalue()

def create_complete_pdf(data, title="📋 Reporte Completo"):
    """Crea un PDF completo con TODAS las columnas en orientación horizontal"""
    buffer = io.BytesIO()
    # Usar orientación horizontal (landscape) para más espacio
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 15))
    
    # Fecha
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<b>Generado:</b> {fecha}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    if isinstance(data, list) and len(data) > 0:
        story.append(Paragraph(f"<b>Total de RdAs:</b> {len(data)}", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Distribución por niveles
        level_counts = {}
        for item in data:
            level = item.get('Nivel Académico Origen', 'N/A')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        if level_counts:
            story.append(Paragraph("<b>Distribución por Nivel Académico:</b>", styles['Normal']))
            for nivel, count in level_counts.items():
                story.append(Paragraph(f"• Nivel {nivel}: {count} RdAs", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Tabla completa con TODAS las columnas importantes
        table_data = [[
            'RdA', 'Verbo', 'Nivel Bloom', 'Adecuación', 
            'Obs', 'Med', 'Eval', 'Corr',
            'Aut.Acc', 'Aut.Ctx', 'Aut.Sen',
            'K.Fact', 'K.Conc', 'K.Proc', 'K.Meta'
        ]]
        
        for item in data:
            rda_text = str(item.get('RA', 'N/A'))
            if len(rda_text) > 35:
                rda_text = rda_text[:35] + '...'
            
            row = [
                rda_text,
                str(item.get('Verbo Principal', 'N/A')),
                str(item.get('Nivel Bloom Detectado', 'N/A')),
                str(item.get('Clasificación vs Nivel Origen', 'N/A')),
                str(item.get('Puntaje Observable', 'N/A')),
                str(item.get('Puntaje Medible', 'N/A')),
                str(item.get('Puntaje Evaluable', 'N/A')),
                str(item.get('Puntaje Corrección', 'N/A')),
                str(item.get('Autenticidad Acción', 'N/A')),
                str(item.get('Autenticidad Contexto', 'N/A')),
                str(item.get('Autenticidad Sentido', 'N/A')),
                str(item.get('Conocimiento Factual', 'N/A')),
                str(item.get('Conocimiento Conceptual', 'N/A')),
                str(item.get('Conocimiento Procedimental', 'N/A')),
                str(item.get('Conocimiento Metacognitivo', 'N/A'))
            ]
            table_data.append(row)
        
        # Tabla con anchos optimizados para orientación horizontal
        col_widths = [
            2.2*inch,  # RdA
            0.6*inch,  # Verbo
            0.8*inch,  # Nivel Bloom
            0.7*inch,  # Adecuación
            0.4*inch,  # Obs
            0.4*inch,  # Med
            0.4*inch,  # Eval
            0.4*inch,  # Corr
            0.5*inch,  # Aut.Acc
            0.5*inch,  # Aut.Ctx
            0.5*inch,  # Aut.Sen
            0.5*inch,  # K.Fact
            0.5*inch,  # K.Conc
            0.5*inch,  # K.Proc
            0.5*inch   # K.Meta
        ]
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(table)
        
        # Leyenda de abreviaciones
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Leyenda:</b>", styles['Heading3']))
        legend_text = """
        <b>Obs:</b> Observable, <b>Med:</b> Medible, <b>Eval:</b> Evaluable, <b>Corr:</b> Corrección<br/>
        <b>Aut.Acc:</b> Autenticidad Acción, <b>Aut.Ctx:</b> Autenticidad Contexto, <b>Aut.Sen:</b> Autenticidad Sentido<br/>
        <b>K.Fact:</b> Conocimiento Factual, <b>K.Conc:</b> Conceptual, <b>K.Proc:</b> Procedimental, <b>K.Meta:</b> Metacognitivo
        """
        story.append(Paragraph(legend_text, styles['Normal']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Generado por Andru.ia - Análisis Completo", styles['Italic']))
    
    doc.build(story)
    return buffer.getvalue()

def create_simple_pdf(data, title="Reporte Andru.ia"):
    """Crea un PDF simple con columnas básicas"""
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
    
    if isinstance(data, list) and len(data) > 0:
        story.append(Paragraph(f"Total de RdAs: {len(data)}", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Tabla simple
        table_data = [['RdA', 'Nivel Bloom', 'Observable', 'Corrección']]
        
        for item in data:
            rda_text = str(item.get('RA', 'N/A'))
            if len(rda_text) > 50:
                rda_text = rda_text[:50] + '...'
            
            row = [
                rda_text,
                str(item.get('Nivel Bloom Detectado', 'N/A')),
                str(item.get('Puntaje Observable', 'N/A')),
                str(item.get('Puntaje Corrección', 'N/A'))
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
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generado por Andru.ia", styles['Italic']))
    
    doc.build(story)
    return buffer.getvalue()

def generate_detailed_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF detallado con análisis completo"""
    return create_simple_pdf(data, "📄 Análisis Detallado de RdAs")

def generate_executive_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF ejecutivo con columnas esenciales"""
    return create_executive_pdf(data, "📊 Reporte Ejecutivo - Resumen Gerencial")

def generate_level_pdf(data, level, summary_stats=None):
    """Genera PDF por nivel con tabla completa filtrada"""
    if isinstance(data, list) and len(data) > 0:
        # Filtrar datos por nivel académico
        filtered_data = []
        level_counts = {}
        
        for item in data:
            item_level = item.get('Nivel Académico Origen', 
                        item.get('nivel_academico', 
                        item.get('level', 
                        item.get('Nivel Origen', ''))))
            
            level_counts[str(item_level)] = level_counts.get(str(item_level), 0) + 1
            
            item_level_str = str(item_level).strip()
            level_str = str(level).strip()
            
            if (item_level_str == level_str or 
                (item_level_str.isdigit() and level_str.isdigit() and int(item_level_str) == int(level_str))):
                filtered_data.append(item)
        
        if filtered_data:
            return create_complete_pdf(filtered_data, f"🎯 Análisis Nivel Académico {level} ({len(filtered_data)} RdAs)")
        else:
            debug_info = [{
                'RA': f'No se encontraron RdAs para el nivel académico {level}',
                'Nivel Bloom Detectado': 'N/A',
                'Puntaje Observable': 'N/A',
                'Puntaje Corrección': f'Niveles disponibles: {", ".join(level_counts.keys())}'
            }]
            return create_simple_pdf(debug_info, f"🎯 Análisis Nivel Académico {level} (Sin datos)")
    
    return create_simple_pdf(data, f"🎯 Análisis Nivel Académico {level}")

def generate_complete_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF completo con todas las columnas en orientación horizontal"""
    return create_complete_pdf(data, "📋 Reporte Completo - Análisis Integral")

def generate_charts_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF con gráficos y análisis visual"""
    return create_charts_pdf(data, "📈 Reporte con Gráficos y Análisis Visual")