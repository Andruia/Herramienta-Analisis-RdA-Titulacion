"""
Generador de PDFs profesionales con branding Andru.ia
Módulo principal para exportación de análisis RdA
Autor: Rubén Mauricio Tocaín Garzón
"""

import io
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import Color

# Importar estilos personalizados
from .pdf_styles import (
    AndruColors, AndruFonts, AndruTableStyles, AndruPageConfig,
    AndruSymbols, get_andru_styles, get_status_color, get_bloom_color
)

# ============================================================================
# CLASE PRINCIPAL DEL GENERADOR PDF
# ============================================================================

class AndruPDFGenerator:
    """Generador principal de PDFs con branding Andru.ia"""
    
    def __init__(self):
        self.styles = get_andru_styles()
        self.page_size = A4
        self.margins = {
            'top': AndruPageConfig.MARGIN_TOP,
            'bottom': AndruPageConfig.MARGIN_BOTTOM,
            'left': AndruPageConfig.MARGIN_LEFT,
            'right': AndruPageConfig.MARGIN_RIGHT
        }
    
    def create_header(self, title: str, subtitle: str = "") -> List:
        """Crea el encabezado profesional Andru.ia"""
        elements = []
        
        # Título principal con branding
        header_text = f"""
        <para align="center">
            <font name="Helvetica-Bold" size="18" color="#2E86AB">
                🤖 Andru.ia - Inteligencia Artificial para Educación
            </font>
        </para>
        """
        elements.append(Paragraph(header_text, self.styles['AndruTitle']))
        
        # Subtítulo del reporte
        if subtitle:
            subtitle_text = f"""
            <para align="center">
                <font name="Helvetica-Bold" size="14" color="#A23B72">
                    {subtitle}
                </font>
            </para>
            """
            elements.append(Paragraph(subtitle_text, self.styles['AndruSubtitle']))
        
        # Línea separadora
        elements.append(Spacer(1, 0.3*inch))
        
        # Información del reporte
        info_text = f"""
        <para align="center">
            <font name="Helvetica" size="10" color="#2C3E50">
                Análisis Inteligente de Resultados de Aprendizaje<br/>
                Taxonomía de Bloom • Verificabilidad • Corrección • Autenticidad<br/>
                Generado el: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}
            </font>
        </para>
        """
        elements.append(Paragraph(info_text, self.styles['AndruBody']))
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def create_footer(self) -> str:
        """Crea el pie de página profesional"""
        return f"""
        <para align="center">
            <font name="Helvetica-Oblique" size="8" color="#2C3E50">
                Generado por Andru.ia - Inteligencia Artificial para Educación Superior<br/>
                Herramienta de Análisis RdA v2.0 | Desarrollado por: Rubén Mauricio Tocaín Garzón<br/>
                Contacto: info@andru.ia
            </font>
        </para>
        """
    
    def create_metrics_summary(self, df: pd.DataFrame) -> List:
        """Crea el resumen de métricas clave"""
        elements = []
        
        # Título de la sección
        elements.append(Paragraph("📊 MÉTRICAS CLAVE DEL ANÁLISIS", self.styles['AndruHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Calcular métricas
        total_rdas = len(df)
        apropiados = len(df[df['Adecuación T.'].str.contains('Apropiado', na=False)])
        pot_bajos = len(df[df['Adecuación T.'].str.contains('Pot. Bajo', na=False)])
        pot_altos = len(df[df['Adecuación T.'].str.contains('Pot. Alto', na=False)])
        
        # Verificabilidad promedio
        if 'Verificabilidad' in df.columns:
            verif_promedio = df['Verificabilidad'].str.replace('%', '').astype(float).mean()
        else:
            verif_promedio = 0
        
        # Nivel Bloom más frecuente
        bloom_mas_frecuente = df['Nivel Bloom'].mode().iloc[0] if not df['Nivel Bloom'].empty else "N/A"
        
        # Crear tabla de métricas
        metrics_data = [
            [f"{AndruSymbols.TOTAL} Total de RdAs Analizados:", f"{total_rdas}"],
            [f"{AndruSymbols.APROPIADO} RdAs Apropiados:", f"{apropiados} ({apropiados/total_rdas*100:.1f}%)"],
            [f"{AndruSymbols.POTENCIAL_BAJO} RdAs Potencialmente Bajos:", f"{pot_bajos} ({pot_bajos/total_rdas*100:.1f}%)"],
            [f"{AndruSymbols.POTENCIAL_ALTO} RdAs Potencialmente Altos:", f"{pot_altos} ({pot_altos/total_rdas*100:.1f}%)"],
            [f"{AndruSymbols.NIVEL} Nivel Bloom Predominante:", f"{bloom_mas_frecuente}"],
            [f"{AndruSymbols.VERIFICABILIDAD} Verificabilidad Promedio:", f"{verif_promedio:.1f}%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[4*inch, 2*inch])
        metrics_table.setStyle(AndruTableStyles.METRICS_TABLE_STYLE)
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def create_detailed_table(self, df: pd.DataFrame) -> List:
        """Crea la tabla detallada de análisis"""
        elements = []
        
        # Título de la sección
        elements.append(Paragraph("📋 ANÁLISIS DETALLADO POR RdA", self.styles['AndruHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Preparar datos de la tabla
        # Seleccionar columnas principales
        columns_to_include = [
            'RA', 'Nivel Académico', 'Verbo Principal', 'Nivel Bloom', 
            'Adecuación T.', 'Verificabilidad', 'Corrección', 'Autenticidad'
        ]
        
        # Filtrar columnas que existen en el DataFrame
        available_columns = [col for col in columns_to_include if col in df.columns]
        
        if not available_columns:
            elements.append(Paragraph("No hay datos disponibles para mostrar.", self.styles['AndruBody']))
            return elements
        
        # Crear encabezados de tabla
        headers = available_columns
        
        # Preparar datos
        table_data = [headers]
        
        for _, row in df.iterrows():
            row_data = []
            for col in available_columns:
                value = str(row[col]) if pd.notna(row[col]) else "N/A"
                
                # Formatear valores especiales
                if col == 'Adecuación T.':
                    if 'Apropiado' in value:
                        value = f"{AndruSymbols.APROPIADO} {value}"
                    elif 'Pot. Bajo' in value:
                        value = f"{AndruSymbols.POTENCIAL_BAJO} {value}"
                    elif 'Pot. Alto' in value:
                        value = f"{AndruSymbols.POTENCIAL_ALTO} {value}"
                
                row_data.append(value)
            
            table_data.append(row_data)
        
        # Crear tabla
        # Calcular anchos de columna dinámicamente
        num_cols = len(available_columns)
        col_width = 6.5 * inch / num_cols
        col_widths = [col_width] * num_cols
        
        detailed_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Aplicar estilo con filas alternadas
        table_style = AndruTableStyles.get_alternating_rows_style(len(table_data))
        detailed_table.setStyle(table_style)
        
        elements.append(detailed_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def create_bloom_distribution_chart(self, df: pd.DataFrame) -> List:
        """Crea gráfico de distribución de niveles Bloom"""
        elements = []
        
        # Título de la sección
        elements.append(Paragraph("📈 DISTRIBUCIÓN DE NIVELES BLOOM", self.styles['AndruHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        if 'Nivel Bloom' not in df.columns or df['Nivel Bloom'].empty:
            elements.append(Paragraph("No hay datos de niveles Bloom disponibles.", self.styles['AndruBody']))
            return elements
        
        # Contar frecuencias
        bloom_counts = df['Nivel Bloom'].value_counts()
        
        # Crear tabla de distribución
        distribution_data = [['Nivel Bloom', 'Frecuencia', 'Porcentaje']]
        
        for bloom_level, count in bloom_counts.items():
            percentage = (count / len(df)) * 100
            symbol = AndruSymbols.BLOOM_SYMBOLS.get(bloom_level.lower(), "📊")
            distribution_data.append([
                f"{symbol} {bloom_level.title()}",
                str(count),
                f"{percentage:.1f}%"
            ])
        
        distribution_table = Table(distribution_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        distribution_table.setStyle(AndruTableStyles.get_alternating_rows_style(len(distribution_data)))
        
        elements.append(distribution_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def create_recommendations_section(self, df: pd.DataFrame) -> List:
        """Crea sección de recomendaciones inteligentes"""
        elements = []
        
        # Título de la sección
        elements.append(Paragraph("💡 RECOMENDACIONES INTELIGENTES", self.styles['AndruHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        recommendations = []
        
        # Analizar patrones y generar recomendaciones
        if 'Adecuación T.' in df.columns:
            pot_bajos = len(df[df['Adecuación T.'].str.contains('Pot. Bajo', na=False)])
            pot_altos = len(df[df['Adecuación T.'].str.contains('Pot. Alto', na=False)])
            
            if pot_bajos > 0:
                recommendations.append(
                    f"• Se identificaron {pot_bajos} RdAs con nivel potencialmente bajo. "
                    "Considere revisar la complejidad de estos objetivos para el nivel académico."
                )
            
            if pot_altos > 0:
                recommendations.append(
                    f"• Se encontraron {pot_altos} RdAs con nivel potencialmente alto. "
                    "Estos objetivos podrían ser muy ambiciosos para el nivel actual."
                )
        
        # Recomendaciones sobre verificabilidad
        if 'Verificabilidad' in df.columns:
            verif_baja = len(df[df['Verificabilidad'].str.replace('%', '').astype(float) < 70])
            if verif_baja > 0:
                recommendations.append(
                    f"• {verif_baja} RdAs tienen baja verificabilidad (<70%). "
                    "Considere usar verbos más específicos y medibles."
                )
        
        # Recomendaciones sobre distribución de Bloom
        if 'Nivel Bloom' in df.columns:
            bloom_counts = df['Nivel Bloom'].value_counts()
            if len(bloom_counts) < 3:
                recommendations.append(
                    "• La distribución de niveles Bloom es limitada. "
                    "Considere incorporar una mayor variedad de niveles cognitivos."
                )
        
        # Recomendaciones generales
        recommendations.extend([
            "• Revise que todos los RdAs estén alineados con los objetivos del programa académico.",
            "• Asegúrese de que los verbos utilizados sean apropiados para el nivel de formación.",
            "• Considere la progresión pedagógica entre diferentes niveles académicos.",
            "• Valide que los RdAs sean medibles y evaluables de manera objetiva."
        ])
        
        # Crear párrafos de recomendaciones
        for recommendation in recommendations:
            elements.append(Paragraph(recommendation, self.styles['AndruBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements

# ============================================================================
# FUNCIONES DE GENERACIÓN ESPECÍFICAS
# ============================================================================

def generate_detailed_pdf(df: pd.DataFrame) -> bytes:
    """Genera PDF con análisis detallado completo"""
    buffer = io.BytesIO()
    
    # Crear documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=AndruPageConfig.MARGIN_TOP,
        bottomMargin=AndruPageConfig.MARGIN_BOTTOM,
        leftMargin=AndruPageConfig.MARGIN_LEFT,
        rightMargin=AndruPageConfig.MARGIN_RIGHT
    )
    
    # Crear generador
    generator = AndruPDFGenerator()
    
    # Construir contenido
    story = []
    
    # Encabezado
    story.extend(generator.create_header(
        "REPORTE DETALLADO DE ANÁLISIS RdA",
        "Análisis Completo por Resultado de Aprendizaje"
    ))
    
    # Métricas resumen
    story.extend(generator.create_metrics_summary(df))
    
    # Tabla detallada
    story.extend(generator.create_detailed_table(df))
    
    # Distribución de Bloom
    story.extend(generator.create_bloom_distribution_chart(df))
    
    # Salto de página
    story.append(PageBreak())
    
    # Recomendaciones
    story.extend(generator.create_recommendations_section(df))
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(generator.create_footer(), generator.styles['AndruFooter']))
    
    # Construir PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()

def generate_executive_pdf(df: pd.DataFrame) -> bytes:
    """Genera PDF ejecutivo con resumen gerencial"""
    buffer = io.BytesIO()
    
    # Crear documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=AndruPageConfig.MARGIN_TOP,
        bottomMargin=AndruPageConfig.MARGIN_BOTTOM,
        leftMargin=AndruPageConfig.MARGIN_LEFT,
        rightMargin=AndruPageConfig.MARGIN_RIGHT
    )
    
    # Crear generador
    generator = AndruPDFGenerator()
    
    # Construir contenido
    story = []
    
    # Encabezado
    story.extend(generator.create_header(
        "REPORTE EJECUTIVO DE ANÁLISIS RdA",
        "Resumen Gerencial y Métricas Clave"
    ))
    
    # Métricas resumen
    story.extend(generator.create_metrics_summary(df))
    
    # Distribución de Bloom
    story.extend(generator.create_bloom_distribution_chart(df))
    
    # Recomendaciones
    story.extend(generator.create_recommendations_section(df))
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(generator.create_footer(), generator.styles['AndruFooter']))
    
    # Construir PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()

def generate_level_pdf(df: pd.DataFrame, academic_level: str) -> bytes:
    """Genera PDF filtrado por nivel académico específico"""
    # Filtrar datos por nivel
    filtered_df = df[df['Nivel Académico'].astype(str) == str(academic_level)]
    
    if filtered_df.empty:
        # Si no hay datos, crear PDF con mensaje
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        generator = AndruPDFGenerator()
        
        story = []
        story.extend(generator.create_header(
            f"REPORTE NIVEL ACADÉMICO {academic_level}",
            "No se encontraron datos para este nivel"
        ))
        story.append(Paragraph(
            f"No se encontraron Resultados de Aprendizaje para el nivel académico {academic_level}.",
            generator.styles['AndruBody']
        ))
        story.append(Paragraph(generator.create_footer(), generator.styles['AndruFooter']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    # Generar PDF normal con datos filtrados
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=AndruPageConfig.MARGIN_TOP,
        bottomMargin=AndruPageConfig.MARGIN_BOTTOM,
        leftMargin=AndruPageConfig.MARGIN_LEFT,
        rightMargin=AndruPageConfig.MARGIN_RIGHT
    )
    
    generator = AndruPDFGenerator()
    
    story = []
    
    # Encabezado específico del nivel
    story.extend(generator.create_header(
        f"REPORTE NIVEL ACADÉMICO {academic_level}",
        f"Análisis Específico para Nivel {academic_level}"
    ))
    
    # Métricas del nivel
    story.extend(generator.create_metrics_summary(filtered_df))
    
    # Tabla detallada del nivel
    story.extend(generator.create_detailed_table(filtered_df))
    
    # Distribución de Bloom del nivel
    story.extend(generator.create_bloom_distribution_chart(filtered_df))
    
    # Recomendaciones específicas del nivel
    story.extend(generator.create_recommendations_section(filtered_df))
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(generator.create_footer(), generator.styles['AndruFooter']))
    
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()

def generate_complete_pdf(df: pd.DataFrame) -> bytes:
    """Genera PDF completo con todos los análisis"""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=AndruPageConfig.MARGIN_TOP,
        bottomMargin=AndruPageConfig.MARGIN_BOTTOM,
        leftMargin=AndruPageConfig.MARGIN_LEFT,
        rightMargin=AndruPageConfig.MARGIN_RIGHT
    )
    
    generator = AndruPDFGenerator()
    
    story = []
    
    # Encabezado
    story.extend(generator.create_header(
        "REPORTE COMPLETO DE ANÁLISIS RdA",
        "Análisis Integral y Comprensivo"
    ))
    
    # Resumen ejecutivo
    story.extend(generator.create_metrics_summary(df))
    
    # Salto de página
    story.append(PageBreak())
    
    # Análisis detallado
    story.extend(generator.create_detailed_table(df))
    
    # Salto de página
    story.append(PageBreak())
    
    # Distribución y gráficos
    story.extend(generator.create_bloom_distribution_chart(df))
    
    # Recomendaciones
    story.extend(generator.create_recommendations_section(df))
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(generator.create_footer(), generator.styles['AndruFooter']))
    
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()