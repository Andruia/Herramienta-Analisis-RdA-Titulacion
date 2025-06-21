"""
Generador PDF mejorado para Andru.ia - Con tablas completas, orientación horizontal y gráficos puros
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
import numpy as np
from collections import Counter

def create_pure_charts_pdf(data, title="📈 Análisis Visual - Solo Gráficos"):
    """Crea un PDF con SOLO gráficos y visualizaciones (sin tablas)"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # Configurar estilo matplotlib
    plt.style.use('default')
    colors_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83', '#0F7B0F', '#FF6B35', '#004E89']
    
    # Título principal
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 15))
    
    # Fecha y resumen
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<b>Generado:</b> {fecha} | <b>Total RdAs:</b> {len(data)}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if isinstance(data, list) and len(data) > 0:
        
        # === PÁGINA 1: DISTRIBUCIONES ===
        story.append(Paragraph("<b>DISTRIBUCIONES GENERALES</b>", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # GRÁFICO 1: Distribución por Nivel Bloom
        bloom_counts = {}
        for item in data:
            bloom_level = item.get('Nivel Bloom Detectado', 'N/A')
            bloom_counts[bloom_level] = bloom_counts.get(bloom_level, 0) + 1
        
        if bloom_counts:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico de barras - Bloom
            levels = list(bloom_counts.keys())
            counts = list(bloom_counts.values())
            bars1 = ax1.bar(levels, counts, color=colors_palette[:len(levels)])
            ax1.set_title('Distribución por Nivel de Bloom', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Nivel de Bloom')
            ax1.set_ylabel('Cantidad de RdAs')
            
            # Añadir valores en las barras
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # GRÁFICO 2: Distribución por Nivel Académico
            level_counts = {}
            for item in data:
                level = item.get('Nivel Académico Origen', 'N/A')
                level_counts[level] = level_counts.get(level, 0) + 1
            
            if level_counts:
                levels_ac = list(level_counts.keys())
                counts_ac = list(level_counts.values())
                wedges, texts, autotexts = ax2.pie(counts_ac, labels=[f'Nivel {l}' for l in levels_ac], 
                                                  autopct='%1.1f%%', colors=colors_palette[:len(levels_ac)], 
                                                  startangle=90)
                ax2.set_title('Distribución por Nivel Académico', fontsize=14, fontweight='bold')
                
                # Mejorar legibilidad
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Guardar y añadir al PDF
            img_buffer1 = io.BytesIO()
            plt.savefig(img_buffer1, format='png', dpi=150, bbox_inches='tight')
            img_buffer1.seek(0)
            plt.close()
            
            img1 = Image(img_buffer1, width=8*inch, height=3.5*inch)
            story.append(img1)
            story.append(Spacer(1, 20))
        
        # === PÁGINA 2: VERIFICABILIDAD ===
        story.append(PageBreak())
        story.append(Paragraph("<b>ANÁLISIS DE VERIFICABILIDAD</b>", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Calcular promedios de verificabilidad
        verificability_metrics = ['Puntaje Observable', 'Puntaje Medible', 'Puntaje Evaluable', 'Puntaje Corrección']
        verificability_averages = []
        verificability_labels = ['Observable', 'Medible', 'Evaluable', 'Corrección']
        
        for metric in verificability_metrics:
            scores = []
            for item in data:
                score = item.get(metric, 0)
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif str(score).replace('.', '').isdigit():
                    scores.append(float(score))
            
            if scores:
                verificability_averages.append(sum(scores) / len(scores))
            else:
                verificability_averages.append(0)
        
        if verificability_averages:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(verificability_labels, verificability_averages, 
                         color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'], width=0.6)
            
            ax.set_title('Promedios de Verificabilidad por Métrica', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Puntuación Promedio (0-3)', fontsize=12)
            ax.set_ylim(0, 3.2)
            ax.grid(axis='y', alpha=0.3)
            
            # Añadir valores en las barras
            for bar, avg in zip(bars, verificability_averages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                       f'{avg:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            plt.xticks(rotation=0)
            plt.tight_layout()
            
            img_buffer2 = io.BytesIO()
            plt.savefig(img_buffer2, format='png', dpi=150, bbox_inches='tight')
            img_buffer2.seek(0)
            plt.close()
            
            img2 = Image(img_buffer2, width=7*inch, height=4*inch)
            story.append(img2)
            story.append(Spacer(1, 20))
        
        # === PÁGINA 3: AUTENTICIDAD ===
        story.append(PageBreak())
        story.append(Paragraph("<b>ANÁLISIS DE AUTENTICIDAD</b>", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Calcular promedios de autenticidad
        authenticity_metrics = ['Autenticidad Acción', 'Autenticidad Contexto', 'Autenticidad Sentido']
        authenticity_averages = []
        authenticity_labels = ['Acción', 'Contexto', 'Sentido']
        
        for metric in authenticity_metrics:
            scores = []
            for item in data:
                score = item.get(metric, 0)
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif str(score).replace('.', '').isdigit():
                    scores.append(float(score))
            
            if scores:
                authenticity_averages.append(sum(scores) / len(scores))
            else:
                authenticity_averages.append(0)
        
        if authenticity_averages:
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(authenticity_labels, authenticity_averages, 
                         color=['#592E83', '#0F7B0F', '#FF6B35'], width=0.5)
            
            ax.set_title('Promedios de Autenticidad por Dimensión', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Puntuación Promedio', fontsize=12)
            ax.set_ylim(0, max(authenticity_averages) * 1.2 if authenticity_averages else 1)
            ax.grid(axis='y', alpha=0.3)
            
            # Añadir valores en las barras
            for bar, avg in zip(bars, authenticity_averages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                       f'{avg:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            plt.tight_layout()
            
            img_buffer3 = io.BytesIO()
            plt.savefig(img_buffer3, format='png', dpi=150, bbox_inches='tight')
            img_buffer3.seek(0)
            plt.close()
            
            img3 = Image(img_buffer3, width=6*inch, height=4*inch)
            story.append(img3)
            story.append(Spacer(1, 20))
        
        # === PÁGINA 4: CONOCIMIENTO ===
        story.append(PageBreak())
        story.append(Paragraph("<b>ANÁLISIS DE DIMENSIONES DEL CONOCIMIENTO</b>", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Calcular promedios de conocimiento
        knowledge_metrics = ['Conocimiento Factual', 'Conocimiento Conceptual', 
                           'Conocimiento Procedimental', 'Conocimiento Metacognitivo']
        knowledge_averages = []
        knowledge_labels = ['Factual', 'Conceptual', 'Procedimental', 'Metacognitivo']
        
        for metric in knowledge_metrics:
            scores = []
            for item in data:
                score = item.get(metric, 0)
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif str(score).replace('.', '').isdigit():
                    scores.append(float(score))
            
            if scores:
                knowledge_averages.append(sum(scores) / len(scores))
            else:
                knowledge_averages.append(0)
        
        if knowledge_averages:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(knowledge_labels, knowledge_averages, 
                         color=['#004E89', '#2E86AB', '#A23B72', '#F18F01'], width=0.6)
            
            ax.set_title('Promedios por Dimensión del Conocimiento', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Puntuación Promedio', fontsize=12)
            ax.set_ylim(0, max(knowledge_averages) * 1.2 if knowledge_averages else 1)
            ax.grid(axis='y', alpha=0.3)
            
            # Añadir valores en las barras
            for bar, avg in zip(bars, knowledge_averages):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                       f'{avg:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            plt.xticks(rotation=15, ha='right')
            plt.tight_layout()
            
            img_buffer4 = io.BytesIO()
            plt.savefig(img_buffer4, format='png', dpi=150, bbox_inches='tight')
            img_buffer4.seek(0)
            plt.close()
            
            img4 = Image(img_buffer4, width=7*inch, height=4*inch)
            story.append(img4)
            story.append(Spacer(1, 20))
        
        # === PÁGINA 5: COMPARACIÓN GENERAL ===
        story.append(PageBreak())
        story.append(Paragraph("<b>COMPARACIÓN GENERAL DE MÉTRICAS</b>", styles['Heading1']))
        story.append(Spacer(1, 10))
        
        # Gráfico de radar/spider con todas las métricas principales
        all_metrics = verificability_averages + authenticity_averages + knowledge_averages
        all_labels = verificability_labels + [f'Aut.{l}' for l in authenticity_labels] + [f'K.{l}' for l in knowledge_labels]
        
        if all_metrics and len(all_metrics) > 0:
            # Normalizar valores para el gráfico radar (0-1)
            max_val = max(all_metrics) if max(all_metrics) > 0 else 1
            normalized_metrics = [m/max_val for m in all_metrics]
            
            # Crear gráfico radar
            angles = np.linspace(0, 2*np.pi, len(all_labels), endpoint=False).tolist()
            normalized_metrics += normalized_metrics[:1]  # Cerrar el círculo
            angles += angles[:1]
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            ax.plot(angles, normalized_metrics, 'o-', linewidth=2, color='#2E86AB')
            ax.fill(angles, normalized_metrics, alpha=0.25, color='#2E86AB')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(all_labels, fontsize=10)
            ax.set_ylim(0, 1)
            ax.set_title('Comparación General de Todas las Métricas\n(Valores Normalizados)', 
                        fontsize=14, fontweight='bold', pad=30)
            ax.grid(True)
            
            plt.tight_layout()
            
            img_buffer5 = io.BytesIO()
            plt.savefig(img_buffer5, format='png', dpi=150, bbox_inches='tight')
            img_buffer5.seek(0)
            plt.close()
            
            img5 = Image(img_buffer5, width=7*inch, height=7*inch)
            story.append(img5)
    
    # Pie de página
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generado por Andru.ia - Análisis Visual Completo (Solo Gráficos)", styles['Italic']))
    
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

# FUNCIONES PRINCIPALES (sin cambios en las firmas para compatibilidad)
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
            return create_executive_pdf(debug_info, f"🎯 Análisis Nivel Académico {level} (Sin datos)")
    
    return create_executive_pdf(data, f"🎯 Análisis Nivel Académico {level}")

def generate_complete_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF completo con todas las columnas en orientación horizontal"""
    return create_complete_pdf(data, "📋 Reporte Completo - Análisis Integral")

def generate_charts_pdf(data, academic_level=None, summary_stats=None):
    """Genera PDF con SOLO gráficos y análisis visual (sin tablas)"""
    return create_pure_charts_pdf(data, "📈 Análisis Visual Completo - Solo Gráficos")