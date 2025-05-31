import spacy
import logging
from typing import List, Dict, Optional

# Configurar logger
logger = logging.getLogger(__name__)

# --- Palabras Clave de Contexto Profesional (EJEMPLO - ¡NECESITA SER PERSONALIZADO!) ---
# Estas listas deben ser adaptadas al dominio específico del programa académico.
# Podrían cargarse desde un archivo de configuración en el futuro.
PROFESSIONAL_KEYWORDS: Dict[str, List[str]] = {
    #"negocios_general": ["empresa", "organizacional", "mercado", "cliente", "estrategia", "proyecto", "gestión", "proceso", "calidad", "riesgo"],
    #"finanzas": ["financiero", "presupuesto", "inversión", "costo", "rentabilidad", "contable", "auditoría", "flujo de caja"],
    #"marketing": ["marketing", "venta", "publicidad", "marca", "consumidor", "producto", "precio", "distribución"],
    # ----- ASIGNATURAS DE 6TO NIVEL -----
    "administracion_talento_humano": [
        "reclutamiento", "selección", "compensación", "capacitación", "desempeño", 
        "competencias", "clima_laboral", "retención", "rotación", "desarrollo_organizacional", 
        "outplacement", "coaching", "cultura_organizacional", "bienestar", "onboarding",
        "evaluación_360", "perfil_competencial", "KPI_recursos_humanos", "engagement", "plan_carrera",
        "headhunting", "job_description", "assessment_center", "employer_branding", "contrato_laboral",
        "feedback_constructivo", "gestión_talento", "mentoring", "plan_sucesión", "conciliación_laboral",
        "análisis_puesto", "employee_experience", "remuneración_variable", "incentivo_laboral", "entrevista_conductual",
        "plan_formación", "clima_organizacional", "relaciones_laborales", "gestión_conflicto", "nómina",
        "diagnóstico_necesidades", "evaluación_desempeño", "atracción_talento", "liderazgo_situacional", "prueba_psicométrica",
        "auditoría_RRHH", "outplacement", "benchmarking_salarial", "core_competencies", "retribución_flexible"
    ],
    
    "auditoria_comercio_internacional": [
        "arancel", "incoterms", "certificación", "aduana", "exportación", 
        "importación", "fiscalización", "despacho", "tratado", "drawback", 
        "partida_arancelaria", "operador_autorizado", "zona_franca", "dumping", "régimen_aduanero",
        "valor_en_aduana", "derecho_compensatorio", "valoración_aduanera", "clasificación_arancelaria", "certificado_origen",
        "barreras_no_arancelarias", "depósito_aduanero", "carta_crédito", "DUA", "licencia_exportación",
        "tránsito_aduanero", "admisión_temporal", "sistema_armonizado", "salvaguardia", "desgravación_arancelaria",
        "OMA", "OMC", "drawback", "cuota_importación", "depósito_franco",
        "comercio_triangular", "TLC", "operador_económico_autorizado", "declaración_aduanera", "auditoría_post_despacho",
        "acuerdo_preferencial", "sanción_aduanera", "medida_antidumping", "ALADI", "contingente_arancelario",
        "nomenclatura_combinada", "tráfico_internacional", "control_aduanero", "flete_internacional", "BL"
    ],
    
    "auditoria": [
        "dictamen", "materialidad", "muestreo", "evidencia", "control_interno", 
        "papeles_trabajo", "opinión", "hallazgo", "conciliación", "fraude", 
        "riesgo_auditoría", "independencia", "aseguramiento", "salvedad", "informe",
        "NIAS", "NAGA", "prueba_sustantiva", "prueba_control", "carta_gerencia",
        "auditoría_forense", "escepticismo_profesional", "confirmación_externa", "procedimiento_analítico", "juicio_profesional",
        "alcance_auditoría", "muestreo_estadístico", "error_tolerable", "análisis_variaciones", "cifra_significativa",
        "auditoría_interna", "auditoría_externa", "revisión_analítica", "COSO", "evaluación_riesgo",
        "responsabilidad_auditor", "documentación_auditoría", "error_material", "carta_representación", "observación_auditoría",
        "planificación_auditoría", "ética_auditor", "revisión_control", "continuidad_negocio", "conclusión_auditoría",
        "dictamen_limpio", "dictamen_adverso", "abstención_opinión", "evidencia_suficiente", "cumplimiento_normativo"
    ],
    
    "diseno_evaluacion_proyectos": [
        "factibilidad", "viabilidad", "inversión", "flujo_caja", "VAN", 
        "TIR", "rentabilidad", "cronograma", "riesgo", "presupuesto", 
        "retorno", "stakeholders", "sostenibilidad", "escalabilidad", "impacto",
        "estudio_mercado", "estudio_técnico", "estudio_financiero", "CAPM", "payback",
        "WACC", "análisis_sensibilidad", "TMAR", "horizonte_evaluación", "inversión_inicial",
        "análisis_costo_beneficio", "relación_beneficio_costo", "periodo_recuperación", "análisis_escenarios", "capital_trabajo",
        "estructura_financiamiento", "depreciación", "amortización", "valor_residual", "EBITDA",
        "análisis_punto_equilibrio", "tasa_descuento", "PER", "matriz_marco_lógico", "gestión_alcance",
        "planificación_proyecto", "EDT", "diagrama_Gantt", "ruta_crítica", "método_PERT",
        "gestión_adquisiciones", "mitigación_riesgo", "estudio_prefactibilidad", "indicador_monitoreo", "sostenibilidad_proyecto"
    ],
    
    "mercadotecnia_i": [
        "segmentación", "posicionamiento", "target", "mezcla_marketing", "investigación_mercados", 
        "comportamiento_consumidor", "estrategia_comercial", "demanda", "propuesta_valor", "branding", 
        "diferenciación", "canal_distribución", "pricing", "promoción", "customer_journey",
        "FODA_marketing", "ciclo_vida_producto", "buyer_persona", "focus_group", "cuota_mercado",
        "marketing_mix", "ventaja_competitiva", "penetración_mercado", "encuesta_satisfacción", "packaging",
        "publicidad_ATL", "publicidad_BTL", "call_to_action", "conversión", "embudo_ventas", 
        "benchmark_competencia", "marketing_experiencial", "insight_consumidor", "brand_equity", "neuromarketing",
        "merchandising", "etnografía_consumo", "KPI_marketing", "ROI_marketing", "análisis_competencia",
        "matriz_BCG", "matriz_Ansoff", "brand_awareness", "plan_marketing", "early_adopters",
        "top_of_mind", "elasticidad_precio", "distribución_intensiva", "CPA", "análisis_PEST"
    ],
    
    "produccion_i": [
        "productividad", "proceso", "capacidad_instalada", "layout", "cadena_suministro", 
        "inventario", "calidad", "just_in_time", "logística", "manufactura", 
        "optimización", "lead_time", "plan_maestro", "cuello_botella", "estandarización",
        "MRP", "balance_línea", "gestión_operaciones", "tiempo_ciclo", "lote_económico",
        "kanban", "diagrama_flujo_proceso", "lean_manufacturing", "mantenimiento_preventivo", "sistema_pull",
        "diagrama_Pareto", "kaizen", "SMED", "poka_yoke", "análisis_valor",
        "control_estadístico_proceso", "seis_sigma", "producción_ajustada", "eficiencia_global_equipo", "planificación_agregada",
        "stock_seguridad", "sistema_push", "takt_time", "teoría_restricciones", "estudio_tiempo",
        "rotación_inventario", "sistema_MRP_II", "carta_control", "análisis_modo_fallo", "HACCP",
        "estudio_métodos", "5S", "célula_manufactura", "fabricación_flexible", "planificación_capacidad"
    ],
    
    # ----- ASIGNATURAS DE 8VO NIVEL -----
    "electiva_ii": [
        "especialización", "tendencia", "innovación", "aplicación", "sector", 
        "metodología_avanzada", "caso_estudio", "benchmark", "disciplina_emergente", "práctica_profesional", 
        "implementación", "tecnología_disruptiva", "adaptación", "interdisciplinariedad", "solución_empresarial",
        "pensamiento_crítico", "transformación_digital", "sistema_inteligente", "análisis_avanzado", "prospección_mercado",
        "reingeniería", "emprendimiento_corporativo", "diseño_organizacional", "estrategia_competitiva", "diversificación_empresarial",
        "responsabilidad_corporativa", "blockchain_aplicado", "ecosistema_negocios", "análisis_disruptivo", "big_data_empresarial",
        "cliente_digital", "simbiosis_industrial", "estrategia_océano_azul", "gamificación_empresarial", "inteligencia_artificial_aplicada",
        "prospectiva_estratégica", "modelos_exponenciales", "automatización_procesos", "gestión_conocimiento", "arquitectura_empresarial",
        "IoT_industrial", "economía_circular", "transformación_organizacional", "servitización", "dinámica_sistemas",
        "design_thinking", "analítica_predictiva", "experiencia_omnicanal", "inteligencia_competitiva", "gestión_cambio_complejo"
    ],
    
    "entorno_socioeconomico": [
        "macroeconómico", "inflación", "PIB", "política_fiscal", "política_monetaria", 
        "globalización", "sector_industrial", "demografía", "indicador_económico", "desarrollo_sostenible", 
        "coyuntura", "tendencia_social", "competitividad_país", "balanza_comercial", "empleo",
        "tasa_interés", "devaluación", "revaluación", "déficit_fiscal", "deuda_externa",
        "ciclo_económico", "recesión", "crecimiento_económico", "tratado_comercial", "inversión_extranjera_directa",
        "matriz_productiva", "índice_precios_consumidor", "balanza_pagos", "política_cambiaria", "sistema_tributario",
        "producto_nacional_bruto", "riesgo_país", "estructura_productiva", "nivel_pobreza", "coeficiente_GINI",
        "distribución_ingreso", "cadena_valor_global", "ventaja_competitiva_nacional", "curva_Lorenz", "análisis_sectorial",
        "índice_desarrollo_humano", "geopolítica_comercial", "reservas_internacionales", "mercado_laboral", "análisis_coyuntural",
        "bono_demográfico", "acuerdo_comercial", "índice_competitividad", "elasticidad_ingreso", "migración_económica"
    ],
    
    "finanzas_corporativas": [
        "valoración", "apalancamiento", "estructura_capital", "fusión", "adquisición", 
        "dividendo", "WACC", "capital_trabajo", "accionista", "emisión", 
        "cobertura", "derivado_financiero", "beta", "gestión_riesgo", "liquidez",
        "modelo_CAPM", "teoría_agencia", "EVA", "flujo_libre_caja", "ratio_endeudamiento",
        "costo_deuda", "costo_capital", "ratio_cobertura_intereses", "EBITDA", "teoría_Modigliani_Miller",
        "valoración_descuento_flujos", "ratio_deuda_capital", "política_dividendos", "apalancamiento_operativo", "apalancamiento_financiero",
        "opciones_reales", "rendimiento_exigido", "prima_riesgo", "forward", "swap_tasa_interés",
        "APT", "due_diligence", "goodwill", "underwriting", "LBO",
        "recompra_acciones", "OPA", "reestructuración_financiera", "gobierno_corporativo", "modelo_Gordon",
        "EBIT", "curva_rendimiento", "spread_crediticio", "covenants", "Project_Finance"
    ],
    
    "liderazgo_tecnicas_negociacion": [
        "influencia", "conflicto", "persuasión", "comunicación_asertiva", "empatía", 
        "resolución_problemas", "mediación", "motivación", "delegación", "inteligencia_emocional", 
        "feedback", "trabajo_equipo", "diplomacia", "BATNA", "concesión",
        "liderazgo_transformacional", "liderazgo_situacional", "liderazgo_transaccional", "liderazgo_adaptativo", "teoría_contingencia",
        "competencias_directivas", "negociación_integrativa", "negociación_distributiva", "negociación_basada_principios", "escucha_activa",
        "gestión_objeciones", "comunicación_no_verbal", "lenguaje_corporal", "rapport", "técnica_harvard",
        "anclaje_negociación", "ZOPA", "MAAN", "coalición", "facilitación",
        "teoría_juegos", "negociación_cooperativa", "negociación_competitiva", "toma_decisiones", "pensamiento_estratégico",
        "coaching_ejecutivo", "manejo_resistencias", "análisis_stakeholders", "mapeo_poder", "agenda_oculta",
        "credibilidad_negociador", "punto_compromiso", "escalamiento_conflicto", "psicodinámica_negociación", "técnica_incrementalismo"
    ],
    
    "politica_empresas": [
        "dirección_estratégica", "gobierno_corporativo", "visión", "misión", "planificación_estratégica", 
        "stakeholder", "compliance", "política_corporativa", "gestión_cambio", "responsabilidad_social", 
        "sostenibilidad", "expansión", "diversificación", "control_directivo", "normativa_institucional",
        "alineamiento_estratégico", "cadena_valor", "ventaja_competitiva", "formulación_estratégica", "implementación_estratégica",
        "estrategia_corporativa", "estrategia_negocio", "estrategia_funcional", "análisis_PESTEL", "cinco_fuerzas_Porter",
        "balanced_scorecard", "KPI_estratégico", "arquitectura_organizacional", "cuadro_mando_integral", "mapa_estratégico",
        "teoría_recursos_capacidades", "capacidad_organizacional", "competencia_distintiva", "cultura_organizacional", "análisis_VRIO",
        "política_expansión", "estrategia_crecimiento", "diversificación_relacionada", "diversificación_no_relacionada", "integración_vertical",
        "análisis_competitivo", "liderazgo_costos", "diferenciación", "enfoque", "océano_azul",
        "alianza_estratégica", "joint_venture", "fusión_estratégica", "consejo_administración", "código_buen_gobierno"
    ]
     # Añadir más categorías y palabras clave según sea necesario
}
   

