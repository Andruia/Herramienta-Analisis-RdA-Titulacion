"""
Prueba simple de generación PDF
"""

import sys
import os
sys.path.append('src')

def test_pdf_generation():
    """Prueba la generación de PDF con datos de muestra"""
    print("🔧 Probando generación de PDF...")
    
    try:
        # Importar las funciones
        from src.pdf_generator import generate_detailed_pdf
        
        # Datos de muestra
        sample_data = [
            {
                'rda': 'Analizar conceptos básicos de programación',
                'bloom_level': 'Analizar',
                'bloom_score': 4,
                'verificability': 'Verificable',
                'correction': 'Correcto',
                'authenticity': 'Auténtico',
                'knowledge_dim': 'Conceptual'
            }
        ]
        
        academic_level = 6
        summary_stats = {
            'total_rdas': 1,
            'bloom_distribution': {'Analizar': 1},
            'avg_bloom_score': 4.0
        }
        
        # Generar PDF
        print("📄 Generando PDF...")
        pdf_bytes = generate_detailed_pdf(sample_data, academic_level, summary_stats)
        
        if pdf_bytes and len(pdf_bytes) > 0:
            # Guardar archivo
            filename = "test_andru_pdf.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✅ PDF generado exitosamente!")
            print(f"📁 Archivo: {os.path.abspath(filename)}")
            print(f"📊 Tamaño: {len(pdf_bytes)} bytes")
            return True
        else:
            print("❌ PDF generado está vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 PRUEBA PDF ANDRU.IA")
    print("=" * 30)
    
    if test_pdf_generation():
        print("\n🎉 ¡Prueba exitosa!")
        print("💡 Los PDFs deberían funcionar en Streamlit")
    else:
        print("\n❌ Prueba fallida")
        print("💡 Revisa los errores mostrados")