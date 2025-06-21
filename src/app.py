import streamlit as st
import pandas as pd
import os
import sys
import logging
import io
from io import StringIO

# <<< MOVIDO AQUÍ >>> Debe ser el primer comando de Streamlit
st.set_page_config(layout="wide")

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Añadir el directorio raíz del proyecto al sys.path ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# ---------------------------------------------------------

# Importar desde nuestros módulos en src
try:
    from bloom_analyzer import analyze_bloom_level, check_appropriateness
    from src.nlp_utils import load_spacy_model
    from verificability_analyzer import check_verificability
    from correction_analyzer import check_correction
    from authenticity_analyzer import check_authenticity, PROFESSIONAL_KEYWORDS
    # <<< AÑADIDO >>> Importar la nueva función de dimensión del conocimiento
    from src.knowledge_analyzer import check_knowledge_dimension
    # <<< AÑADIDO >>> Importar módulo de generación PDF
    from src.pdf_generator_simple import (
        generate_executive_pdf, generate_level_pdf,
        generate_complete_pdf, generate_charts_pdf
    )
except ImportError as e:
    st.error(f"Error al importar módulos: {e}")
    st.error(f"Asegúrate de que los archivos .py necesarios estén en la carpeta 'src' y que ejecutas Streamlit desde la carpeta raíz del proyecto: {PROJECT_ROOT}")
    st.stop()

# Mapeo de Nivel de Bloom a Número
LEVEL_TO_NUMBER = {
    'recordar': 1, 'comprender': 2, 'aplicar': 3,
    'analizar': 4, 'evaluar': 5, 'crear': 6
}
# <<< AÑADIDO >>> Mapeo para Dimensión Conocimiento (para tooltips)
KNOWLEDGE_SCORE_DESC = {
    1: "Bajo", 2: "Medio", 3: "Alto"
}


# --- Carga de Recursos con Caché de Streamlit ---
@st.cache_resource
def cached_load_spacy_model():
    logging.info("Intentando cargar modelo spaCy (cache)...")
    model = load_spacy_model()
    if model: logging.info("Modelo spaCy cargado exitosamente (cache).")
    else: logging.error("Fallo al cargar modelo spaCy (cache).")
    return model

# --- Carga inicial de recursos ---
nlp_model = cached_load_spacy_model()

if not nlp_model:
    st.error("Error crítico: No se pudo cargar el modelo NLP. La aplicación no puede continuar.")
    st.stop()
else:
    st.success("Recursos NLP cargados correctamente.")
    logging.info("Recursos NLP cargados correctamente en app.py.")

# --- Interfaz de Usuario ---
st.title("Analizador de Resultados de Aprendizaje (RdA)")
st.markdown("Análisis basado en Taxonomía de Bloom Revisada y Criterios de Calidad")

# --- Opciones en la Barra Lateral ---
st.sidebar.header("Opciones de Análisis")

# Selector global, principalmente para "Pegar Texto"
global_academic_level = st.sidebar.selectbox(
    "Nivel Académico (para 'Pegar Texto'):", ('2', '4', '6', '8'), index=0
)
st.sidebar.info(f"Nivel Académico Global seleccionado: **{global_academic_level}** (Usado si pega texto o archivo .txt)")

# Texto informativo sobre niveles Bloom esperados (basado en selector global)
expected_bloom_levels_text = ""
if global_academic_level == '2':
    expected_bloom_levels_text = "Nivel 2: Se esperan niveles Bloom **1 (Recordar) a 2 (Comprender)** como apropiados."
elif global_academic_level == '4':
    expected_bloom_levels_text = "Nivel 4: Se esperan niveles Bloom **2 (Comprender) a 4 (Analizar)** como apropiados."
elif global_academic_level == '6':
    expected_bloom_levels_text = "Nivel 6: Se esperan niveles Bloom **1 (Recordar) a 3 (Aplicar)** como apropiados."
elif global_academic_level == '8':
    expected_bloom_levels_text = "Nivel 8: Se esperan niveles Bloom **3 (Aplicar) a 6 (Crear)** como apropiados."
if expected_bloom_levels_text:
    st.sidebar.markdown(f"ℹ️ *{expected_bloom_levels_text}*")

st.sidebar.divider() # Separador visual

# Información adicional sobre progresión pedagógica
with st.sidebar.expander("📚 Progresión Pedagógica por Niveles"):
    st.markdown("""
    **Nivel 2 (Fundamentos):**
    - Enfoque en construcción de bases conceptuales
    - Apropiados: Recordar, Comprender

    **Nivel 4 (Desarrollo):**
    - Desarrollo de habilidades de aplicación y análisis
    - Apropiados: Comprender, Aplicar, Analizar

    **Nivel 6 (Integración):**
    - Integración y síntesis equilibrada
    - Apropiados: Recordar, Comprender, Aplicar

    **Nivel 8 (Dominio):**
    - Dominio profesional y pensamiento crítico avanzado
    - Apropiados: Aplicar, Analizar, Evaluar, Crear
    """)