# --- Función Principal ---

def check_authenticity(text: str, nlp_model: spacy.language.Language, professional_keywords: Optional[Dict[str, List[str]]] = None) -> dict:
    """
    Estima la autenticidad de un RA basado en heurísticas.

    Args:
        text: El texto del Resultado de Aprendizaje.
        nlp_model: El modelo de lenguaje spaCy cargado.
        professional_keywords: Diccionario de palabras clave por categoría profesional.
                               Si es None, usa el default (PROFESSIONAL_KEYWORDS).

    Returns:
        Un diccionario con puntajes estimados (1-5) y notas.
    """
    logger.info(f"--- Iniciando check_authenticity para: '{text}' ---")
    if not text or not isinstance(text, str):
        logger.warning("Texto de entrada inválido o vacío.")
        return {
            'action_score': 1, 'context_score': 1, 'meaning_score': 1,
            'authenticity_notes': 'Texto de entrada inválido o vacío.'
        }
    if not nlp_model:
         logger.error("Modelo NLP no disponible para check_authenticity.")
         return {
            'action_score': 1, 'context_score': 1, 'meaning_score': 1,
            'authenticity_notes': 'Modelo NLP no disponible.'
        }

    # Usar keywords por defecto si no se proporcionan
    if professional_keywords is None:
        professional_keywords = PROFESSIONAL_KEYWORDS

    try:
        doc = nlp_model(text.lower())
        notes = []
        lemmas = {token.lemma_ for token in doc}

        # --- 1. Estimación de Orientación a la Acción (1-5) ---
        action_score = 1 # Default: Muy bajo
        main_verb_token = None
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                main_verb_token = token
                break
        if not main_verb_token:
             for token in doc:
                 if token.pos_ == "VERB":
                     main_verb_token = token
                     break

        if main_verb_token:
            verb_lemma = main_verb_token.lemma_
            # Lógica simple: verbos comunes de niveles altos de Bloom = más acción
            if verb_lemma in ["analizar", "evaluar", "crear", "diseñar", "aplicar", "implementar", "desarrollar", "generar", "resolver"]:
                action_score = 4 # Alto
                notes.append(f"Verbo '{verb_lemma}' sugiere acción clara/aplicable.")
            elif verb_lemma in ["identificar", "describir", "explicar", "comparar", "utilizar"]:
                action_score = 3 # Medio
                notes.append(f"Verbo '{verb_lemma}' sugiere acción, podría ser más concreto.")
            elif verb_lemma in ["comprender", "conocer", "recordar", "definir"]:
                 action_score = 2 # Bajo
                 notes.append(f"Verbo '{verb_lemma}' sugiere acción menos directa/observable.")
            else:
                 action_score = 3 # Default para otros verbos
                 notes.append(f"Verbo '{verb_lemma}' encontrado.")

            # Bonus simple por adverbios (ejemplo muy básico)
            if any(child.lemma_ in ["eficazmente", "correctamente", "eficientemente"] for child in main_verb_token.children if child.pos_ == "ADV"):
                 action_score = min(5, action_score + 1)
                 notes.append("Adverbio sugiere mayor nivel de aplicación.")

        else:
            notes.append("No se encontró verbo principal claro, baja orientación a la acción.")
            action_score = 1

        # --- 2. Estimación de Vinculación con Contexto Profesional (1-5) ---
        context_score = 2 # Default: Bajo (asumiendo que algo de contexto académico siempre hay)
        found_keywords = set()
        all_keywords = set(kw for sublist in professional_keywords.values() for kw in sublist)

        matched_kws = lemmas.intersection(all_keywords)
        if matched_kws:
            found_keywords.update(matched_kws)
            context_score = 4 # Alto si encuentra alguna keyword relevante
            notes.append(f"Vinculación con contexto sugerida por keywords: {', '.join(found_keywords)}.")
        else:
            notes.append("No se encontraron keywords específicas de contexto profesional (según lista actual).")
            # Podríamos intentar una lógica más compleja aquí (buscar sustantivos clave, etc.)
            # pero por ahora lo dejamos simple.

        # --- 3. Estimación de Sentido Formativo (Placeholder) ---
        meaning_score = 3 # Default: Medio
        notes.append("Sentido formativo requiere evaluación manual (default=3).")

        # --- Resultado Final ---
        final_notes = " ".join(notes)
        final_result = {
            'action_score': action_score,
            'context_score': context_score,
            'meaning_score': meaning_score,
            'authenticity_notes': final_notes
        }
        logger.info(f"--- Resultado final check_authenticity: {final_result} ---")
        return final_result

    except Exception as e:
        logger.error(f"Error en check_authenticity para texto '{text[:50]}...': {e}", exc_info=True)
        return {
            'action_score': 1, 'context_score': 1, 'meaning_score': 1,
            'authenticity_notes': f'Error durante el análisis: {e}'
        }

