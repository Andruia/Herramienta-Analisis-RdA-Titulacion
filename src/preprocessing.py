import re

def clean_text(text):
    """
    Realiza una limpieza básica del texto: minúsculas y elimina espacios extra.
    """
    if not isinstance(text, str):
        return "" # Devuelve cadena vacía si no es texto
    text = text.lower() # Convertir a minúsculas
    text = re.sub(r'\s+', ' ', text).strip() # Eliminar espacios múltiples y al inicio/final
    return text

# Ejemplo de uso
if __name__ == '__main__':
    test_text = "  Este es   un EJEMPLO de   Texto.   "
    cleaned = clean_text(test_text)
    print(f"Original: '{test_text}'")
    print(f"Limpio: '{cleaned}'")
    