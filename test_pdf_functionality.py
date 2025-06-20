"""
Script de prueba para la funcionalidad de exportación PDF
Autor: Rubén Mauricio Tocaín Garzón
"""

import pandas as pd
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.pdf_generator import (
        generate_detailed_pdf, generate_executive_pdf, 
        generate_level_pdf, generate_complete_pdf
    )
    print("✅ Módulos PDF importados exitosamente")
except ImportError as e:
    print(f"❌ Error al importar módulos PDF: {e}")
    sys.exit(1)

def create_sample_data():
    """Crea datos de muestra para probar la generación PDF"""
    sample_data = {
        'RA': [1, 2, 3, 4, 5],
        'Nivel Académico': ['2', '4', '6', '8', '6'],
        'Verbo Principal': ['recordar', 'analizar', 'aplicar', 'crear', 'evaluar'],
        'Nivel Bloom': ['recordar', 'analizar', 'aplicar', 'crear', 'evaluar'],
        'Adecuación T.': ['✅ Apropiado', '✅ Apropiado', '⚠️ Pot. Bajo', '⬆️ Pot. Alto', '✅ Apropiado'],
        'Verificabilidad': ['85%', '92%', '78%', '88%', '95%'],
        'Corrección': [3, 2, 3, 3, 2],
        'Autenticidad': [4.2, 3.8, 4.5, 4.0, 4.3]
    }
    
    return pd.DataFrame(sample_data)

def test_pdf_generation():
    """Prueba la generación de todos los tipos de PDF"""
    print("🧪 Iniciando pruebas de generación PDF...")
    
    # Crear datos de muestra
    df = create_sample_data()
    print(f"📊 Datos de muestra creados: {len(df)} registros")
    
    # Probar PDF detallado
    try:
        print("📄 Probando PDF detallado...")
        pdf_data = generate_detailed_pdf(df)
        print(f"✅ PDF detallado generado: {len(pdf_data)} bytes")
        
        # Guardar archivo de prueba
        with open("test_detailed.pdf", "wb") as f:
            f.write(pdf_data)
        print("💾 Archivo test_detailed.pdf guardado")
        
    except Exception as e:
        print(f"❌ Error en PDF detallado: {e}")
    
    # Probar PDF ejecutivo
    try:
        print("📊 Probando PDF ejecutivo...")
        pdf_data = generate_executive_pdf(df)
        print(f"✅ PDF ejecutivo generado: {len(pdf_data)} bytes")
        
        # Guardar archivo de prueba
        with open("test_executive.pdf", "wb") as f:
            f.write(pdf_data)
        print("💾 Archivo test_executive.pdf guardado")
        
    except Exception as e:
        print(f"❌ Error en PDF ejecutivo: {e}")
    
    # Probar PDF por nivel
    try:
        print("🎯 Probando PDF por nivel (nivel 6)...")
        pdf_data = generate_level_pdf(df, '6')
        print(f"✅ PDF por nivel generado: {len(pdf_data)} bytes")
        
        # Guardar archivo de prueba
        with open("test_level_6.pdf", "wb") as f:
            f.write(pdf_data)
        print("💾 Archivo test_level_6.pdf guardado")
        
    except Exception as e:
        print(f"❌ Error en PDF por nivel: {e}")
    
    # Probar PDF completo
    try:
        print("📋 Probando PDF completo...")
        pdf_data = generate_complete_pdf(df)
        print(f"✅ PDF completo generado: {len(pdf_data)} bytes")
        
        # Guardar archivo de prueba
        with open("test_complete.pdf", "wb") as f:
            f.write(pdf_data)
        print("💾 Archivo test_complete.pdf guardado")
        
    except Exception as e:
        print(f"❌ Error en PDF completo: {e}")
    
    print("🎉 Pruebas de PDF completadas")

def test_styles():
    """Prueba la importación de estilos"""
    try:
        from src.pdf_styles import AndruColors, AndruFonts, get_andru_styles
        print("✅ Estilos Andru.ia importados correctamente")
        
        # Probar colores
        print(f"🎨 Color primario: {AndruColors.PRIMARY}")
        print(f"🎨 Color secundario: {AndruColors.SECONDARY}")
        
        # Probar fuentes
        print(f"🔤 Fuente principal: {AndruFonts.PRIMARY_FONT}")
        print(f"🔤 Tamaño título: {AndruFonts.TITLE_SIZE}")
        
        # Probar estilos
        styles = get_andru_styles()
        print(f"📝 Estilos disponibles: {len(styles.byName)} estilos")
        
    except Exception as e:
        print(f"❌ Error al probar estilos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema PDF Andru.ia")
    print("=" * 50)
    
    # Probar estilos
    test_styles()
    print()
    
    # Probar generación PDF
    test_pdf_generation()
    
    print("=" * 50)
    print("✅ Pruebas completadas. Revisa los archivos PDF generados.")
    print("📁 Archivos generados:")
    print("   - test_detailed.pdf")
    print("   - test_executive.pdf") 
    print("   - test_level_6.pdf")
    print("   - test_complete.pdf")