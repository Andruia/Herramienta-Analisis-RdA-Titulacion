# Herramienta de Análisis de Resultados de Aprendizaje (RdA) para Caso Práctico de Titulación de Maestría

Herramienta inteligente desarrollada como parte del Trabajo de Titulación de Maestría
para el análisis y evaluación de Resultados de Aprendizaje (RdA) 
según la Taxonomía de Bloom (dimensión cognitiva), Verificabilidad, Corrección y Autenticidad, 
utilizando técnicas de Procesamiento de Lenguaje Natural (NLP) y presentada a través 
de una aplicación web con Streamlit.

**Autor:** Rubén Mauricio Tocaín Garzón

**Programa:** Maestría en Inteligencia Artificial Aplicada

**Universidad:** Universidad Hemisferios

**Fecha:** Mayo 2025

## Descripción General

Este proyecto presenta un prototipo funcional de una herramienta de software, implementada como 
una aplicación web con Streamlit, diseñada para asistir a docentes y diseñadores curriculares en 
la formulación y refinamiento de Resultados de Aprendizaje.
La herramienta permite al usuario ingresar un RdA, el cual es analizado para proporcionar una evaluación
basada en criterios pedagógicos y lingüísticos predefinidos, identificando fortalezas y áreas de mejora 
de forma interactiva.

El informe completo de este Trabajo de Titulación, que detalla la fundamentación teórica, la metodología,
el desarrollo, los resultados y las conclusiones, puede ser consultado según el documento entregado.

## Características Principales

*   Análisis de RdA según la **Taxonomía de Bloom (Dimensión Cognitiva)**: Identifica el nivel cognitivo al que apunta el RdA.
*   Evaluación de la **Verificabilidad**: Determina si el RdA está formulado de manera que su logro pueda ser evidenciado.
*   Análisis de la **Corrección Lingüística y Estructural**: Verifica aspectos gramaticales y de claridad en la redacción.
*   Evaluación de la **Autenticidad**: Considera la relevancia y el contexto del RdA.
*   **Interfaz Web Interactiva (Streamlit)**: Facilita la entrada de RdA y la visualización clara de los resultados del análisis.
*   Capacidad para descargar en formato Excel (.xlsx) a manera de tablas independientes el analisis de cada criterio, 
    permitiendo una revisión detallada y la posibilidad de compartir los resultados con otros interesados.
## Estructura del Repositorio

*   `/` (Raíz del proyecto):
    *   `requirements.txt`: Listado de dependencias de Python (incluyendo Streamlit).
    *   `README.md`: Este archivo.
    *   `.gitignore`: Especifica archivos y directorios ignorados por Git.
*   `/src/`: Contiene el código fuente de la aplicación.
    *   `app.py`: Script principal de la aplicación Streamlit.
    *   `authenticity_analyzer.py`: Módulo para el análisis de autenticidad.
    *   `correction_analyzer.py`: Módulo para el análisis de corrección.
    *   `verificability_analyzer.py`: Módulo para el análisis de verificabilidad.
    *   `bloom_analyzer.py`: Módulo para el análisis según la Taxonomía de Anderson (2001).
    *   `[otros_modulos_o_utilidades.py]`: Cualquier otro script de apoyo o utilidades.
*   `/data/` - Contiene archivos de entrada/salida usados en los análisis.  
*   `/docs/` - Documentación adicional sobre la arquitectura y funcionalidades.
    *   `[diagrama_arquitectura.png]`: [Descripción].

## Requisitos Previos

*   Python 3.12 (se recomienda 3.8 - 3.11, verificar compatibilidad con Streamlit y otras librerías)
*   pip (manejador de paquetes de Python)
*   Un navegador web moderno (para interactuar con la aplicación Streamlit)

## Instalación

1.  **Clonar el repositorio (recomendado):**
    ```bash
    git clone https://github.com/Andruia/Herramienta-Analisis-RdA-Titulacion.git
    cd Herramienta-Analisis-RdA-Titulacion
    ```
    Alternativamente, puede descargar el código como un archivo ZIP desde GitHub y descomprimirlo.

2.  **Crear y activar un entorno virtual (altamente recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    .\venv_py312\Scripts\activate
    # En macOS/Linux
    source venv_py312/bin/activate
    ```

3.  **Instalar las dependencias:**
    Asegúrese de que su archivo `requirements.txt` incluya `streamlit` y todas las demás librerías necesarias (`spacy`, `nltk`, `pandas`,etc.).
    ```bash
    pip install -r requirements.txt
    ```
   
    ```bash
    python -m spacy download es_core_news_sm 
    # ( modelo específico que se utilizó en la aplicación)
    ```

## Uso de la Herramienta

1.  **Navegar a la raíz del proyecto:**
    Asegúrese de estar en la carpeta principal del repositorio (donde se encuentra la carpeta `src/`).
    ```bash
    cd Herramienta-Analisis-RdA-Titulacion 
    # (Si no está ya allí)
    ```

2.  **Ejecutar la aplicación Streamlit:**
    ```bash
    streamlit run src/app.py
    ```

3.  **Interactuar con la aplicación:**
    *   Una vez ejecutado el comando anterior, Streamlit debería abrir automáticamente
     una nueva pestaña en su navegador web predeterminado, mostrando la interfaz de la aplicación. 
     Si no se abre automáticamente, la terminal le proporcionará una URL local (generalmente `http://localhost:8501`) 
     que puede copiar y pegar en su navegador.
    *   Siga las instrucciones en pantalla dentro de la aplicación para ingresar un 
    Resultado de Aprendizaje en el área de texto designada, o cargue un archivo .xlsx con RdA.
    *   Asegúrese de que el RdA esté redactado en español, ya que la aplicación está configurada para analizar textos en este idioma.
    *   Presione el botón de "Analizar".
    *   Los resultados del análisis se mostrarán en la interfaz de la aplicación.

## Ejemplo de RdA para Pruebas

Puede utilizar los siguientes RdA para una prueba rápida dentro de la aplicación:
*   Identificar las partes de una célula.
*   El alumno comprenderá los principios de la termodinámica para aplicarlos en la resolución de problemas complejos de ingeniería.
*   Desarrollar un plan de negocios sostenible.
*   Analizar críticamente las teorías de la evolución para evaluar su impacto en la biología moderna.
*   Crear un proyecto de investigación que demuestre la aplicación de técnicas avanzadas de programación.
*   Aplicar técnicas de procesamiento de lenguaje natural para analizar textos académicos.

## Contribución y Contacto

Este proyecto fue desarrollado por Rubén M. Tocaín G.

Para cualquier consulta o sugerencia, puede contactar a rtocain@gmail.com
## 📢 Notas Finales
Este proyecto es parte del trabajo de titulación de maestría, desarrollado con enfoque en inteligencia artificial aplicada a la educación. 