# Configuración Avanzada (Autenticidad)
st.sidebar.expander("Configuración Avanzada (Autenticidad)").markdown(
    """
    *Actualmente, la autenticidad del contexto profesional se estima usando una lista
    predeterminada de palabras clave.*
    """
)
current_professional_keywords = PROFESSIONAL_KEYWORDS

st.sidebar.divider() # Separador visual

st.sidebar.header("Entrada de RdAs")
input_method = st.sidebar.radio(
    "Seleccione método de entrada:",
    ("Pegar Texto", "Subir Archivo")
)

uploaded_file = None
text_input = ""
input_data = [] # Almacenará tuplas (texto_ra, nivel_academico_ra)

# --- Procesamiento de la Entrada ---
# (Sin cambios significativos aquí, solo asegurar que las keys de selectbox sean únicas si se usan)
if input_method == "Pegar Texto":
    text_input = st.sidebar.text_area("Pegue uno o más RAs (uno por línea):", height=150)
    if text_input:
        raw_objectives = [line.strip() for line in text_input.split('\n') if line.strip()]
        input_data = [(text, global_academic_level) for text in raw_objectives]
        st.sidebar.info(f"{len(input_data)} RAs pegados. Se analizarán contra el Nivel Académico Global: {global_academic_level}")

else: # Método "Subir Archivo"
    uploaded_file = st.sidebar.file_uploader(
        "Seleccione un archivo (.txt, .csv, .xlsx):",
        type=["txt", "csv", "xlsx"]
    )
    if uploaded_file is not None:
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            if file_extension == ".txt":
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                raw_objectives = [line.strip() for line in stringio.readlines() if line.strip()]
                input_data = [(text, global_academic_level) for text in raw_objectives]
                st.sidebar.warning(f"Archivo .txt leído ({len(input_data)} RdAs). Se analizarán contra el Nivel Académico Global: {global_academic_level}")

            elif file_extension in [".csv", ".xlsx"]:
                if file_extension == ".csv":
                    df_upload = pd.read_csv(uploaded_file)
                else: # .xlsx
                    df_upload = pd.read_excel(uploaded_file)

                st.sidebar.success(f"Archivo {file_extension} '{uploaded_file.name}' leído.")
                st.sidebar.markdown("**Por favor, seleccione las columnas:**")

                available_columns = [""] + df_upload.columns.tolist()

                # Usar keys únicas para evitar problemas de estado
                col_ra_text = st.sidebar.selectbox(
                    "Columna con el texto del RA:", available_columns, index=0, key="sel_ra_col"
                )
                col_academic_level = st.sidebar.selectbox(
                    "Columna con el Nivel Académico (ej: 2, 4, 6 o 8):", available_columns, index=0, key="sel_level_col"
                )

                if col_ra_text and col_academic_level and col_ra_text != col_academic_level:
                    if col_ra_text in df_upload.columns and col_academic_level in df_upload.columns:
                        df_filtered = df_upload[[col_ra_text, col_academic_level]].dropna(subset=[col_ra_text, col_academic_level])
                        df_filtered[col_ra_text] = df_filtered[col_ra_text].astype(str)
                        df_filtered[col_academic_level] = df_filtered[col_academic_level].astype(str).str.replace(r'\.0$', '', regex=True)

                        input_data = list(df_filtered[[col_ra_text, col_academic_level]].itertuples(index=False, name=None))
                        st.sidebar.info(f"{len(input_data)} RdAs leídos del archivo con niveles individuales.")
                    else:
                        st.sidebar.error("Una o ambas columnas seleccionadas no existen en el archivo.")
                        input_data = []
                elif col_ra_text or col_academic_level:
                     if col_ra_text and col_academic_level and col_ra_text == col_academic_level:
                         st.sidebar.warning("Por favor, seleccione columnas diferentes para el RdA y el Nivel Académico.")
                     else:
                         st.sidebar.warning("Por favor, seleccione ambas columnas (RA y Nivel Académico).")
                     input_data = []
                else:
                    pass # No hacer nada si no se han seleccionado columnas aún

            else:
                 st.sidebar.error(f"Tipo de archivo '{file_extension}' no soportado.")
                 input_data = []

        except Exception as e:
            st.sidebar.error(f"Error al procesar el archivo: {e}")
            input_data = []

# Botón para iniciar análisis en la barra lateral
analyze_button = st.sidebar.button("Analizar RAs", type="primary")

# --- Área Principal de Resultados ---
st.header("Resultados del Análisis")

# Definir results_df fuera del bloque 'if analyze_button' para que esté disponible para descarga
results_df = pd.DataFrame()

