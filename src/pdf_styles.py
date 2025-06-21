"""
Estilos y configuración visual para PDFs con branding Andru.ia
Autor: Rubén Mauricio Tocaín Garzón
"""

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch, cm

# ============================================================================
# PALETA DE COLORES ANDRU.IA
# ============================================================================

class AndruColors:
    """Paleta de colores corporativos Andru.ia"""
    
    # Colores principales
    PRIMARY = HexColor('#2E86AB')      # Azul principal Andru.ia
    SECONDARY = HexColor('#A23B72')    # Magenta/Rosa corporativo
    ACCENT = HexColor('#F18F01')       # Naranja de acento
    SUCCESS = HexColor('#C73E1D')      # Rojo para destacar
    
    # Colores neutros
    NEUTRAL_LIGHT = HexColor('#F5F5F5')  # Gris claro
    NEUTRAL_DARK = HexColor('#2C3E50')   # Gris oscuro para texto
    WHITE = HexColor('#FFFFFF')
    BLACK = HexColor('#000000')
    
    # Colores para estados de análisis
    APROPIADO = HexColor('#28a745')      # Verde para apropiado
    POTENCIAL_BAJO = HexColor('#ffc107')  # Amarillo para pot. bajo
    POTENCIAL_ALTO = HexColor('#17a2b8')  # Azul claro para pot. alto
    ERROR = HexColor('#dc3545')          # Rojo para errores
    
    # Colores para gráficos
    CHART_COLORS = [
        HexColor('#2E86AB'),  # Azul principal
        HexColor('#A23B72'),  # Magenta
        HexColor('#F18F01'),  # Naranja
        HexColor('#C73E1D'),  # Rojo
        HexColor('#28a745'),  # Verde
        HexColor('#17a2b8'),  # Azul claro
        HexColor('#6f42c1'),  # Púrpura
        HexColor('#fd7e14'),  # Naranja claro
    ]

# ============================================================================
# CONFIGURACIÓN DE FUENTES
# ============================================================================

class AndruFonts:
    """Configuración de tipografía Andru.ia"""
    
    # Familias de fuentes
    PRIMARY_FONT = 'Helvetica'
    SECONDARY_FONT = 'Helvetica-Bold'
    MONO_FONT = 'Courier'
    
    # Tamaños de fuente
    TITLE_SIZE = 18
    SUBTITLE_SIZE = 16
    HEADER_SIZE = 14
    SUBHEADER_SIZE = 12
    BODY_SIZE = 10
    SMALL_SIZE = 8
    FOOTER_SIZE = 8
    
    # Configuraciones específicas
    FONTS = {
        'title': (SECONDARY_FONT, TITLE_SIZE),
        'subtitle': (SECONDARY_FONT, SUBTITLE_SIZE),
        'header': (SECONDARY_FONT, HEADER_SIZE),
        'subheader': (SECONDARY_FONT, SUBHEADER_SIZE),
        'body': (PRIMARY_FONT, BODY_SIZE),
        'body_bold': (SECONDARY_FONT, BODY_SIZE),
        'small': (PRIMARY_FONT, SMALL_SIZE),
        'footer': ('Helvetica-Oblique', FOOTER_SIZE),
        'mono': (MONO_FONT, BODY_SIZE)
    }

# ============================================================================
# ESTILOS DE PÁRRAFO
# ============================================================================

def get_andru_styles():
    """Obtiene los estilos de párrafo personalizados para Andru.ia"""
    
    styles = getSampleStyleSheet()
    
    # Estilo para título principal
    styles.add(ParagraphStyle(
        name='AndruTitle',
        parent=styles['Title'],
        fontName=AndruFonts.SECONDARY_FONT,
        fontSize=AndruFonts.TITLE_SIZE,
        textColor=AndruColors.PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=10
    ))
    
    # Estilo para subtítulos
    styles.add(ParagraphStyle(
        name='AndruSubtitle',
        parent=styles['Heading1'],
        fontName=AndruFonts.SECONDARY_FONT,
        fontSize=AndruFonts.SUBTITLE_SIZE,
        textColor=AndruColors.SECONDARY,
        alignment=TA_LEFT,
        spaceAfter=12,
        spaceBefore=12
    ))
    
    # Estilo para encabezados de sección
    styles.add(ParagraphStyle(
        name='AndruHeader',
        parent=styles['Heading2'],
        fontName=AndruFonts.SECONDARY_FONT,
        fontSize=AndruFonts.HEADER_SIZE,
        textColor=AndruColors.NEUTRAL_DARK,
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=8,
        borderWidth=0,
        borderColor=AndruColors.PRIMARY,
        borderPadding=5
    ))
    
    # Estilo para texto normal
    styles.add(ParagraphStyle(
        name='AndruBody',
        parent=styles['Normal'],
        fontName=AndruFonts.PRIMARY_FONT,
        fontSize=AndruFonts.BODY_SIZE,
        textColor=AndruColors.NEUTRAL_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        spaceBefore=0
    ))
    
    # Estilo para texto pequeño
    styles.add(ParagraphStyle(
        name='AndruSmall',
        parent=styles['Normal'],
        fontName=AndruFonts.PRIMARY_FONT,
        fontSize=AndruFonts.SMALL_SIZE,
        textColor=AndruColors.NEUTRAL_DARK,
        alignment=TA_LEFT,
        spaceAfter=4,
        spaceBefore=0
    ))
    
    # Estilo para pie de página
    styles.add(ParagraphStyle(
        name='AndruFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=AndruFonts.FOOTER_SIZE,
        textColor=AndruColors.NEUTRAL_DARK,
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0
    ))
    
    # Estilo para métricas destacadas
    styles.add(ParagraphStyle(
        name='AndruMetric',
        parent=styles['Normal'],
        fontName=AndruFonts.SECONDARY_FONT,
        fontSize=AndruFonts.SUBHEADER_SIZE,
        textColor=AndruColors.PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=8,
        spaceBefore=8
    ))
    
    # Estilo para texto de estado (Apropiado, Pot. Bajo, etc.)
    styles.add(ParagraphStyle(
        name='AndruStatus',
        parent=styles['Normal'],
        fontName=AndruFonts.SECONDARY_FONT,
        fontSize=AndruFonts.BODY_SIZE,
        alignment=TA_CENTER,
        spaceAfter=0,
        spaceBefore=0
    ))
    
    return styles

