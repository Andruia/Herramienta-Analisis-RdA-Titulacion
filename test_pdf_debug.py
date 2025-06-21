"""
Script de diagnóstico para la funcionalidad PDF
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Prueba las importaciones necesarias"""
    print("🔍 Probando importaciones...")
    
    try:
        import reportlab
        print(f"✅ ReportLab: {reportlab.Version}")
    except ImportError as e:
        print(f"❌ ReportLab: {e}")
        return False
    
    try:
        from src.pdf_styles import AndruColors, AndruFonts
        print("✅ PDF Styles importado")
    except ImportError as e:
        print(f"❌ PDF Styles: {e}")
        return False
    
    try:
        from src.pdf_generator import generate_detailed_pdf
        print("✅ PDF Generator importado")
    except ImportError as e:
        print(f"❌ PDF Generator: {e}")
        return False
    
    return True

def create_sample_data():
    """Crea datos de muestra para prueba"""
    return {
        'results_data': [
            {
                'rda': 'Analizar conceptos básicos de programación',
                'bloom_level': 'Analizar',
                'bloom_score': 4,
                'verificability': 'Verificable',
                'correction': 'Correcto',
                'authenticity': 'Auténtico',
                'knowledge_dim': 'Conceptual'
            }
        ],
        'academic_level': 6,
        'summary_stats': {
            'total_rdas': 1,
            'bloom_distribution': {'Analizar': 1},
            'avg_bloom_score': 4.0
        }
    }

def test_pdf_generation():
    """Prueba la generación de PDF"""
    print("\n📄 Probando generación de PDF...")
    
    try:
        from src.pdf_generator import generate_detailed_pdf
        
        # Crear datos de muestra
        sample_data = create_sample_data()
        
        # Generar PDF
        pdf_bytes = generate_detailed_pdf(
            sample_data['results_data'],
            sample_data['academic_level'],
            sample_data['summary_stats']
        )
        
        if pdf_bytes:
            print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")
            
            # Guardar archivo de prueba
            filename = "test_pdf_output.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ PDF guardado como: {filename}")
            print(f"📁 Ubicación: {os.path.abspath(filename)}")
            return True
        else:
            print("❌ PDF generado está vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔧 DIAGNÓSTICO PDF ANDRU.IA")
    print("=" * 40)
    
    # Probar importaciones
    if not test_imports():
        print("\n❌ Falló la importación de módulos")
        return
    
    # Probar generación de PDF
    if test_pdf_generation():
        print("\n🎉 ¡Diagnóstico exitoso!")
        print("💡 El problema puede estar en la integración con Streamlit")
    else:
        print("\n❌ Falló la generación de PDF")
        print("💡 Revisa los errores mostrados arriba")

if __name__ == "__main__":
    main()