if analyze_button:
    if not input_data:
        st.warning("Por favor, ingrese o suba RdAs válidos y seleccione las columnas necesarias (si aplica) para analizar.")
    else:
        st.info(f"Analizando {len(input_data)} RdAs...")
        results_list = []
        progress_bar = st.progress(0)
        total_items = len(input_data)

        with st.spinner('Procesando...'):
            for i, data_item in enumerate(input_data):
                objective_text, ra_academic_level = data_item

                if not objective_text or not isinstance(objective_text, str):
                    logging.warning(f"Saltando entrada inválida en índice {i}: {objective_text}")
                    continue

                # 1. Analizar Nivel de Bloom (Proceso Cognitivo)
                bloom_result = analyze_bloom_level(objective_text)
                original_level = bloom_result.get('level', 'Error')
                verb = bloom_result.get('verb', 'N/A')
                error_bloom = bloom_result.get('error')
                level_number = LEVEL_TO_NUMBER.get(original_level.lower(), '')
                formatted_level = f"{original_level} ({level_number})" if level_number else original_level

                # 2. Evaluar Adecuación vs Nivel Académico
                appropriateness = check_appropriateness(original_level, str(ra_academic_level))

                # 3. Evaluar Verificabilidad
                verificability_result = check_verificability(objective_text, nlp_model)
                obs_score = verificability_result.get('observable_score', 0)
                mea_score = verificability_result.get('measurable_score', 0)
                eva_score = verificability_result.get('evaluability_score', 0)
                # verif_justification = verificability_result.get('justification', '')

                # 4. Evaluar Corrección
                correction_result = check_correction(objective_text, nlp_model)
                corr_score = correction_result.get('correction_score', 0)
                corr_notes = correction_result.get('correction_notes', '')

                # 5. Evaluar Autenticidad
                authenticity_result = check_authenticity(objective_text, nlp_model, current_professional_keywords)
                auth_action_score = authenticity_result.get('action_score', 1)
                auth_context_score = authenticity_result.get('context_score', 1)
                auth_meaning_score = authenticity_result.get('meaning_score', 1)
                auth_notes = authenticity_result.get('authenticity_notes', '')

                # 6. Evaluar Dimensión del Conocimiento <<< AÑADIDO >>>
                knowledge_result = check_knowledge_dimension(objective_text, nlp_model)
                k_fact_score = knowledge_result.get('factual_score', 1)
                k_conc_score = knowledge_result.get('conceptual_score', 1)
                k_proc_score = knowledge_result.get('procedural_score', 1)
                k_meta_score = knowledge_result.get('metacognitive_score', 1)
                k_notes = knowledge_result.get('knowledge_notes', '')


                # Construir diccionario de resultados <<< MODIFICADO >>>
                results_list.append({
                    "RA": objective_text,
                    "Nivel Académico Origen": ra_academic_level,
                    "Verbo Principal": verb,
                    "Nivel Bloom Original": original_level,
                    "Nivel Bloom Detectado": formatted_level,
                    "Clasificación vs Nivel Origen": appropriateness,
                    "Puntaje Observable": obs_score,
                    "Puntaje Medible": mea_score,
                    "Puntaje Evaluable": eva_score,
                    "Puntaje Corrección": corr_score,
                    "Autenticidad Acción": auth_action_score,
                    "Autenticidad Contexto": auth_context_score,
                    "Autenticidad Sentido": auth_meaning_score,
                    "Conocimiento Factual": k_fact_score,      # <<< AÑADIDO >>>
                    "Conocimiento Conceptual": k_conc_score,   # <<< AÑADIDO >>>
                    "Conocimiento Procedimental": k_proc_score,# <<< AÑADIDO >>>
                    "Conocimiento Metacognitivo": k_meta_score,# <<< AÑADIDO >>>
                    "Notas Corrección": corr_notes,
                    "Notas Autenticidad": auth_notes,
                    "Notas Conocimiento": k_notes,             # <<< AÑADIDO >>>
                    "Error Bloom": error_bloom
                })

                # Actualizar barra de progreso
                progress_bar.progress((i + 1) / total_items)

        if results_list:
            results_df = pd.DataFrame(results_list)

            # --- Mostrar Tabla de Resultados Detallados ---
            st.subheader("Análisis Detallado por RdA")
            # <<< MODIFICADO >>> Añadir nuevas columnas de Conocimiento
            display_columns = {
                "RdA": "Resultado de Aprendizaje",
                "Nivel Académico Origen": "Nivel Origen",
                "Verbo Principal": "Verbo",
                "Nivel Bloom Detectado": "Nivel Bloom (Proceso)", # Aclarar que es Proceso
                "Clasificación vs Nivel Origen": "Adecuación T.",
                "Puntaje Observable": "Obs.",
                "Puntaje Medible": "Med.",
                "Puntaje Evaluable": "Eval.",
                "Puntaje Corrección": "Corr.",
                "Autenticidad Acción": "Aut. Acción",
                "Autenticidad Contexto": "Aut. Contexto",
                "Autenticidad Sentido": "Aut. Sentido",
                "Conocimiento Factual": "K.Fact",        # <<< AÑADIDO >>>
                "Conocimiento Conceptual": "K.Conc",     # <<< AÑADIDO >>>
                "Conocimiento Procedimental": "K.Proc",  # <<< AÑADIDO >>>
                "Conocimiento Metacognitivo": "K.Meta",  # <<< AÑADIDO >>>
            }
            # Reordenar columnas <<< MODIFICADO >>>
            display_order = [
                "RA",
                "Nivel Académico Origen",
                "Verbo Principal",
                "Nivel Bloom Detectado", # Proceso Cognitivo
                "Conocimiento Factual",        # <<< AÑADIDO >>>
                "Conocimiento Conceptual",     # <<< AÑADIDO >>>
                "Conocimiento Procedimental",  # <<< AÑADIDO >>>
                "Conocimiento Metacognitivo",  # <<< AÑADIDO >>>
                "Clasificación vs Nivel Origen",
                "Puntaje Observable",
                "Puntaje Medible",
                "Puntaje Evaluable",
                "Puntaje Corrección",
                "Autenticidad Acción",
                "Autenticidad Contexto",
                "Autenticidad Sentido",
            ]
            existing_display_order = [col for col in display_order if col in results_df.columns]
            st.dataframe(
                results_df[existing_display_order].rename(columns=display_columns),
                use_container_width=True,
                column_config={ # <<< MODIFICADO >>> Añadir ayuda para las nuevas columnas
                     "Corr.": st.column_config.NumberColumn(help="Corrección (0-3): Claridad y completitud."),
                     "Aut. Acción": st.column_config.NumberColumn(format="%d ⭐", help="Autenticidad - Acción (1-5)"),
                     "Aut. Contexto": st.column_config.NumberColumn(format="%d ⭐", help="Autenticidad - Contexto (1-5)"),
                     "Aut. Sentido": st.column_config.NumberColumn(format="%d ⭐", help="Autenticidad - Sentido (1-5)"),
                     "K.Fact": st.column_config.NumberColumn(format="%d", help="Conocimiento Factual (1=Bajo, 2=Medio, 3=Alto)"),
                     "K.Conc": st.column_config.NumberColumn(format="%d", help="Conocimiento Conceptual (1=Bajo, 2=Medio, 3=Alto)"),
                     "K.Proc": st.column_config.NumberColumn(format="%d", help="Conocimiento Procedimental (1=Bajo, 2=Medio, 3=Alto)"),
                     "K.Meta": st.column_config.NumberColumn(format="%d", help="Conocimiento Metacognitivo (1=Bajo, 2=Medio, 3=Alto)"),
                 }
            )

            # --- Botón de Descarga para Tabla Detallada ---
            if not results_df.empty:
                @st.cache_data
                def convert_df_to_excel_detailed(df):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Descargar las columnas mostradas con nombres amigables
                        # <<< MODIFICADO >>> Asegurarse que existing_display_order y display_columns están actualizados
                        df_to_download = df[existing_display_order].rename(columns=display_columns)
                        # O descargar todas las columnas originales si se prefiere:
                        # df_to_download = df # Incluiría notas y errores
                        df_to_download.to_excel(writer, index=False, sheet_name='Analisis_Detallado')
                    processed_data = output.getvalue()
                    return processed_data

                excel_bytes_detailed = convert_df_to_excel_detailed(results_df)

                st.download_button(
                    label="📥 Descargar Análisis Detallado (.xlsx)",
                    data=excel_bytes_detailed,
                    file_name='analisis_detallado_ras.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='dl_detailed' # Key única
                )

            # --- Descarga Consolidada ---
            # <<< AÑADIDO >>> Sección de descarga de PDFs con estado persistente
            st.markdown("---")

            # === INFORMACIÓN SOBRE LOS REPORTES ===
            with st.expander("ℹ️ Información sobre los Reportes PDF"):
                st.markdown("""
                ### 📊 **PDF Ejecutivo** (Vertical)
                - **Columnas**: RdA, Nivel Bloom, Observable, Medible, Evaluable, Corrección
                - **Uso**: Resumen gerencial rápido y presentaciones ejecutivas
                - **Formato**: A4 vertical, tabla compacta

                ### 📋 **PDF Completo** (Horizontal)
                - **Columnas**: 15 columnas completas con toda la información
                - **Incluye**: Verbo, Adecuación, Autenticidad, Conocimiento, etc.
                - **Formato**: A4 horizontal para máximo aprovechamiento del espacio
                - **Uso**: Análisis detallado y documentación completa

                ### 📈 **PDF Solo Gráficos** (Horizontal)
                - **Contenido**: 5 páginas con SOLO visualizaciones (sin tablas)
                - **Gráficos**: Distribuciones, Verificabilidad, Autenticidad, Conocimiento, Comparación
                - **Formato**: A4 horizontal, gráficos de alta calidad
                - **Uso**: Presentaciones visuales y análisis estadístico

                ### 🎯 **PDFs por Nivel**
                - **Contenido**: Tabla completa filtrada por nivel académico específico
                - **Formato**: A4 horizontal con 15 columnas
                - **Uso**: Análisis específico por nivel de formación
                """)

            st.subheader("📥 Descarga de Reportes PDF")

            # Usar session_state para mantener el estado de los PDFs generados
            if 'pdf_cache' not in st.session_state:
                st.session_state.pdf_cache = {}

            # Generar cache key único basado en los datos
            cache_key = f"pdfs_{len(results_df)}_{hash(str(results_df.to_dict()))}"

            # Solo regenerar PDFs si los datos han cambiado
            if cache_key not in st.session_state.pdf_cache:
                with st.spinner("🔄 Preparando reportes PDF..."):
                    try:
                        # Preparar datos comunes
                        bloom_distribution = {}
                        if 'Nivel Bloom Detectado' in results_df.columns:
                            bloom_distribution = results_df['Nivel Bloom Detectado'].value_counts().to_dict()

                        common_stats = {
                            'total_rdas': len(results_df),
                            'bloom_distribution': bloom_distribution,
                            'avg_bloom_score': 0
                        }

                        # Generar PDFs optimizados (sin PDF detallado)
                        st.session_state.pdf_cache[cache_key] = {
                            'executive': generate_executive_pdf(results_df.to_dict('records'), global_academic_level, common_stats),
                            'complete': generate_complete_pdf(results_df.to_dict('records'), global_academic_level, common_stats),
                            'charts': generate_charts_pdf(results_df.to_dict('records'), global_academic_level, common_stats)
                        }

                        # Generar PDFs por nivel
                        for level in ['2', '4', '6', '8']:
                            st.session_state.pdf_cache[cache_key][f'level_{level}'] = generate_level_pdf(
                                results_df.to_dict('records'), level, common_stats
                            )
                    except Exception as e:
                        st.error(f"Error al preparar PDFs: {str(e)}")
                        st.session_state.pdf_cache[cache_key] = {}

            # Mostrar botones de descarga principales (sin regenerar PDFs)
            if cache_key in st.session_state.pdf_cache and st.session_state.pdf_cache[cache_key]:

                # === REPORTES PRINCIPALES ===
                st.markdown("**📊 Reportes Principales:**")
                col_pdf1, col_pdf2, col_pdf3 = st.columns(3)

                with col_pdf1:
                    st.download_button(
                        label="📊 PDF Ejecutivo",
                        data=st.session_state.pdf_cache[cache_key].get('executive', b''),
                        file_name=f"Andru_Ejecutivo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        help="📋 Resumen gerencial con 6 columnas esenciales (vertical)",
                        key="dl_pdf_executive_cached"
                    )

                with col_pdf2:
                    st.download_button(
                        label="📋 PDF Completo",
                        data=st.session_state.pdf_cache[cache_key].get('complete', b''),
                        file_name=f"Andru_Completo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        help="📊 Análisis integral con 15 columnas completas (horizontal)",
                        key="dl_pdf_complete_cached"
                    )

                with col_pdf3:
                    st.download_button(
                        label="📈 PDF Solo Gráficos",
                        data=st.session_state.pdf_cache[cache_key].get('charts', b''),
                        file_name=f"Andru_Graficos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        help="📈 5 páginas con SOLO gráficos y análisis visual (sin tablas)",
                        key="dl_pdf_charts_cached"
                    )

                st.markdown("---")

            # --- Fin Descarga Consolidada Mejorada ---
            st.subheader("Resumen General")

            # --- Botón de Descarga para Resumen General Consolidado ---
            if not results_df.empty:
                @st.cache_data
                def convert_summaries_to_excel(df_results):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Hoja 1: Frecuencia Nivel Bloom (Proceso)
                        level_counts = df_results['Nivel Bloom Original'].value_counts().sort_index()
                        formatted_labels = [f"{lvl} ({LEVEL_TO_NUMBER.get(lvl.lower(), '')})" if LEVEL_TO_NUMBER.get(lvl.lower()) else lvl for lvl in level_counts.index]
                        freq_df_bloom = pd.DataFrame({'Nivel_Proceso': formatted_labels, 'Frecuencia': level_counts.values})
                        if not freq_df_bloom.empty: freq_df_bloom.to_excel(writer, index=False, sheet_name='Frecuencia_Bloom_Proceso')

                        # <<< AÑADIDO >>> Hoja 2: Promedios Dimensión Conocimiento
                        avg_scores_know = df_results[[
                            "Conocimiento Factual", "Conocimiento Conceptual",
                            "Conocimiento Procedimental", "Conocimiento Metacognitivo"
                        ]].mean().round(2).reset_index()
                        avg_scores_know.columns = ['Dimensión Conocimiento', 'Promedio (1-3)']
                        avg_scores_know['Dimensión Conocimiento'] = avg_scores_know['Dimensión Conocimiento'].replace({
                            "Conocimiento Factual": "Factual", "Conocimiento Conceptual": "Conceptual",
                            "Conocimiento Procedimental": "Procedimental", "Conocimiento Metacognitivo": "Metacognitivo"
                        })
                        if not avg_scores_know.empty: avg_scores_know.to_excel(writer, index=False, sheet_name='Promedios_Conocimiento')

                        # Hoja 3: Frecuencia Adecuación
                        adequacy_counts = df_results['Clasificación vs Nivel Origen'].value_counts().reset_index()
                        adequacy_counts.columns = ['Clasificación', 'Frecuencia']
                        if not adequacy_counts.empty: adequacy_counts.to_excel(writer, index=False, sheet_name='Frecuencia_Adecuacion')

                        # Hoja 4: Promedios Verificabilidad
                        avg_scores_verif = df_results[["Puntaje Observable", "Puntaje Medible", "Puntaje Evaluable"]].mean().round(2).reset_index()
                        avg_scores_verif.columns = ['Métrica', 'Promedio']
                        avg_scores_verif['Métrica'] = avg_scores_verif['Métrica'].replace({"Puntaje Observable": "Observable", "Puntaje Medible": "Medible", "Puntaje Evaluable": "Evaluable"})
                        if not avg_scores_verif.empty: avg_scores_verif.to_excel(writer, index=False, sheet_name='Promedios_Verificabilidad')

                        # Hoja 5 y 6: Corrección
                        avg_corr_val = df_results["Puntaje Corrección"].mean().round(2)
                        corr_freq = df_results["Puntaje Corrección"].value_counts().sort_index().reset_index()
                        corr_freq.columns = ['Puntaje', 'Frecuencia']
                        avg_corr_df = pd.DataFrame({'Métrica': ['Promedio Corrección (0-3)'], 'Valor': [f"{avg_corr_val:.2f}"]})
                        if not avg_corr_df.empty: avg_corr_df.to_excel(writer, index=False, sheet_name='Promedio_Correccion')
                        if not corr_freq.empty: corr_freq.to_excel(writer, index=False, sheet_name='Frecuencia_Correccion')

                        # Hoja 7: Promedios Autenticidad
                        avg_scores_auth = df_results[["Autenticidad Acción", "Autenticidad Contexto", "Autenticidad Sentido"]].mean().round(2).reset_index()
                        avg_scores_auth.columns = ['Métrica', 'Promedio']
                        avg_scores_auth['Métrica'] = avg_scores_auth['Métrica'].replace({"Autenticidad Acción": "Acción", "Autenticidad Contexto": "Contexto", "Autenticidad Sentido": "Sentido"})
                        if not avg_scores_auth.empty: avg_scores_auth.to_excel(writer, index=False, sheet_name='Promedios_Autenticidad')

                    processed_data = output.getvalue()
                    return processed_data

                excel_bytes_summary = convert_summaries_to_excel(results_df)
                st.download_button(
                    label="📥 Descargar Resumen General (.xlsx)",
                    data=excel_bytes_summary,
                    file_name='resumen_general_ras.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key='download_summary'
                )

                # --- Botones PDF para Resumen General ---
                st.markdown("#### 🤖 **Exportación PDF - Resumen General**")

                col_summary_pdf1, col_summary_pdf2 = st.columns(2)

                with col_summary_pdf1:
                    try:
                        # Corregir: usar directamente st.download_button sin st.button
                        bloom_distribution = {}
                        if 'Nivel Bloom Detectado' in results_df.columns:
                            bloom_distribution = results_df['Nivel Bloom Detectado'].value_counts().to_dict()

                        pdf_data = generate_executive_pdf(results_df.to_dict('records'), global_academic_level, {
                            'total_rdas': len(results_df),
                            'bloom_distribution': bloom_distribution,
                            'avg_bloom_score': 0
                        })
                        st.download_button(
                            label="📊 PDF Resumen Ejecutivo",
                            data=pdf_data,
                            file_name=f"Andru_Resumen_Ejecutivo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            help="Resumen general con métricas agregadas",
                            key="dl_summary_pdf_executive"
                        )
                    except Exception as e:
                        st.error(f"Error al generar PDF resumen ejecutivo: {str(e)}")

                with col_summary_pdf2:
                    try:
                        # Corregir: usar directamente st.download_button sin st.button
                        bloom_distribution = {}
                        if 'Nivel Bloom Detectado' in results_df.columns:
                            bloom_distribution = results_df['Nivel Bloom Detectado'].value_counts().to_dict()

                        # CORREGIDO: Usar generate_charts_pdf en lugar de generate_complete_pdf
                        pdf_data = generate_charts_pdf(results_df.to_dict('records'), global_academic_level, {
                            'total_rdas': len(results_df),
                            'bloom_distribution': bloom_distribution,
                            'avg_bloom_score': 0
                        })
                        st.download_button(
                            label="📈 PDF con Gráficos",
                            data=pdf_data,
                            file_name=f"Andru_PDF_Graficos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            help="Reporte con gráficos, visualizaciones y análisis estadístico",
                            key="dl_summary_pdf_charts"
                        )
                    except Exception as e:
                        st.error(f"Error al generar PDF con gráficos: {str(e)}")
            # --- Fin Descarga Consolidada ---


            # --- Mostrar Resúmenes en Columnas ---
            # <<< MODIFICADO >>> Usar 6 columnas para incluir Conocimiento
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1: # Frecuencia Bloom (Proceso)
                st.markdown("##### Frecuencia Bloom (Proceso)")
                if not results_df.empty:
                    level_counts = results_df['Nivel Bloom Original'].value_counts().sort_index()
                    formatted_labels = [f"{lvl} ({LEVEL_TO_NUMBER.get(lvl.lower(), '')})" if LEVEL_TO_NUMBER.get(lvl.lower()) else lvl for lvl in level_counts.index]
                    freq_df_bloom = pd.DataFrame({'Nivel': formatted_labels, 'Frecuencia': level_counts.values})
                    st.dataframe(freq_df_bloom, use_container_width=True, height=250, hide_index=True)

            # <<< AÑADIDO >>> Columna para Promedios Conocimiento
            with col2:
                st.markdown("##### Promedios Conocimiento")
                if not results_df.empty:
                    avg_scores_know = results_df[[
                        "Conocimiento Factual", "Conocimiento Conceptual",
                        "Conocimiento Procedimental", "Conocimiento Metacognitivo"
                    ]].mean().round(2).reset_index()
                    avg_scores_know.columns = ['Dimensión', 'Promedio (1-3)']
                    avg_scores_know['Dimensión'] = avg_scores_know['Dimensión'].replace({
                        "Conocimiento Factual": "Factual", "Conocimiento Conceptual": "Conceptual",
                        "Conocimiento Procedimental": "Procedimental", "Conocimiento Metacognitivo": "Metacognitivo"
                    })
                    st.dataframe(avg_scores_know, use_container_width=True, height=250, hide_index=True)

            with col3: # Frecuencia Adecuación
                st.markdown("##### Frecuencia Adecuación T.")
                if not results_df.empty:
                    adequacy_counts = results_df['Clasificación vs Nivel Origen'].value_counts().reset_index()
                    adequacy_counts.columns = ['Clasificación', 'Frecuencia']
                    st.dataframe(adequacy_counts, use_container_width=True, height=250, hide_index=True)

            with col4: # Promedios Verificabilidad
                st.markdown("##### Promedios Verificabilidad")
                if not results_df.empty:
                    avg_scores_verif = results_df[["Puntaje Observable", "Puntaje Medible", "Puntaje Evaluable"]].mean().round(2).reset_index()
                    avg_scores_verif.columns = ['Métrica', 'Promedio']
                    avg_scores_verif['Métrica'] = avg_scores_verif['Métrica'].replace({"Puntaje Observable": "Observable", "Puntaje Medible": "Medible", "Puntaje Evaluable": "Evaluable"})
                    st.dataframe(avg_scores_verif, use_container_width=True, height=250, hide_index=True)

            with col5: # Corrección
                st.markdown("##### Corrección")
                if not results_df.empty:
                    avg_corr = results_df["Puntaje Corrección"].mean().round(2)
                    corr_freq = results_df["Puntaje Corrección"].value_counts().sort_index().reset_index()
                    corr_freq.columns = ['Puntaje', 'Frecuencia']
                    st.metric(label="Promedio Corrección (0-3)", value=f"{avg_corr:.2f}")
                    st.markdown("Frecuencia Puntajes:")
                    st.dataframe(corr_freq, use_container_width=True, hide_index=True)

            with col6: # Autenticidad
                st.markdown("##### Promedios Autenticidad")
                if not results_df.empty:
                    avg_scores_auth = results_df[["Autenticidad Acción", "Autenticidad Contexto", "Autenticidad Sentido"]].mean().round(2).reset_index()
                    avg_scores_auth.columns = ['Métrica', 'Promedio']
                    avg_scores_auth['Métrica'] = avg_scores_auth['Métrica'].replace({"Autenticidad Acción": "Acción", "Autenticidad Contexto": "Contexto", "Autenticidad Sentido": "Sentido"})
                    st.dataframe(avg_scores_auth, use_container_width=True, height=250, hide_index=True)


            # --- Mostrar RAs que Requieren Atención ---
            st.divider()
            st.subheader("RdAs que Requieren Atención")
            # <<< MODIFICADO >>> Añadir pestaña opcional para Conocimiento si se desea, o mantener 4
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Errores Bloom", "Baja Verificabilidad", "Baja Corrección", "Baja Autenticidad", "Bajo Conocimiento (?)"])
            # Si se quiere una pestaña para Conocimiento:
            # tab1, tab2, tab3, tab4, tab5 = st.tabs(["Errores Bloom", "Baja Verificabilidad", "Baja Corrección", "Baja Autenticidad", "Bajo Conocimiento (?)"])

            with tab1: # Errores Bloom
                if not results_df.empty:
                    errors_df = results_df[
                        results_df['Nivel Bloom Original'].isin(['Error', 'No clasificado', 'No identificado', 'N/A']) |
                        results_df['Error Bloom'].notna()
                    ][['RA', 'Nivel Académico Origen', 'Verbo Principal', 'Nivel Bloom Original', 'Error Bloom']].rename(columns={'Nivel Bloom Original': 'Estado'})
                    if not errors_df.empty:
                        st.warning("No se pudo clasificar nivel Bloom (Proceso):")
                        st.dataframe(errors_df, use_container_width=True, hide_index=True)
                    else: st.info("No se encontraron RAs con errores de clasificación Bloom.")

            with tab2: # Baja Verificabilidad
                if not results_df.empty:
                    low_verif_threshold = 2
                    low_verif_df = results_df[
                        (results_df['Puntaje Observable'] <= low_verif_threshold) |
                        (results_df['Puntaje Medible'] <= low_verif_threshold)
                    ][['RA', 'Puntaje Observable', 'Puntaje Medible', 'Puntaje Evaluable']].rename(columns={
                         "Puntaje Observable": "Obs.", "Puntaje Medible": "Med.", "Puntaje Evaluable": "Eval."
                    })
                    if not low_verif_df.empty:
                         st.warning(f"Puntajes bajos (≤{low_verif_threshold}) en Observabilidad o Medibilidad:")
                         st.dataframe(low_verif_df, use_container_width=True, hide_index=True)
                    else: st.info(f"No se encontraron RAs con baja verificabilidad (Obs/Med ≤ {low_verif_threshold}).")

            with tab3: # Baja Corrección
                if not results_df.empty:
                    low_corr_threshold = 1
                    low_corr_df = results_df[
                        results_df['Puntaje Corrección'] <= low_corr_threshold
                    ][['RA', 'Puntaje Corrección', 'Notas Corrección']].rename(columns={
                         "Puntaje Corrección": "Corr.", "Notas Corrección": "Justificación"
                    })
                    if not low_corr_df.empty:
                         st.warning(f"Requieren revisión por posibles problemas de formulación (Puntaje ≤ {low_corr_threshold}):")
                         st.dataframe(low_corr_df, use_container_width=True, hide_index=True)
                    else: st.info(f"No se encontraron RAs con baja corrección (≤ {low_corr_threshold}).")

            with tab4: # Baja Autenticidad
                if not results_df.empty:
                    low_auth_threshold = 2
                    low_auth_df = results_df[
                        (results_df['Autenticidad Acción'] <= low_auth_threshold) |
                        (results_df['Autenticidad Contexto'] <= low_auth_threshold)
                    ][['RA', 'Autenticidad Acción', 'Autenticidad Contexto', 'Autenticidad Sentido', 'Notas Autenticidad']].rename(columns={
                         "Autenticidad Acción": "Acción", "Autenticidad Contexto": "Contexto",
                         "Autenticidad Sentido": "Sentido", "Notas Autenticidad": "Justificación (Estimada)"
                    })
                    if not low_auth_df.empty:
                         st.warning(f"Posible baja autenticidad (Acción o Contexto ≤ {low_auth_threshold}):")
                         st.dataframe(low_auth_df, use_container_width=True, hide_index=True)
                    else: st.info(f"No se encontraron RAs con baja autenticidad estimada (Acción/Contexto ≤ {low_auth_threshold}).")

            # Opcional: Añadir pestaña para bajo conocimiento si se desea
            with tab5:
                st.markdown("##### RdAs con Bajo Nivel en Dimensiones Clave del Conocimiento")
                if not results_df.empty:
                    low_know_threshold = 1 # Mostrar RAs con puntaje 1 (Bajo)
                    # Definir qué dimensiones son 'clave' para marcar un RA
                    low_know_df = results_df[
                        (results_df['Conocimiento Conceptual'] <= low_know_threshold) | # Ejemplo: Marcar si Conceptual o Procedimental es bajo
                        (results_df['Conocimiento Procedimental'] <= low_know_threshold)
                    ][['RA', 'Conocimiento Factual', 'Conocimiento Conceptual', 'Conocimiento Procedimental', 'Conocimiento Metacognitivo', 'Notas Conocimiento']].rename(columns={
                         'Conocimiento Factual': 'K.Fact', 'Conocimiento Conceptual': 'K.Conc',
                         'Conocimiento Procedimental': 'K.Proc', 'Conocimiento Metacognitivo': 'K.Meta',
                         'Notas Conocimiento': 'Justificación (Estimada)'
                    })
                    if not low_know_df.empty:
                         st.warning(f"Posible bajo nivel de conocimiento Conceptual o Procedimental (Puntaje = {low_know_threshold}):")
                         st.dataframe(low_know_df, use_container_width=True, hide_index=True)
                    else:
                         st.info(f"No se encontraron RAs con bajo nivel estimado en Conocimiento Conceptual o Procedimental.")


        else:
            if analyze_button:
                st.info("No se generaron resultados para los RdAs proporcionados.")

# --- Fin del Script ---

# Para ejecutar: streamlit run src/app.py

# --- Sección de Información Adicional ---
st.markdown("##### Desarrollado por Ruben Tocain G.")
st.caption("## Como parte del Proyecto de Investigación RdA's- v0.1 y Caso Práctico de Titulación")
st.sidebar.info("Herramienta desarrollada para asistir en el análisis curricular.")
# st.caption("Versión 1.2.0 - Integración Incremental y Selección de Columna")