# --- Ejemplo de uso (opcional, para pruebas) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        # Cargar modelo spaCy
        nlp = spacy.load("es_core_news_sm")

        # Definir keywords para prueba (sobrescribir el default si es necesario)
        test_keywords = {
             "negocios": ["empresa", "mercado", "cliente", "estrategia", "proyecto", "gestión"],
             "finanzas": ["financiero", "presupuesto", "inversión", "costo"],
             "biologia": ["célula", "gen", "adn", "proteína", "organismo"]
        }


        test_ras = [
            "Analizar el impacto de las decisiones financieras en la sostenibilidad empresarial.", # Esperado: Acción=4, Contexto=4, Significado=3
            "Describir las partes de la célula.", # Esperado: Acción=3, Contexto=4(bio), Significado=3
            "Conocer los hechos históricos.", # Esperado: Acción=2, Contexto=2, Significado=3
            "Implementar eficazmente una estrategia de marketing.", # Esperado: Acción=5, Contexto=4(mkt), Significado=3
            "Ser bueno.", # Esperado: Acción=1, Contexto=2, Significado=3
            "Aplicar técnicas de gestión de proyectos.", # Esperado: Acción=4, Contexto=4(neg), Significado=3
        ]

        for ra in test_ras:
            # Pasar las keywords de prueba a la función
            result = check_authenticity(ra, nlp, professional_keywords=test_keywords)
            print(f"RA: {ra}")
            print(f"Resultado: {result}\n")

    except OSError:
        print("Error: Modelo spaCy 'es_core_news_sm' no encontrado.")
        print("Por favor, instálalo ejecutando: python -m spacy download es_core_news_sm")
    except Exception as e:
        print(f"Ocurrió un error: {e}")