# ============================================================================
# CONFIGURACIÓN DE TABLAS
# ============================================================================

class AndruTableStyles:
    """Estilos para tablas con branding Andru.ia"""
    
    # Estilo base para tablas
    BASE_TABLE_STYLE = [
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), AndruColors.PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), AndruColors.WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), AndruFonts.SECONDARY_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), AndruFonts.SUBHEADER_SIZE),
        
        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), AndruFonts.PRIMARY_FONT),
        ('FONTSIZE', (0, 1), (-1, -1), AndruFonts.BODY_SIZE),
        ('TEXTCOLOR', (0, 1), (-1, -1), AndruColors.NEUTRAL_DARK),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, AndruColors.NEUTRAL_DARK),
        ('LINEBELOW', (0, 0), (-1, 0), 2, AndruColors.PRIMARY),
        
        # Espaciado
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    
    # Estilo para filas alternadas
    @staticmethod
    def get_alternating_rows_style(num_rows):
        """Genera estilo para filas alternadas"""
        style = AndruTableStyles.BASE_TABLE_STYLE.copy()
        
        # Agregar color alternado para filas
        for i in range(1, num_rows, 2):
            style.append(('BACKGROUND', (0, i), (-1, i), AndruColors.NEUTRAL_LIGHT))
        
        return style
    
    # Estilo para tabla de métricas
    METRICS_TABLE_STYLE = [
        ('BACKGROUND', (0, 0), (-1, -1), AndruColors.NEUTRAL_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, -1), AndruColors.NEUTRAL_DARK),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), AndruFonts.PRIMARY_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), AndruFonts.BODY_SIZE),
        ('GRID', (0, 0), (-1, -1), 1, AndruColors.NEUTRAL_DARK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

class AndruPageConfig:
    """Configuración de página para documentos Andru.ia"""
    
    # Márgenes
    MARGIN_TOP = 2.5 * cm
    MARGIN_BOTTOM = 2 * cm
    MARGIN_LEFT = 2 * cm
    MARGIN_RIGHT = 2 * cm
    
    # Espaciado
    HEADER_HEIGHT = 1.5 * cm
    FOOTER_HEIGHT = 1 * cm
    
    # Configuración de encabezado
    HEADER_CONFIG = {
        'height': HEADER_HEIGHT,
        'background_color': AndruColors.PRIMARY,
        'text_color': AndruColors.WHITE,
        'font': AndruFonts.FONTS['header']
    }
    
    # Configuración de pie de página
    FOOTER_CONFIG = {
        'height': FOOTER_HEIGHT,
        'background_color': AndruColors.WHITE,
        'text_color': AndruColors.NEUTRAL_DARK,
        'font': AndruFonts.FONTS['footer']
    }

# ============================================================================
# UTILIDADES DE COLOR
# ============================================================================

def get_status_color(status):
    """Obtiene el color según el estado de adecuación"""
    status_colors = {
        'apropiado': AndruColors.APROPIADO,
        'potencialmente_bajo': AndruColors.POTENCIAL_BAJO,
        'potencialmente_alto': AndruColors.POTENCIAL_ALTO,
        'error': AndruColors.ERROR
    }
    return status_colors.get(status.lower(), AndruColors.NEUTRAL_DARK)

def get_bloom_color(bloom_level):
    """Obtiene color específico para cada nivel de Bloom"""
    bloom_colors = {
        'recordar': HexColor('#FF6B6B'),      # Rojo suave
        'comprender': HexColor('#4ECDC4'),    # Verde azulado
        'aplicar': HexColor('#45B7D1'),       # Azul
        'analizar': HexColor('#96CEB4'),      # Verde claro
        'evaluar': HexColor('#FFEAA7'),       # Amarillo suave
        'crear': HexColor('#DDA0DD')          # Púrpura suave
    }
    return bloom_colors.get(bloom_level.lower(), AndruColors.NEUTRAL_DARK)

# ============================================================================
# CONFIGURACIÓN DE ICONOS Y SÍMBOLOS
# ============================================================================

class AndruSymbols:
    """Símbolos y iconos para usar en los reportes"""
    
    # Símbolos de estado
    APROPIADO = "✅"
    POTENCIAL_BAJO = "⚠️"
    POTENCIAL_ALTO = "⬆️"
    ERROR = "❌"
    
    # Símbolos de métricas
    TOTAL = "📊"
    BLOOM = "🧠"
    VERIFICABILIDAD = "🔍"
    CORRECCION = "✏️"
    AUTENTICIDAD = "🎯"