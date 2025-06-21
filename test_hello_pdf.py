"""
Prueba muy simple de ReportLab
"""

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    
    print("✅ Importaciones exitosas")
    
    # Crear PDF simple
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = [Paragraph("Hola Mundo PDF", styles['Title'])]
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    print(f"✅ PDF creado: {len(pdf_bytes)} bytes")
    
    # Guardar archivo
    with open('test_hello_world.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("✅ Archivo guardado: test_hello_world.pdf")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()