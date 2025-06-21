"""
Generador de PDFs profesionales con branding Andru.ia
Autor: Rubén Mauricio Tocaín Garzón
"""

import pandas as pd
from datetime import datetime
from io import BytesIO
import logging

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Importar nuestros estilos personalizados
from .pdf_styles import (
    AndruColors, AndruFonts, AndruTableStyles, AndruPageConfig,
    get_andru_styles, get_status_color, get_bloom_color, AndruSymbols
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AndruPDFGenerator:
    """Generador principal de PDFs con branding Andru.ia"""
    
    def __init__(self):
        self.styles = get_andru_styles()
        self.page_width = A4[0]
        self.page_height = A4[1]
        
    def _create_header(self):
        """Crea el encabezado corporativo Andru.ia"""
        header_data = [
            [Paragraph("🤖 <b>Andru.ia</b> - Inteligencia Artificial para Educación", self.styles['AndruTitle'])],
            [Paragraph("Análisis Inteligente de Resultados de Aprendizaje", self.styles['AndruSubtitle'])],
            [Paragraph("Taxonomía de Bloom • Verificabilidad • Corrección • Autenticidad", self.styles['AndruBody'])],
            [Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", self.styles['AndruSmall'])]
        ]
        
        header_table = Table(header_data, colWidths=[self.page_width - 4*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), AndruColors.PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), AndruColors.WHITE),
            ('BACKGROUND', (0, 1), (-1, -1), AndruColors.NEUTRAL_LIGHT),
        ]))
        
        return header_table
    
    def _create_footer(self):
        """Crea el pie de página corporativo"""
        footer_data = [
            ["Generado por Andru.ia - Inteligencia Artificial para Educación Superior"],
            ["Herramienta de Análisis RdA v2.0"],
            ["Desarrollado por: Rubén Mauricio Tocaín Garzón"],
            ["Contacto: info@andru.ia"]
        ]
        
        footer_table = Table(footer_data, colWidths=[self.page_width - 4*cm])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), AndruFonts.PRIMARY_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), AndruFonts.FOOTER_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), AndruColors.NEUTRAL_DARK),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return footer_table
    
    def _create_metrics_summary(self, df):
        """Crea resumen de métricas clave"""
        total_ras = len(df)
        
        # Contar adecuación
        apropiados = len(df[df['Adecuación T.'].str.contains('Apropiado', na=False)])
        pot_bajo = len(df[df['Adecuación T.'].str.contains('Pot. Bajo', na=False)])
        pot_alto = len(df[df['Adecuación T.'].str.contains('Pot. Alto', na=False)])
        
        # Nivel Bloom predominante
        bloom_counts = df['Nivel Bloom'].value_counts()
        bloom_predominante = bloom_counts.index[0] if len(bloom_counts) > 0 else "N/A"
        
        # Verificabilidad promedio
        verificabilidad_nums = df['Verificabilidad'].str.replace('%', '').astype(float, errors='ignore')
        verificabilidad_prom = verificabilidad_nums.mean() if len(verificabilidad_nums) > 0 else 0
        
        metrics_data = [
            ["Métrica", "Valor", "Descripción"],
            [f"{AndruSymbols.TOTAL} Total RdAs", str(total_ras), "Resultados de Aprendizaje analizados"],
            [f"{AndruSymbols.APROPIADO} Apropiados", f"{apropiados} ({apropiados/total_ras*100:.1f}%)", "RdAs con adecuación apropiada"],
            [f"{AndruSymbols.POTENCIAL_BAJO} Pot. Bajo", f"{pot_bajo} ({pot_bajo/total_ras*100:.1f}%)", "RdAs con potencial bajo"],
            [f"{AndruSymbols.POTENCIAL_ALTO} Pot. Alto", f"{pot_alto} ({pot_alto/total_ras*100:.1f}%)", "RdAs con potencial alto"],
            [f"{AndruSymbols.BLOOM} Bloom Predominante", bloom_predominante.title(), "Nivel cognitivo más frecuente"],
            [f"{AndruSymbols.VERIFICABILIDAD} Verificabilidad", f"{verificabilidad_prom:.1f}%", "Promedio de verificabilidad"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[4*cm, 3*cm, 8*cm])
        metrics_table.setStyle(AndruTableStyles.get_alternating_rows_style(len(metrics_data)))
        
        return metrics_table
    
    def _create_detailed_table(self, df):
        """Crea tabla detallada de análisis"""
        # Preparar datos para la tabla
        table_data = [["RA", "Nivel", "Verbo", "Bloom", "Adecuación", "Verif.", "Corr.", "Aut."]]
        
        for _, row in df.iterrows():
            table_data.append([
                str(row['RA']),
                str(row['Nivel Académico']),
                str(row['Verbo Principal'])[:15] + "..." if len(str(row['Verbo Principal'])) > 15 else str(row['Verbo Principal']),
                str(row['Nivel Bloom']).title(),
                str(row['Adecuación T.']),
                str(row['Verificabilidad']),
                str(row['Corrección']),
                f"{row['Autenticidad']:.1f}" if pd.notna(row['Autenticidad']) else "N/A"
            ])
        
        # Crear tabla
        detailed_table = Table(table_data, colWidths=[1*cm, 1*cm, 3*cm, 2*cm, 2.5*cm, 1.5*cm, 1*cm, 1*cm])
        detailed_table.setStyle(AndruTableStyles.get_alternating_rows_style(len(table_data)))
        
        return detailed_table
    
    def _create_bloom_distribution(self, df):
        """Crea tabla de distribución de niveles Bloom"""
        bloom_counts = df['Nivel Bloom'].value_counts()
        total = len(df)
        
        bloom_data = [["Nivel Bloom", "Cantidad", "Porcentaje", "Descripción"]]
        
        bloom_descriptions = {
            'recordar': 'Recuperar información de la memoria',
            'comprender': 'Construir significado a partir de mensajes',
            'aplicar': 'Usar procedimientos en situaciones dadas',
            'analizar': 'Descomponer en partes y determinar relaciones',
            'evaluar': 'Hacer juicios basados en criterios',
            'crear': 'Reorganizar elementos en un patrón nuevo'
        }
        
        for nivel, count in bloom_counts.items():
            percentage = (count / total) * 100
            description = bloom_descriptions.get(nivel.lower(), "Descripción no disponible")
            bloom_data.append([
                nivel.title(),
                str(count),
                f"{percentage:.1f}%",
                description
            ])
        
        bloom_table = Table(bloom_data, colWidths=[2.5*cm, 2*cm, 2*cm, 8.5*cm])
        bloom_table.setStyle(AndruTableStyles.get_alternating_rows_style(len(bloom_data)))
        
        return bloom_table
    
    def _create_recommendations(self, df):
        """Crea sección de recomendaciones inteligentes"""
        recommendations = []
        
        # Análisis de adecuación
        total = len(df)
        apropiados = len(df[df['Adecuación T.'].str.contains('Apropiado', na=False)])
        pot_bajo = len(df[df['Adecuación T.'].str.contains('Pot. Bajo', na=False)])
        pot_alto = len(df[df['Adecuación T.'].str.contains('Pot. Alto', na=False)])
        
        if apropiados / total < 0.7:
            recommendations.append("• Revisar la formulación de RdAs para mejorar la adecuación taxonómica")
        
        if pot_bajo > 0:
            recommendations.append(f"• {pot_bajo} RdAs tienen potencial bajo - considerar elevar el nivel cognitivo")
        
        if pot_alto > 0:
            recommendations.append(f"• {pot_alto} RdAs tienen potencial alto - verificar si es apropiado para el nivel")
        
        # Análisis de diversidad Bloom
        bloom_diversity = len(df['Nivel Bloom'].unique())
        if bloom_diversity < 3:
            recommendations.append("• Considerar incorporar mayor diversidad de niveles cognitivos de Bloom")
        
        # Análisis de verificabilidad
        verificabilidad_nums = df['Verificabilidad'].str.replace('%', '').astype(float, errors='ignore')
        verificabilidad_prom = verificabilidad_nums.mean() if len(verificabilidad_nums) > 0 else 0
        
        if verificabilidad_prom < 80:
            recommendations.append("• Mejorar la verificabilidad usando verbos más específicos y medibles")
        
        if not recommendations:
            recommendations.append("• ¡Excelente! Los RdAs muestran una formulación adecuada")
        
        return recommendations
    
    def generate_detailed_pdf(self, df):
        """Genera PDF detallado con análisis completo"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=AndruPageConfig.MARGIN_RIGHT,
                leftMargin=AndruPageConfig.MARGIN_LEFT,
                topMargin=AndruPageConfig.MARGIN_TOP,
                bottomMargin=AndruPageConfig.MARGIN_BOTTOM
            )
            
            # Construir contenido
            story = []
            
            # Encabezado
            story.append(self._create_header())
            story.append(Spacer(1, 20))
            
            # Título del reporte
            story.append(Paragraph("📄 Reporte Detallado de Análisis", self.styles['AndruTitle']))
            story.append(Spacer(1, 15))
            
            # Resumen de métricas
            story.append(Paragraph("📊 Resumen de Métricas", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_metrics_summary(df))
            story.append(Spacer(1, 20))
            
            # Tabla detallada
            story.append(Paragraph("📋 Análisis Detallado por RdA", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_detailed_table(df))
            story.append(Spacer(1, 20))
            
            # Distribución Bloom
            story.append(Paragraph("🧠 Distribución de Niveles Bloom", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_bloom_distribution(df))
            story.append(Spacer(1, 20))
            
            # Recomendaciones
            story.append(Paragraph("💡 Recomendaciones Inteligentes", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            recommendations = self._create_recommendations(df)
            for rec in recommendations:
                story.append(Paragraph(rec, self.styles['AndruBody']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 30))
            story.append(self._create_footer())
            
            # Generar PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando PDF detallado: {e}")
            raise
    
    def generate_executive_pdf(self, df):
        """Genera PDF ejecutivo con resumen gerencial"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=AndruPageConfig.MARGIN_RIGHT,
                leftMargin=AndruPageConfig.MARGIN_LEFT,
                topMargin=AndruPageConfig.MARGIN_TOP,
                bottomMargin=AndruPageConfig.MARGIN_BOTTOM
            )
            
            story = []
            
            # Encabezado
            story.append(self._create_header())
            story.append(Spacer(1, 20))
            
            # Título del reporte
            story.append(Paragraph("📊 Reporte Ejecutivo", self.styles['AndruTitle']))
            story.append(Spacer(1, 15))
            
            # Resumen ejecutivo
            story.append(Paragraph("🎯 Resumen Ejecutivo", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            
            total = len(df)
            apropiados = len(df[df['Adecuación T.'].str.contains('Apropiado', na=False)])
            
            executive_summary = f"""
            Se analizaron <b>{total}</b> Resultados de Aprendizaje utilizando inteligencia artificial.
            El <b>{apropiados/total*100:.1f}%</b> de los RdAs muestran adecuación apropiada según la Taxonomía de Bloom.
            """
            
            story.append(Paragraph(executive_summary, self.styles['AndruBody']))
            story.append(Spacer(1, 15))
            
            # Métricas clave
            story.append(self._create_metrics_summary(df))
            story.append(Spacer(1, 20))
            
            # Distribución Bloom
            story.append(Paragraph("🧠 Distribución Cognitiva", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_bloom_distribution(df))
            story.append(Spacer(1, 20))
            
            # Recomendaciones estratégicas
            story.append(Paragraph("🚀 Recomendaciones Estratégicas", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            recommendations = self._create_recommendations(df)
            for rec in recommendations:
                story.append(Paragraph(rec, self.styles['AndruBody']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 30))
            story.append(self._create_footer())
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando PDF ejecutivo: {e}")
            raise
    
    def generate_level_pdf(self, df, level):
        """Genera PDF filtrado por nivel académico"""
        try:
            # Filtrar por nivel
            df_filtered = df[df['Nivel Académico'] == level].copy()
            
            if len(df_filtered) == 0:
                raise ValueError(f"No se encontraron RdAs para el nivel {level}")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=AndruPageConfig.MARGIN_RIGHT,
                leftMargin=AndruPageConfig.MARGIN_LEFT,
                topMargin=AndruPageConfig.MARGIN_TOP,
                bottomMargin=AndruPageConfig.MARGIN_BOTTOM
            )
            
            story = []
            
            # Encabezado
            story.append(self._create_header())
            story.append(Spacer(1, 20))
            
            # Título del reporte
            story.append(Paragraph(f"🎯 Análisis por Nivel Académico {level}", self.styles['AndruTitle']))
            story.append(Spacer(1, 15))
            
            # Contexto del nivel
            story.append(Paragraph(f"📚 Análisis Específico - Nivel {level}", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            
            context_text = f"Este reporte presenta el análisis específico de {len(df_filtered)} RdAs correspondientes al nivel académico {level}."
            story.append(Paragraph(context_text, self.styles['AndruBody']))
            story.append(Spacer(1, 15))
            
            # Métricas del nivel
            story.append(self._create_metrics_summary(df_filtered))
            story.append(Spacer(1, 20))
            
            # Tabla detallada del nivel
            story.append(Paragraph("📋 RdAs del Nivel", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_detailed_table(df_filtered))
            story.append(Spacer(1, 20))
            
            # Distribución Bloom del nivel
            story.append(Paragraph("🧠 Distribución Bloom del Nivel", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_bloom_distribution(df_filtered))
            story.append(Spacer(1, 20))
            
            # Recomendaciones específicas del nivel
            story.append(Paragraph(f"💡 Recomendaciones para Nivel {level}", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            recommendations = self._create_recommendations(df_filtered)
            for rec in recommendations:
                story.append(Paragraph(rec, self.styles['AndruBody']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 30))
            story.append(self._create_footer())
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando PDF por nivel: {e}")
            raise
    
    def generate_complete_pdf(self, df):
        """Genera PDF completo con todos los análisis"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=AndruPageConfig.MARGIN_RIGHT,
                leftMargin=AndruPageConfig.MARGIN_LEFT,
                topMargin=AndruPageConfig.MARGIN_TOP,
                bottomMargin=AndruPageConfig.MARGIN_BOTTOM
            )
            
            story = []
            
            # Encabezado
            story.append(self._create_header())
            story.append(Spacer(1, 20))
            
            # Título del reporte
            story.append(Paragraph("📋 Reporte Integral Completo", self.styles['AndruTitle']))
            story.append(Spacer(1, 15))
            
            # Resumen ejecutivo
            story.append(Paragraph("🎯 Resumen Ejecutivo", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            
            total = len(df)
            apropiados = len(df[df['Adecuación T.'].str.contains('Apropiado', na=False)])
            
            executive_summary = f"""
            <b>Análisis Integral de Resultados de Aprendizaje</b><br/><br/>
            Se realizó un análisis comprehensivo de <b>{total}</b> Resultados de Aprendizaje utilizando 
            técnicas avanzadas de Procesamiento de Lenguaje Natural e Inteligencia Artificial.<br/><br/>
            <b>Hallazgos Principales:</b><br/>
            • {apropiados/total*100:.1f}% de adecuación apropiada según Taxonomía de Bloom<br/>
            • Análisis multidimensional: Verificabilidad, Corrección y Autenticidad<br/>
            • Recomendaciones inteligentes para mejora continua
            """
            
            story.append(Paragraph(executive_summary, self.styles['AndruBody']))
            story.append(Spacer(1, 20))
            
            # Métricas generales
            story.append(Paragraph("📊 Métricas Generales", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_metrics_summary(df))
            story.append(PageBreak())
            
            # Análisis detallado
            story.append(Paragraph("📋 Análisis Detallado", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_detailed_table(df))
            story.append(Spacer(1, 20))
            
            # Distribución Bloom
            story.append(Paragraph("🧠 Análisis de Taxonomía de Bloom", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            story.append(self._create_bloom_distribution(df))
            story.append(Spacer(1, 20))
            
            # Análisis por nivel académico
            levels = df['Nivel Académico'].unique()
            for level in sorted(levels):
                df_level = df[df['Nivel Académico'] == level]
                story.append(Paragraph(f"📚 Análisis Nivel {level}", self.styles['AndruSubtitle']))
                story.append(Spacer(1, 10))
                
                level_summary = f"Nivel {level}: {len(df_level)} RdAs analizados"
                story.append(Paragraph(level_summary, self.styles['AndruBody']))
                story.append(Spacer(1, 10))
                
                story.append(self._create_detailed_table(df_level))
                story.append(Spacer(1, 15))
            
            # Recomendaciones finales
            story.append(Paragraph("🚀 Recomendaciones Integrales", self.styles['AndruSubtitle']))
            story.append(Spacer(1, 10))
            recommendations = self._create_recommendations(df)
            for rec in recommendations:
                story.append(Paragraph(rec, self.styles['AndruBody']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 30))
            story.append(self._create_footer())
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando PDF completo: {e}")
            raise

# ============================================================================
# FUNCIONES DE INTERFAZ PÚBLICA
# ============================================================================

def generate_detailed_pdf(df):
    """Función pública para generar PDF detallado"""
    generator = AndruPDFGenerator()
    return generator.generate_detailed_pdf(df)

def generate_executive_pdf(df):
    """Función pública para generar PDF ejecutivo"""
    generator = AndruPDFGenerator()
    return generator.generate_executive_pdf(df)

def generate_level_pdf(df, level):
    """Función pública para generar PDF por nivel"""
    generator = AndruPDFGenerator()
    return generator.generate_level_pdf(df, level)

def generate_complete_pdf(df):
    """Función pública para generar PDF completo"""
    generator = AndruPDFGenerator()
    return generator.generate_complete_pdf(df)