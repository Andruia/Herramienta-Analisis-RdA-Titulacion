"""
Prueba simple de ReportLab
"""

try:
    import reportlab
    print("✅ ReportLab importado correctamente")
    print(f"📦 Versión: {reportlab.Version}")
    
    from reportlab.lib.colors import HexColor
    print("✅ Colores importados")
    
    from reportlab.platypus import SimpleDocTemplate
    print("✅ SimpleDocTemplate importado")
    
    print("🎉 ¡ReportLab está funcionando correctamente!")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("💡 Instala ReportLab con: pip install reportlab")
    
except Exception as e:
    print(f"⚠️ Error inesperado: {e}")